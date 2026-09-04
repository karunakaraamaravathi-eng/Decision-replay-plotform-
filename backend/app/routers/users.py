from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import get_db
from app.models import User, RoleEnum, Team
from app.schemas import (
    UserResponse,
    UserUpdate,
    UserRoleUpdate,
    UserStatusUpdate
)
from app.auth import get_current_user, require_role, get_password_hash

router = APIRouter(prefix="/users", tags=["Users Management"])


@router.get("", response_model=List[UserResponse])
def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    role: Optional[RoleEnum] = None,
    team_id: Optional[int] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List registered users with optional filtering by role, team, or search text.
    Accessible to all authenticated users (Managers & Admins see full organizational directory).
    """
    query = db.query(User)
    
    if role:
        query = query.filter(User.role == role)
    if team_id:
        query = query.filter(User.team_id == team_id)
    if search:
        search_pattern = f"%{search.lower()}%"
        query = query.filter(
            or_(
                User.full_name.ilike(search_pattern),
                User.email.ilike(search_pattern)
            )
        )
    
    users = query.order_by(User.created_at.desc()).offset(skip).limit(limit).all()
    return users


@router.get("/{user_id}", response_model=UserResponse)
def get_user_by_id(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve single user details by ID.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.put("/{user_id}", response_model=UserResponse)
def update_user_profile(
    user_id: int,
    update_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update user profile.
    Employees can update their own profile; Administrators can update any profile.
    """
    if current_user.id != user_id and current_user.role != RoleEnum.ADMINISTRATOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to modify this profile."
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if update_data.email and update_data.email.lower() != user.email:
        existing = db.query(User).filter(User.email == update_data.email.lower()).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email is already taken.")
        user.email = update_data.email.lower()

    if update_data.full_name is not None:
        user.full_name = update_data.full_name

    if update_data.team_id is not None:
        if update_data.team_id == 0:
            user.team_id = None
        else:
            team = db.query(Team).filter(Team.id == update_data.team_id).first()
            if not team:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Team does not exist.")
            user.team_id = update_data.team_id

    if update_data.password:
        user.hashed_password = get_password_hash(update_data.password)

    db.commit()
    db.refresh(user)
    return user


@router.put("/{user_id}/role", response_model=UserResponse)
def update_user_role(
    user_id: int,
    role_data: UserRoleUpdate,
    current_user: User = Depends(require_role([RoleEnum.ADMINISTRATOR])),
    db: Session = Depends(get_db)
):
    """
    Change user role. (Restricted to ADMINISTRATOR only)
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Prevent admin from demoting themselves if they are the only administrator
    if user.id == current_user.id and role_data.role != RoleEnum.ADMINISTRATOR:
        admin_count = db.query(User).filter(User.role == RoleEnum.ADMINISTRATOR, User.is_active == True).count()
        if admin_count <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot demote the only remaining active Administrator."
            )

    user.role = role_data.role
    db.commit()
    db.refresh(user)
    return user


@router.put("/{user_id}/status", response_model=UserResponse)
def toggle_user_status(
    user_id: int,
    status_data: UserStatusUpdate,
    current_user: User = Depends(require_role([RoleEnum.ADMINISTRATOR])),
    db: Session = Depends(get_db)
):
    """
    Activate or deactivate a user account. (Restricted to ADMINISTRATOR only)
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if user.id == current_user.id and not status_data.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own administrator account."
        )

    user.is_active = status_data.is_active
    db.commit()
    db.refresh(user)
    return user
