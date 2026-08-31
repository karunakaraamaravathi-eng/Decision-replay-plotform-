from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.database import get_db
from app.models import Decision, Alternative, User, AuditLog
from app.schemas import AlternativeCreate, AlternativeResponse
from app.auth import get_current_user

router = APIRouter(tags=["Alternative Comparison"])

@router.post("/decisions/{decision_id}/alternatives", response_model=AlternativeResponse, status_code=status.HTTP_201_CREATED)
def add_alternative(
    decision_id: int,
    alt_in: AlternativeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add a new alternative option to a decision."""
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")

    alt = Alternative(
        decision_id=decision_id,
        title=alt_in.title,
        description=alt_in.description,
        pros=alt_in.pros,
        cons=alt_in.cons,
        estimated_cost=alt_in.estimated_cost or 0.0,
        risk_level=alt_in.risk_level or "Low",
        feasibility_score=alt_in.feasibility_score or 5
    )
    db.add(alt)
    
    audit = AuditLog(
        user_id=current_user.id,
        action="ALTERNATIVE_ADD",
        entity_type="Decision",
        entity_id=decision_id,
        details=f"Added alternative '{alt.title}' (Cost: ${alt.estimated_cost}, Risk: {alt.risk_level}, Feasibility: {alt.feasibility_score}/10) to decision #{decision_id}"
    )
    db.add(audit)
    db.commit()
    db.refresh(alt)
    return alt

@router.get("/decisions/{decision_id}/alternatives", response_model=List[AlternativeResponse])
def list_alternatives(
    decision_id: int,
    db: Session = Depends(get_db)
):
    """List all alternatives recorded for a decision."""
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")

    return db.query(Alternative).filter(Alternative.decision_id == decision_id).all()

@router.get("/decisions/{decision_id}/alternatives/comparison")
def compare_alternatives(
    decision_id: int,
    db: Session = Depends(get_db)
):
    """Return comprehensive comparison matrix metrics and recommendation analysis for alternatives."""
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")

    alternatives = db.query(Alternative).filter(Alternative.decision_id == decision_id).all()
    if not alternatives:
        return {
            "decision_id": decision_id,
            "decision_title": decision.title,
            "total_alternatives": 0,
            "alternatives": [],
            "recommendation": None
        }

    alt_data = []
    best_option = None
    best_score = -1.0

    for alt in alternatives:
        risk_multiplier = {"Low": 1.2, "Medium": 1.0, "High": 0.7}.get(alt.risk_level, 1.0)
        cost_penalty = (alt.estimated_cost / 10000.0) if alt.estimated_cost > 0 else 0
        composite_score = round((alt.feasibility_score * risk_multiplier) - cost_penalty, 2)

        data = {
            "id": alt.id,
            "title": alt.title,
            "description": alt.description,
            "pros": alt.pros,
            "cons": alt.cons,
            "estimated_cost": alt.estimated_cost,
            "risk_level": alt.risk_level,
            "feasibility_score": alt.feasibility_score,
            "composite_score": composite_score
        }
        alt_data.append(data)

        if composite_score > best_score:
            best_score = composite_score
            best_option = alt.title

    return {
        "decision_id": decision_id,
        "decision_title": decision.title,
        "total_alternatives": len(alternatives),
        "alternatives": alt_data,
        "recommended_option": best_option,
        "recommendation_reason": f"Selected based on highest composite score ({best_score}) evaluating feasibility score and risk profile." if best_option else "None"
    }

@router.put("/alternatives/{alt_id}", response_model=AlternativeResponse)
def update_alternative(
    alt_id: int,
    alt_in: AlternativeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update alternative details."""
    alt = db.query(Alternative).filter(Alternative.id == alt_id).first()
    if not alt:
        raise HTTPException(status_code=404, detail="Alternative not found")

    alt.title = alt_in.title
    alt.description = alt_in.description
    alt.pros = alt_in.pros
    alt.cons = alt_in.cons
    alt.estimated_cost = alt_in.estimated_cost or 0.0
    alt.risk_level = alt_in.risk_level or "Low"
    alt.feasibility_score = alt_in.feasibility_score or 5

    audit = AuditLog(
        user_id=current_user.id,
        action="ALTERNATIVE_UPDATE",
        entity_type="Decision",
        entity_id=alt.decision_id,
        details=f"Updated alternative #{alt_id} '{alt.title}'"
    )
    db.add(audit)
    db.commit()
    db.refresh(alt)
    return alt

@router.delete("/alternatives/{alt_id}", status_code=status.HTTP_200_OK)
def delete_alternative(
    alt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete an alternative."""
    alt = db.query(Alternative).filter(Alternative.id == alt_id).first()
    if not alt:
        raise HTTPException(status_code=404, detail="Alternative not found")

    decision_id = alt.decision_id
    title = alt.title
    db.delete(alt)

    audit = AuditLog(
        user_id=current_user.id,
        action="ALTERNATIVE_DELETE",
        entity_type="Decision",
        entity_id=decision_id,
        details=f"Deleted alternative '{title}' from decision #{decision_id}"
    )
    db.add(audit)
    db.commit()
    return {"message": f"Alternative '{title}' deleted", "alternative_id": alt_id}
