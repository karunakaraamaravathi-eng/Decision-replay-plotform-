from typing import Optional, Dict, Any, List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from app.models import (
    Decision,
    DecisionStatus,
    Approval,
    ApprovalHistory,
    ApprovalStatus,
    User,
    RoleEnum,
    AuditAction,
    AuditResourceType,
    NotificationType,
    utc_now
)
from app.services import notification_service, audit_service


def _find_default_reviewer(db: Session, team_id: Optional[int]) -> Optional[User]:
    """Find a designated or default reviewer for level 1 approval."""
    if team_id:
        team_reviewer = db.query(User).filter(
            User.team_id == team_id,
            User.role == RoleEnum.REVIEWER,
            User.is_active == True
        ).first()
        if team_reviewer:
            return team_reviewer

        team_manager = db.query(User).filter(
            User.team_id == team_id,
            User.role.in_([RoleEnum.MANAGER, RoleEnum.ADMINISTRATOR]),
            User.is_active == True
        ).first()
        if team_manager:
            return team_manager

    # Fallback to any active Reviewer
    reviewer = db.query(User).filter(
        User.role == RoleEnum.REVIEWER,
        User.is_active == True
    ).first()
    if reviewer:
        return reviewer

    # Fallback to any Manager or Admin
    return db.query(User).filter(
        User.role.in_([RoleEnum.MANAGER, RoleEnum.ADMINISTRATOR]),
        User.is_active == True
    ).first()


def _find_default_manager(db: Session, team_id: Optional[int]) -> Optional[User]:
    """Find a manager or administrator for level 2 approval."""
    if team_id:
        team_mgr = db.query(User).filter(
            User.team_id == team_id,
            User.role.in_([RoleEnum.MANAGER, RoleEnum.ADMINISTRATOR]),
            User.is_active == True
        ).first()
        if team_mgr:
            return team_mgr

    # Fallback to any Manager
    mgr = db.query(User).filter(
        User.role == RoleEnum.MANAGER,
        User.is_active == True
    ).first()
    if mgr:
        return mgr

    return db.query(User).filter(
        User.role == RoleEnum.ADMINISTRATOR,
        User.is_active == True
    ).first()


def submit_decision_for_review(
    db: Session,
    decision_id: int,
    current_user: User,
    reviewer_id: Optional[int] = None,
    comments: Optional[str] = None,
    ip_address: Optional[str] = None
) -> Decision:
    """
    Transition a decision from Draft / Rejected -> Under Review and initiate Level 1 approval.
    """
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Decision not found")

    # Only creator, manager, or administrator can submit
    if (
        decision.created_by_id != current_user.id
        and current_user.role not in [RoleEnum.MANAGER, RoleEnum.ADMINISTRATOR]
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the decision author, team manager, or administrator can submit this decision for review."
        )

    if decision.status == DecisionStatus.APPROVED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Approved decisions cannot be re-submitted. Please formulate a new version or revision."
        )

    # Resolve Level 1 Reviewer
    approver = None
    if reviewer_id:
        approver = db.query(User).filter(User.id == reviewer_id, User.is_active == True).first()
        if not approver:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Selected reviewer not found or inactive")
    else:
        approver = _find_default_reviewer(db, current_user.team_id)

    if not approver:
        # Self-fallback or admin fallback
        approver = current_user

    # Reset any previous pending approvals for clean slate
    db.query(Approval).filter(
        Approval.decision_id == decision.id,
        Approval.status == ApprovalStatus.PENDING
    ).update({"status": ApprovalStatus.REJECTED, "comments": "Superseded by new submission"})

    # Create Level 1 Approval Record
    approval = Approval(
        decision_id=decision.id,
        approver_id=approver.id,
        level=1,
        status=ApprovalStatus.PENDING,
        comments=comments
    )
    db.add(approval)

    # Create Approval History Entry
    history = ApprovalHistory(
        decision_id=decision.id,
        approver_id=approver.id,
        level=1,
        action="SUBMITTED",
        comments=comments or "Decision submitted for Level 1 review"
    )
    db.add(history)

    # Update Decision Status
    decision.status = DecisionStatus.UNDER_REVIEW
    decision.updated_at = utc_now()
    db.commit()
    db.refresh(decision)

    # Audit Logging
    audit_service.log_audit_event(
        db=db,
        action=AuditAction.SUBMIT,
        resource_type=AuditResourceType.DECISION,
        user_id=current_user.id,
        resource_id=str(decision.id),
        details={"level": 1, "assigned_reviewer_id": approver.id, "reviewer_name": approver.full_name},
        ip_address=ip_address
    )

    # System Notifications
    if approver.id != current_user.id:
        notification_service.create_notification(
            db=db,
            user_id=approver.id,
            title="Review Requested",
            message=f"'{decision.title}' has been submitted and assigned to you for Level 1 review.",
            type=NotificationType.APPROVAL_REQUEST.value,
            link=f"/decisions/{decision.id}"
        )

    notification_service.create_notification(
        db=db,
        user_id=decision.created_by_id,
        title="Decision Under Review",
        message=f"Your decision '{decision.title}' is now Under Review (Level 1 assigned to {approver.full_name}).",
        type=NotificationType.DECISION_UPDATE.value,
        link=f"/decisions/{decision.id}"
    )

    return decision


def approve_decision(
    db: Session,
    decision_id: int,
    current_user: User,
    comments: Optional[str] = None,
    ip_address: Optional[str] = None
) -> Decision:
    """
    Approve the decision at the current level.
    If Level 1: advance to Level 2 (Manager review).
    If Level 2: transition decision status to Approved.
    """
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Decision not found")

    if decision.status != DecisionStatus.UNDER_REVIEW:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Decision must be in 'Under Review' status to approve. Current status: {decision.status.value}"
        )

    # Locate current pending approval
    current_approval = db.query(Approval).filter(
        Approval.decision_id == decision.id,
        Approval.status == ApprovalStatus.PENDING
    ).order_by(Approval.level.asc()).first()

    current_level = current_approval.level if current_approval else 1

    # Check approval authority
    # Level 1: Reviewer, Manager, Admin, or explicitly assigned approver
    # Level 2: Manager, Admin, or explicitly assigned approver
    is_assigned = current_approval and current_approval.approver_id == current_user.id
    is_admin = current_user.role == RoleEnum.ADMINISTRATOR
    is_manager = current_user.role == RoleEnum.MANAGER
    is_reviewer = current_user.role == RoleEnum.REVIEWER

    if current_level == 1:
        if not (is_assigned or is_reviewer or is_manager or is_admin):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have reviewer permissions to approve at Level 1."
            )
    else:  # Level 2+
        if not (is_assigned or is_manager or is_admin):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Level 2 approval requires Manager or Administrator privileges."
            )

    # Mark current approval as approved
    if current_approval:
        current_approval.status = ApprovalStatus.APPROVED
        current_approval.comments = comments
        current_approval.approver_id = current_user.id
        current_approval.updated_at = utc_now()

    # Log History for this level approval
    db.add(ApprovalHistory(
        decision_id=decision.id,
        approver_id=current_user.id,
        level=current_level,
        action="APPROVED",
        comments=comments or f"Approved at Level {current_level}"
    ))

    # Determine next step
    if current_level == 1:
        # Advance to Level 2 (Manager)
        manager = _find_default_manager(db, current_user.team_id) or current_user
        lvl2_approval = Approval(
            decision_id=decision.id,
            approver_id=manager.id,
            level=2,
            status=ApprovalStatus.PENDING,
            comments=None
        )
        db.add(lvl2_approval)

        db.add(ApprovalHistory(
            decision_id=decision.id,
            approver_id=manager.id,
            level=2,
            action="ESCALATED_TO_LEVEL_2",
            comments=f"Level 1 passed by {current_user.full_name}. Forwarded to Manager Level 2."
        ))

        decision.updated_at = utc_now()
        db.commit()
        db.refresh(decision)

        # Notifications
        notification_service.create_notification(
            db=db,
            user_id=manager.id,
            title="Manager Approval Required (Level 2)",
            message=f"'{decision.title}' passed Level 1 review and is awaiting your Level 2 Manager approval.",
            type=NotificationType.APPROVAL_REQUEST.value,
            link=f"/decisions/{decision.id}"
        )
        notification_service.create_notification(
            db=db,
            user_id=decision.created_by_id,
            title="Level 1 Review Passed",
            message=f"'{decision.title}' was approved at Level 1 by {current_user.full_name} and advanced to Manager approval.",
            type=NotificationType.DECISION_UPDATE.value,
            link=f"/decisions/{decision.id}"
        )

        audit_service.log_audit_event(
            db=db,
            action=AuditAction.APPROVE,
            resource_type=AuditResourceType.APPROVAL,
            user_id=current_user.id,
            resource_id=str(decision.id),
            details={"level": 1, "next_level": 2, "manager_assigned": manager.full_name, "comments": comments},
            ip_address=ip_address
        )
    else:
        # Final Level Approved!
        decision.status = DecisionStatus.APPROVED
        decision.updated_at = utc_now()
        db.commit()
        db.refresh(decision)

        # Notify author and team
        notification_service.create_notification(
            db=db,
            user_id=decision.created_by_id,
            title="Decision Approved!",
            message=f"Congratulations! Your decision '{decision.title}' has received final organizational approval.",
            type=NotificationType.DECISION_UPDATE.value,
            link=f"/decisions/{decision.id}"
        )

        audit_service.log_audit_event(
            db=db,
            action=AuditAction.APPROVE,
            resource_type=AuditResourceType.DECISION,
            user_id=current_user.id,
            resource_id=str(decision.id),
            details={"level": current_level, "final_status": "Approved", "comments": comments},
            ip_address=ip_address
        )

    return decision


def reject_decision(
    db: Session,
    decision_id: int,
    current_user: User,
    comments: str,
    ip_address: Optional[str] = None
) -> Decision:
    """
    Reject the decision at any review level, returning it to Rejected status with mandatory feedback.
    """
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Decision not found")

    if decision.status != DecisionStatus.UNDER_REVIEW:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Only decisions in 'Under Review' status can be rejected. Current status: {decision.status.value}"
        )

    if not comments or len(comments.strip()) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rejection rationale/feedback comments are mandatory."
        )

    current_approval = db.query(Approval).filter(
        Approval.decision_id == decision.id,
        Approval.status == ApprovalStatus.PENDING
    ).first()

    current_level = current_approval.level if current_approval else 1

    # Check authority
    is_assigned = current_approval and current_approval.approver_id == current_user.id
    can_reject = (
        is_assigned
        or current_user.role in [RoleEnum.REVIEWER, RoleEnum.MANAGER, RoleEnum.ADMINISTRATOR]
    )
    if not can_reject:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permissions to reject this decision review."
        )

    if current_approval:
        current_approval.status = ApprovalStatus.REJECTED
        current_approval.comments = comments
        current_approval.approver_id = current_user.id
        current_approval.updated_at = utc_now()

    db.add(ApprovalHistory(
        decision_id=decision.id,
        approver_id=current_user.id,
        level=current_level,
        action="REJECTED",
        comments=comments
    ))

    decision.status = DecisionStatus.REJECTED
    decision.updated_at = utc_now()
    db.commit()
    db.refresh(decision)

    # Notify author
    notification_service.create_notification(
        db=db,
        user_id=decision.created_by_id,
        title="Decision Rejected",
        message=f"Your decision '{decision.title}' was rejected by {current_user.full_name}. Rationale: {comments}",
        type=NotificationType.DECISION_UPDATE.value,
        link=f"/decisions/{decision.id}"
    )

    # Audit log
    audit_service.log_audit_event(
        db=db,
        action=AuditAction.REJECT,
        resource_type=AuditResourceType.DECISION,
        user_id=current_user.id,
        resource_id=str(decision.id),
        details={"level": current_level, "rejected_by": current_user.full_name, "reason": comments},
        ip_address=ip_address
    )

    return decision


def escalate_decision(
    db: Session,
    decision_id: int,
    current_user: User,
    reason: Optional[str] = None,
    new_approver_id: Optional[int] = None,
    ip_address: Optional[str] = None
) -> Decision:
    """
    Escalate a pending decision beyond SLA or directly assign to a senior manager/administrator.
    """
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Decision not found")

    if decision.status != DecisionStatus.UNDER_REVIEW:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only decisions in 'Under Review' can be escalated."
        )

    if current_user.role not in [RoleEnum.MANAGER, RoleEnum.ADMINISTRATOR, RoleEnum.REVIEWER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only reviewers, managers, or administrators can escalate reviews."
        )

    current_approval = db.query(Approval).filter(
        Approval.decision_id == decision.id,
        Approval.status == ApprovalStatus.PENDING
    ).first()

    # Determine target manager or administrator
    target_user = None
    if new_approver_id:
        target_user = db.query(User).filter(User.id == new_approver_id, User.is_active == True).first()
    if not target_user:
        target_user = _find_default_manager(db, current_user.team_id)

    target_id = target_user.id if target_user else current_user.id
    target_name = target_user.full_name if target_user else "Manager"

    if current_approval:
        current_approval.approver_id = target_id
        current_approval.comments = f"Escalated by {current_user.full_name}: {reason or 'SLA threshold reached'}"
        current_approval.updated_at = utc_now()
    else:
        current_approval = Approval(
            decision_id=decision.id,
            approver_id=target_id,
            level=2,
            status=ApprovalStatus.PENDING,
            comments=reason
        )
        db.add(current_approval)

    db.add(ApprovalHistory(
        decision_id=decision.id,
        approver_id=target_id,
        level=current_approval.level if current_approval else 2,
        action="ESCALATED",
        comments=f"Escalated to {target_name}. Reason: {reason or 'SLA turnaround escalation'}"
    ))

    decision.updated_at = utc_now()
    db.commit()
    db.refresh(decision)

    # Notify new assignee
    if target_id != current_user.id:
        notification_service.create_notification(
            db=db,
            user_id=target_id,
            title="Escalated Review Urgency",
            message=f"'{decision.title}' has been escalated to you by {current_user.full_name}. Priority review needed.",
            type=NotificationType.ESCALATION.value,
            link=f"/decisions/{decision.id}"
        )

    audit_service.log_audit_event(
        db=db,
        action=AuditAction.ESCALATE,
        resource_type=AuditResourceType.DECISION,
        user_id=current_user.id,
        resource_id=str(decision.id),
        details={"escalated_to_id": target_id, "reason": reason},
        ip_address=ip_address
    )

    return decision


def get_approval_history(db: Session, decision_id: int) -> Dict[str, Any]:
    """Retrieve complete approval history and active levels for a decision."""
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Decision not found")

    approvals = db.query(Approval).filter(
        Approval.decision_id == decision_id
    ).order_by(Approval.level.asc()).all()

    history = db.query(ApprovalHistory).filter(
        ApprovalHistory.decision_id == decision_id
    ).order_by(ApprovalHistory.created_at.desc()).all()

    active_pending = next((a for a in approvals if a.status == ApprovalStatus.PENDING), None)

    return {
        "decision_id": decision.id,
        "decision_title": decision.title,
        "status": decision.status.value,
        "current_level": active_pending.level if active_pending else (2 if decision.status == DecisionStatus.APPROVED else 1),
        "pending_approver": {
            "id": active_pending.approver.id,
            "full_name": active_pending.approver.full_name,
            "role": active_pending.approver.role.value
        } if active_pending and active_pending.approver else None,
        "approvals": approvals,
        "history": history
    }
