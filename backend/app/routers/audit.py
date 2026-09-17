from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, RoleEnum
from app.auth import get_current_active_user, require_role
from app.schemas import AuditLogListResponse, AuditLogResponse, UserResponse
from app.services import audit_service

router = APIRouter(prefix="/audit", tags=["Audit Logging & Compliance"])


@router.get(
    "/logs",
    response_model=AuditLogListResponse,
    dependencies=[Depends(require_role([RoleEnum.ADMINISTRATOR, RoleEnum.MANAGER]))]
)
def get_audit_logs(
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    action: Optional[str] = Query(None, description="Filter by action (CREATE, UPDATE, APPROVE, etc.)"),
    resource_type: Optional[str] = Query(None, description="Filter by resource type (DECISION, USER, etc.)"),
    start_date: Optional[datetime] = Query(None, description="Filter logs on or after this timestamp"),
    end_date: Optional[datetime] = Query(None, description="Filter logs on or before this timestamp"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Retrieve filterable audit compliance logs (Restricted to Administrator and Manager roles).
    """
    items, total = audit_service.list_audit_logs(
        db=db,
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit
    )

    formatted_items = [
        AuditLogResponse(
            id=item.id,
            user_id=item.user_id,
            action=item.action,
            resource_type=item.resource_type,
            resource_id=item.resource_id,
            details=item.parsed_details,
            ip_address=item.ip_address,
            timestamp=item.timestamp,
            user=UserResponse.model_validate(item.user) if item.user else None
        )
        for item in items
    ]

    return AuditLogListResponse(total=total, items=formatted_items)
