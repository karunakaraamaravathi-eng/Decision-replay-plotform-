from typing import List, Optional, Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, DecisionStatus, ApprovalStatus
from app.schemas import (
    DecisionCreate,
    DecisionUpdate,
    DecisionResponse,
    DecisionDetailResponse,
    DecisionVersionResponse,
    UserResponse,
    AlternativeResponse,
    AttachmentResponse,
    ApprovalSubmit,
    ApprovalAction,
    ApprovalReject,
    ApprovalEscalate,
    ApprovalResponse,
    ApprovalHistoryResponse
)
from app.auth import get_current_active_user
from app.services import decision_service, alternative_service, discussion_service, file_service, approval_service

router = APIRouter(prefix="/decisions", tags=["Decisions & Version History"])

def _format_decision_response(d) -> DecisionResponse:
    return DecisionResponse(
        id=d.id,
        title=d.title,
        problem_statement=d.problem_statement,
        category=d.category,
        status=d.status,
        created_by_id=d.created_by_id,
        creator=UserResponse.model_validate(d.creator) if d.creator else None,
        created_at=d.created_at,
        updated_at=d.updated_at,
        version_count=len(d.versions) if d.versions else 1,
        alternatives_count=len(d.alternatives) if d.alternatives else 0
    )

@router.post("", response_model=DecisionResponse, status_code=status.HTTP_201_CREATED)
def create_decision(
    decision_in: DecisionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new organizational decision and automatically initialize version history (v1).
    """
    decision = decision_service.create_decision(db, decision_in, current_user)
    return _format_decision_response(decision)

@router.get("", response_model=List[DecisionResponse])
def list_decisions(
    status: Optional[DecisionStatus] = None,
    category: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    List all organizational decisions with optional filtering by status, category, or search term.
    """
    decisions = decision_service.list_decisions(
        db, status_filter=status, category_filter=category, search=search, skip=skip, limit=limit
    )
    return [_format_decision_response(d) for d in decisions]

@router.get("/{id}", response_model=DecisionDetailResponse)
def get_decision_details(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Retrieve comprehensive details for a decision, including alternatives, versions, threaded discussions, attachments, and approval workflow chain.
    """
    decision = decision_service.get_decision(db, id)
    
    # Alternatives
    alts = [
        AlternativeResponse(
            id=a.id,
            decision_id=a.decision_id,
            title=a.title,
            description=a.description,
            pros=a.parsed_pros,
            cons=a.parsed_cons,
            estimated_cost=a.estimated_cost or 0.0,
            feasibility_score=a.feasibility_score or 5,
            risk_assessment=a.risk_assessment,
            created_at=a.created_at
        )
        for a in decision.alternatives
    ]

    # Versions
    vers = [
        DecisionVersionResponse(
            id=v.id,
            decision_id=v.decision_id,
            version_number=v.version_number,
            snapshot_data=v.parsed_snapshot,
            changed_by_id=v.changed_by_id,
            changed_by=UserResponse.model_validate(v.changed_by) if v.changed_by else None,
            change_summary=v.change_summary,
            timestamp=v.timestamp
        )
        for v in decision.versions
    ]

    # Discussion comments tree
    comments = discussion_service.get_decision_comments_tree(db, id)

    # Attachments
    attachments = [file_service.to_attachment_response(att) for att in decision.attachments]

    # Approvals & Approval History (Milestone 3)
    approvals = [
        ApprovalResponse(
            id=app.id,
            decision_id=app.decision_id,
            approver_id=app.approver_id,
            level=app.level,
            status=app.status,
            comments=app.comments,
            created_at=app.created_at,
            updated_at=app.updated_at,
            approver=UserResponse.model_validate(app.approver) if app.approver else None
        )
        for app in decision.approvals
    ]

    history = [
        ApprovalHistoryResponse(
            id=h.id,
            decision_id=h.decision_id,
            approver_id=h.approver_id,
            level=h.level,
            action=h.action,
            comments=h.comments,
            created_at=h.created_at,
            approver=UserResponse.model_validate(h.approver) if h.approver else None
        )
        for h in decision.approval_history
    ]

    # Active level calculation
    pending_app = next((a for a in decision.approvals if a.status == ApprovalStatus.PENDING), None)
    curr_level = pending_app.level if pending_app else (2 if decision.status == DecisionStatus.APPROVED else 1)

    return DecisionDetailResponse(
        id=decision.id,
        title=decision.title,
        problem_statement=decision.problem_statement,
        category=decision.category,
        status=decision.status,
        created_by_id=decision.created_by_id,
        creator=UserResponse.model_validate(decision.creator) if decision.creator else None,
        created_at=decision.created_at,
        updated_at=decision.updated_at,
        version_count=len(vers),
        alternatives_count=len(alts),
        alternatives=alts,
        versions=vers,
        comments=comments,
        attachments=attachments,
        approvals=approvals,
        approval_history=history,
        current_approval_level=curr_level
    )

@router.put("/{id}", response_model=DecisionResponse)
def update_decision(
    id: int,
    update_in: DecisionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update decision metadata/status and automatically capture a new version snapshot.
    """
    decision = decision_service.update_decision(db, id, update_in, current_user)
    return _format_decision_response(decision)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_decision(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a decision and associated cascade records (Creator or Admin/Manager only).
    """
    decision_service.delete_decision(db, id, current_user)
    return None

# --- Version History Endpoints ---

@router.get("/{id}/versions", response_model=List[DecisionVersionResponse])
def get_decision_versions(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Fetch the complete historical version timeline and audit snapshots for a decision.
    """
    versions = decision_service.get_decision_versions(db, id)
    return [
        DecisionVersionResponse(
            id=v.id,
            decision_id=v.decision_id,
            version_number=v.version_number,
            snapshot_data=v.parsed_snapshot,
            changed_by_id=v.changed_by_id,
            changed_by=UserResponse.model_validate(v.changed_by) if v.changed_by else None,
            change_summary=v.change_summary,
            timestamp=v.timestamp
        )
        for v in versions
    ]

@router.get("/{id}/versions/{version_number}", response_model=DecisionVersionResponse)
def get_decision_version_by_number(
    id: int,
    version_number: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Retrieve an exact point-in-time snapshot for a specific decision version number.
    """
    v = decision_service.get_decision_version_by_number(db, id, version_number)
    return DecisionVersionResponse(
        id=v.id,
        decision_id=v.decision_id,
        version_number=v.version_number,
        snapshot_data=v.parsed_snapshot,
        changed_by_id=v.changed_by_id,
        changed_by=UserResponse.model_validate(v.changed_by) if v.changed_by else None,
        change_summary=v.change_summary,
        timestamp=v.timestamp
    )

# --- Milestone 3: Multi-Level Approval Workflow Endpoints ---

@router.post("/{id}/submit-for-review", response_model=DecisionResponse)
def submit_for_review(
    id: int,
    submit_in: Optional[ApprovalSubmit] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    request: Request = None
):
    """
    Submit a decision for Level 1 review, transitioning state to 'Under Review' and assigning a reviewer.
    """
    client_ip = request.client.host if request and request.client else None
    reviewer_id = submit_in.reviewer_id if submit_in else None
    comments = submit_in.comments if submit_in else None

    decision = approval_service.submit_decision_for_review(
        db=db,
        decision_id=id,
        current_user=current_user,
        reviewer_id=reviewer_id,
        comments=comments,
        ip_address=client_ip
    )
    return _format_decision_response(decision)

@router.post("/{id}/approve", response_model=DecisionResponse)
def approve_decision_level(
    id: int,
    action_in: Optional[ApprovalAction] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    request: Request = None
):
    """
    Approve decision at current level. If Level 1 passes, automatically advances to Level 2 Manager review.
    If Level 2 passes, status transitions to 'Approved'.
    """
    client_ip = request.client.host if request and request.client else None
    comments = action_in.comments if action_in else None

    decision = approval_service.approve_decision(
        db=db,
        decision_id=id,
        current_user=current_user,
        comments=comments,
        ip_address=client_ip
    )
    return _format_decision_response(decision)

@router.post("/{id}/reject", response_model=DecisionResponse)
def reject_decision_level(
    id: int,
    reject_in: ApprovalReject,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    request: Request = None
):
    """
    Reject decision at review level, transitioning status to 'Rejected' with mandatory feedback explanation.
    """
    client_ip = request.client.host if request and request.client else None
    decision = approval_service.reject_decision(
        db=db,
        decision_id=id,
        current_user=current_user,
        comments=reject_in.comments,
        ip_address=client_ip
    )
    return _format_decision_response(decision)

@router.post("/{id}/escalate", response_model=DecisionResponse)
def escalate_decision_review(
    id: int,
    escalate_in: Optional[ApprovalEscalate] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    request: Request = None
):
    """
    Escalate a pending review to senior manager or administrator for immediate intervention.
    """
    client_ip = request.client.host if request and request.client else None
    reason = escalate_in.reason if escalate_in else None
    new_approver_id = escalate_in.new_approver_id if escalate_in else None

    decision = approval_service.escalate_decision(
        db=db,
        decision_id=id,
        current_user=current_user,
        reason=reason,
        new_approver_id=new_approver_id,
        ip_address=client_ip
    )
    return _format_decision_response(decision)

@router.get("/{id}/approval-history", response_model=Dict[str, Any])
def get_decision_approval_history(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Retrieve the historical trail of multi-level status transitions, reviewer decisions, and rationale.
    """
    history_data = approval_service.get_approval_history(db, id)
    
    # Format approvals and history with UserResponse
    approvals_formatted = [
        ApprovalResponse(
            id=app.id,
            decision_id=app.decision_id,
            approver_id=app.approver_id,
            level=app.level,
            status=app.status,
            comments=app.comments,
            created_at=app.created_at,
            updated_at=app.updated_at,
            approver=UserResponse.model_validate(app.approver) if app.approver else None
        ).model_dump()
        for app in history_data["approvals"]
    ]

    history_formatted = [
        ApprovalHistoryResponse(
            id=h.id,
            decision_id=h.decision_id,
            approver_id=h.approver_id,
            level=h.level,
            action=h.action,
            comments=h.comments,
            created_at=h.created_at,
            approver=UserResponse.model_validate(h.approver) if h.approver else None
        ).model_dump()
        for h in history_data["history"]
    ]

    return {
        "decision_id": history_data["decision_id"],
        "decision_title": history_data["decision_title"],
        "status": history_data["status"],
        "current_level": history_data["current_level"],
        "pending_approver": history_data["pending_approver"],
        "approvals": approvals_formatted,
        "history": history_formatted
    }

