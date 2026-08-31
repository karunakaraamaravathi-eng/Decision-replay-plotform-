from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import Decision, DecisionVersion, Alternative, User, Team, AuditLog
from app.schemas import DecisionCreate, DecisionUpdate, DecisionResponse, DecisionVersionResponse
from app.auth import get_current_user

router = APIRouter(prefix="/decisions", tags=["Decision Management"])

@router.post("", response_model=DecisionResponse, status_code=status.HTTP_201_CREATED)
def create_decision(
    decision_in: DecisionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new organizational decision and record version 1 snapshot."""
    team_id = decision_in.team_id or current_user.team_id

    decision = Decision(
        title=decision_in.title,
        problem_statement=decision_in.problem_statement,
        category=decision_in.category,
        status=decision_in.status or "Draft",
        rationale=decision_in.rationale,
        creator_id=current_user.id,
        team_id=team_id,
        version=1
    )
    db.add(decision)
    db.commit()
    db.refresh(decision)

    # Save initial version 1 snapshot
    initial_version = DecisionVersion(
        decision_id=decision.id,
        version=1,
        title=decision.title,
        problem_statement=decision.problem_statement,
        category=decision.category,
        status=decision.status,
        rationale=decision.rationale,
        change_summary="Initial decision creation",
        created_by_id=current_user.id
    )
    db.add(initial_version)

    # Add initial alternatives if provided
    if decision_in.alternatives:
        for alt_in in decision_in.alternatives:
            alt = Alternative(
                decision_id=decision.id,
                title=alt_in.title,
                description=alt_in.description,
                pros=alt_in.pros,
                cons=alt_in.cons,
                estimated_cost=alt_in.estimated_cost or 0.0,
                risk_level=alt_in.risk_level or "Low",
                feasibility_score=alt_in.feasibility_score or 5
            )
            db.add(alt)

    # Audit Log
    audit = AuditLog(
        user_id=current_user.id,
        action="DECISION_CREATE",
        entity_type="Decision",
        entity_id=decision.id,
        details=f"Created decision '{decision.title}' in category '{decision.category}' with status '{decision.status}'"
    )
    db.add(audit)
    db.commit()
    db.refresh(decision)

    res = DecisionResponse.model_validate(decision)
    res.creator_name = current_user.full_name
    if decision.team:
        res.team_name = decision.team.name
    res.comments_count = len(decision.comments)
    res.attachments_count = len(decision.attachments)
    return res

@router.get("", response_model=List[DecisionResponse])
def list_decisions(
    category: Optional[str] = Query(None, description="Filter by category"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status"),
    search: Optional[str] = Query(None, description="Search keyword in title or problem statement"),
    team_id: Optional[int] = Query(None, description="Filter by team ID"),
    db: Session = Depends(get_db)
):
    """Retrieve decisions with optional filters for category, status, team, and search keywords."""
    query = db.query(Decision)

    if category and category != "All":
        query = query.filter(Decision.category == category)
    if status_filter and status_filter != "All":
        query = query.filter(Decision.status == status_filter)
    if team_id:
        query = query.filter(Decision.team_id == team_id)
    if search:
        pattern = f"%{search}%"
        query = query.filter((Decision.title.ilike(pattern)) | (Decision.problem_statement.ilike(pattern)))

    decisions = query.order_by(Decision.updated_at.desc()).all()

    result = []
    for d in decisions:
        res = DecisionResponse.model_validate(d)
        res.creator_name = d.creator.full_name if d.creator else "Unknown"
        res.team_name = d.team.name if d.team else None
        res.comments_count = len(d.comments)
        res.attachments_count = len(d.attachments)
        result.append(res)

    return result

@router.get("/{decision_id}", response_model=DecisionResponse)
def get_decision(
    decision_id: int,
    db: Session = Depends(get_db)
):
    """Get single decision details by ID including alternatives, comments count, attachments count."""
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")

    res = DecisionResponse.model_validate(decision)
    res.creator_name = decision.creator.full_name if decision.creator else "Unknown"
    res.team_name = decision.team.name if decision.team else None
    res.comments_count = len(decision.comments)
    res.attachments_count = len(decision.attachments)
    return res

@router.put("/{decision_id}", response_model=DecisionResponse)
def update_decision(
    decision_id: int,
    decision_in: DecisionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update decision details and automatically record a version snapshot."""
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")

    if decision_in.title is not None:
        decision.title = decision_in.title
    if decision_in.problem_statement is not None:
        decision.problem_statement = decision_in.problem_statement
    if decision_in.category is not None:
        decision.category = decision_in.category
    if decision_in.status is not None:
        decision.status = decision_in.status
    if decision_in.rationale is not None:
        decision.rationale = decision_in.rationale

    decision.version += 1
    db.commit()
    db.refresh(decision)

    # Version snapshot
    version_snapshot = DecisionVersion(
        decision_id=decision.id,
        version=decision.version,
        title=decision.title,
        problem_statement=decision.problem_statement,
        category=decision.category,
        status=decision.status,
        rationale=decision.rationale,
        change_summary=decision_in.change_summary or f"Updated to version {decision.version}",
        created_by_id=current_user.id
    )
    db.add(version_snapshot)

    audit = AuditLog(
        user_id=current_user.id,
        action="DECISION_UPDATE",
        entity_type="Decision",
        entity_id=decision.id,
        details=f"Updated decision '{decision.title}' to Version {decision.version}. Status: {decision.status}"
    )
    db.add(audit)
    db.commit()
    db.refresh(decision)

    res = DecisionResponse.model_validate(decision)
    res.creator_name = decision.creator.full_name if decision.creator else "Unknown"
    res.team_name = decision.team.name if decision.team else None
    res.comments_count = len(decision.comments)
    res.attachments_count = len(decision.attachments)
    return res

@router.delete("/{decision_id}", status_code=status.HTTP_200_OK)
def delete_decision(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete decision record."""
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")

    title = decision.title
    db.delete(decision)

    audit = AuditLog(
        user_id=current_user.id,
        action="DECISION_DELETE",
        entity_type="Decision",
        entity_id=decision_id,
        details=f"Deleted decision '{title}' (ID: {decision_id})"
    )
    db.add(audit)
    db.commit()
    return {"message": f"Decision '{title}' deleted successfully", "decision_id": decision_id}

@router.get("/{decision_id}/versions", response_model=List[DecisionVersionResponse])
def get_decision_versions(
    decision_id: int,
    db: Session = Depends(get_db)
):
    """Retrieve full version snapshot history for a given decision."""
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")

    versions = db.query(DecisionVersion).filter(DecisionVersion.decision_id == decision_id).order_by(DecisionVersion.version.desc()).all()
    result = []
    for v in versions:
        res = DecisionVersionResponse.model_validate(v)
        res.created_by_name = v.created_by.full_name if v.created_by else "System"
        result.append(res)
    return result

@router.get("/{decision_id}/versions/{version_num}", response_model=DecisionVersionResponse)
def get_decision_version_by_num(
    decision_id: int,
    version_num: int,
    db: Session = Depends(get_db)
):
    """Get a specific historical snapshot by version number."""
    v = db.query(DecisionVersion).filter(
        DecisionVersion.decision_id == decision_id,
        DecisionVersion.version == version_num
    ).first()
    if not v:
        raise HTTPException(status_code=404, detail=f"Version {version_num} for decision {decision_id} not found")

    res = DecisionVersionResponse.model_validate(v)
    res.created_by_name = v.created_by.full_name if v.created_by else "System"
    return res
