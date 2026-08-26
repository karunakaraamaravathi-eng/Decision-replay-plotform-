from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import User, AuditLog, Team
from app.schemas import UserResponse, UserUpdateRole, AuditLogResponse, SystemStats
from app.auth import get_current_user, require_roles
from app.config import settings

router = APIRouter(prefix="/users", tags=["User Management"])

@router.get("", response_model=List[UserResponse])
def list_users(
    role: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Administrator", "Manager", "Reviewer"]))
):
    """List all users with optional role and search filter."""
    query = db.query(User)
    
    if role:
        query = query.filter(User.role == role)
    if search:
        query = query.filter(
            (User.full_name.ilike(f"%{search}%")) | (User.email.ilike(f"%{search}%"))
        )

    return query.order_by(User.id.asc()).all()

@router.get("/roles", response_model=List[str])
def get_roles():
    """Return available system roles."""
    return settings.VALID_ROLES

@router.put("/{user_id}/role", response_model=UserResponse)
def update_user_role(
    user_id: int,
    role_update: UserUpdateRole,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Administrator"]))
):
    """Update a user's role (Administrator only)."""
    if role_update.role not in settings.VALID_ROLES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {settings.VALID_ROLES}"
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )

    old_role = user.role
    user.role = role_update.role
    db.commit()
    db.refresh(user)

    # Audit log
    audit = AuditLog(
        user_id=current_user.id,
        action="ROLE_UPDATE",
        entity_type="User",
        entity_id=user.id,
        details=f"Updated user '{user.email}' role from {old_role} to {user.role}"
    )
    db.add(audit)
    db.commit()

    return user

@router.get("/system-stats", response_model=SystemStats)
def get_system_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Administrator", "Manager"]))
):
    """Return system overview statistics."""
    total_users = db.query(User).count()
    roles = db.query(User.role).all()
    roles_breakdown = {}
    for r in settings.VALID_ROLES:
        roles_breakdown[r] = sum(1 for (user_role,) in roles if user_role == r)

    total_teams = db.query(Team).count()
    
    return {
        "total_users": total_users,
        "roles_breakdown": roles_breakdown,
        "total_teams": total_teams,
        "active_sessions": total_users,
        "system_status": "Healthy (Milestone 1 Active)"
    }

@router.get("/audit-logs", response_model=List[AuditLogResponse])
def get_audit_logs(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Administrator"]))
):
    """Return recent audit logs (Administrator only)."""
    return db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(limit).all()
