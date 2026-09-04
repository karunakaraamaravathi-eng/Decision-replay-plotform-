from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Team, RoleEnum, User
from app.schemas import TeamResponse, TeamCreate
from app.auth import get_current_user, require_role

router = APIRouter(prefix="/teams", tags=["Teams Management"])


@router.get("", response_model=List[TeamResponse])
def list_teams(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all organizational teams. Accessible to all authenticated users.
    """
    return db.query(Team).order_by(Team.name.asc()).all()


@router.post("", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
def create_team(
    team_in: TeamCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([RoleEnum.ADMINISTRATOR, RoleEnum.MANAGER]))
):
    """
    Create a new team. Restricted to Managers and Administrators.
    """
    existing = db.query(Team).filter(Team.name.ilike(team_in.name)).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A team with this name already exists."
        )

    team = Team(name=team_in.name.strip(), description=team_in.description)
    db.add(team)
    db.commit()
    db.refresh(team)
    return team


@router.get("/{team_id}", response_model=TeamResponse)
def get_team(
    team_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get team details by ID.
    """
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
    return team
