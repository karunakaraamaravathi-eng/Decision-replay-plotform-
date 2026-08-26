from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Team, User, AuditLog
from app.schemas import TeamCreate, TeamResponse
from app.auth import get_current_user, require_roles

router = APIRouter(prefix="/teams", tags=["Team Management"])

@router.get("", response_model=List[TeamResponse])
def list_teams(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List teams with member count."""
    teams = db.query(Team).all()
    result = []
    for team in teams:
        member_count = db.query(User).filter(User.team_id == team.id).count()
        result.append(
            TeamResponse(
                id=team.id,
                name=team.name,
                description=team.description,
                manager_id=team.manager_id,
                created_at=team.created_at,
                member_count=member_count
            )
        )
    return result

@router.post("", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
def create_team(
    team_in: TeamCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Administrator", "Manager"]))
):
    """Create a new team (Manager / Administrator only)."""
    existing = db.query(Team).filter(Team.name == team_in.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Team with this name already exists."
        )

    new_team = Team(
        name=team_in.name,
        description=team_in.description,
        manager_id=team_in.manager_id or current_user.id
    )

    db.add(new_team)
    db.commit()
    db.refresh(new_team)

    # Audit log
    audit = AuditLog(
        user_id=current_user.id,
        action="TEAM_CREATE",
        entity_type="Team",
        entity_id=new_team.id,
        details=f"Created team: {new_team.name}"
    )
    db.add(audit)
    db.commit()

    return TeamResponse(
        id=new_team.id,
        name=new_team.name,
        description=new_team.description,
        manager_id=new_team.manager_id,
        created_at=new_team.created_at,
        member_count=0
    )
