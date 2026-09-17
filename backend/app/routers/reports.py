from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response, Request
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.database import get_db
from app.models import User, RoleEnum, AuditAction, AuditResourceType
from app.auth import get_current_active_user, require_role
from app.services import report_service, audit_service

router = APIRouter(prefix="/reports", tags=["Reports & Data Exports"])


@router.get("/decisions/export")
def export_decisions_report(
    format: str = Query("pdf", pattern="^(pdf|excel)$", description="Export format: pdf or excel"),
    decision_id: Optional[int] = Query(None, description="Optional single decision ID to export"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    request: Request = None
):
    """
    Export organizational decisions summary report to PDF or Excel.
    """
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    client_ip = request.client.host if request and request.client else None

    if format == "pdf":
        file_bytes = report_service.generate_decisions_pdf(db, decision_id=decision_id)
        media_type = "application/pdf"
        filename = f"decisions_report_{timestamp}.pdf"
    else:
        file_bytes = report_service.generate_decisions_excel(db, decision_id=decision_id)
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        filename = f"decisions_report_{timestamp}.xlsx"

    audit_service.log_audit_event(
        db=db,
        action=AuditAction.EXPORT,
        resource_type=AuditResourceType.REPORT,
        user_id=current_user.id,
        resource_id=f"decisions_{format}",
        details={"format": format, "decision_id": decision_id},
        ip_address=client_ip
    )

    return Response(
        content=file_bytes,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@router.get("/decisions/{decision_id}/export")
def export_single_decision(
    decision_id: int,
    format: str = Query("pdf", pattern="^(pdf|excel)$", description="Export format: pdf or excel"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    request: Request = None
):
    """
    Export a specific decision's complete dossier to PDF or Excel.
    """
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    client_ip = request.client.host if request and request.client else None

    if format == "pdf":
        file_bytes = report_service.generate_decisions_pdf(db, decision_id=decision_id)
        media_type = "application/pdf"
        filename = f"decision_{decision_id}_dossier_{timestamp}.pdf"
    else:
        file_bytes = report_service.generate_decisions_excel(db, decision_id=decision_id)
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        filename = f"decision_{decision_id}_dossier_{timestamp}.xlsx"

    audit_service.log_audit_event(
        db=db,
        action=AuditAction.EXPORT,
        resource_type=AuditResourceType.REPORT,
        user_id=current_user.id,
        resource_id=f"decision_{decision_id}_{format}",
        details={"format": format, "decision_id": decision_id},
        ip_address=client_ip
    )

    return Response(
        content=file_bytes,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@router.get("/approvals/export")
def export_approvals_report(
    format: str = Query("pdf", pattern="^(pdf|excel)$", description="Export format: pdf or excel"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    request: Request = None
):
    """
    Export approvals turnaround and team productivity report to PDF or Excel.
    """
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    client_ip = request.client.host if request and request.client else None

    if format == "pdf":
        file_bytes = report_service.generate_approvals_pdf(db)
        media_type = "application/pdf"
        filename = f"approvals_report_{timestamp}.pdf"
    else:
        file_bytes = report_service.generate_approvals_excel(db)
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        filename = f"approvals_report_{timestamp}.xlsx"

    audit_service.log_audit_event(
        db=db,
        action=AuditAction.EXPORT,
        resource_type=AuditResourceType.REPORT,
        user_id=current_user.id,
        resource_id=f"approvals_{format}",
        details={"format": format},
        ip_address=client_ip
    )

    return Response(
        content=file_bytes,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@router.get(
    "/audit/export",
    dependencies=[Depends(require_role([RoleEnum.ADMINISTRATOR, RoleEnum.MANAGER]))]
)
def export_audit_report(
    format: str = Query("pdf", pattern="^(pdf|excel)$", description="Export format: pdf or excel"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    request: Request = None
):
    """
    Export enterprise audit trail & compliance log to PDF or Excel (Restricted to Manager and Admin).
    """
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    client_ip = request.client.host if request and request.client else None

    if format == "pdf":
        file_bytes = report_service.generate_audit_pdf(db)
        media_type = "application/pdf"
        filename = f"audit_compliance_report_{timestamp}.pdf"
    else:
        file_bytes = report_service.generate_audit_excel(db)
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        filename = f"audit_compliance_report_{timestamp}.xlsx"

    audit_service.log_audit_event(
        db=db,
        action=AuditAction.EXPORT,
        resource_type=AuditResourceType.REPORT,
        user_id=current_user.id,
        resource_id=f"audit_{format}",
        details={"format": format},
        ip_address=client_ip
    )

    return Response(
        content=file_bytes,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )
