import json
from datetime import datetime
from typing import Optional, List, Tuple, Any
from sqlalchemy.orm import Session
from app.models import AuditLog, AuditAction, AuditResourceType, User


def log_audit_event(
    db: Session,
    action: str,
    resource_type: str,
    user_id: Optional[int] = None,
    resource_id: Optional[str] = None,
    details: Optional[Any] = None,
    ip_address: Optional[str] = None
) -> AuditLog:
    """
    Persist an immutable audit log record capturing an action, target resource, diff/metadata, and IP.
    """
    serialized_details = None
    if details is not None:
        if isinstance(details, (dict, list)):
            serialized_details = json.dumps(details, default=str)
        else:
            serialized_details = str(details)

    act_str = action.value if hasattr(action, 'value') else str(action)
    res_str = resource_type.value if hasattr(resource_type, 'value') else str(resource_type)

    audit_entry = AuditLog(
        user_id=user_id,
        action=act_str,
        resource_type=res_str,
        resource_id=str(resource_id) if resource_id is not None else None,
        details=serialized_details,
        ip_address=ip_address
    )
    db.add(audit_entry)
    db.commit()
    db.refresh(audit_entry)
    return audit_entry


def list_audit_logs(
    db: Session,
    user_id: Optional[int] = None,
    action: Optional[str] = None,
    resource_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100
) -> Tuple[List[AuditLog], int]:
    """
    Query audit logs with multi-parameter filtering, returning items and total count.
    """
    query = db.query(AuditLog)

    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    if action:
        query = query.filter(AuditLog.action.ilike(f"%{action}%"))
    if resource_type:
        query = query.filter(AuditLog.resource_type.ilike(f"%{resource_type}%"))
    if start_date:
        query = query.filter(AuditLog.timestamp >= start_date)
    if end_date:
        query = query.filter(AuditLog.timestamp <= end_date)

    total = query.count()
    items = query.order_by(AuditLog.timestamp.desc()).offset(skip).limit(limit).all()

    return items, total
