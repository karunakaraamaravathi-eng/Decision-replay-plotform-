from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, ConfigDict
from app.models import RoleEnum


# --- Team Schemas ---
class TeamBase(BaseModel):
    name: str
    description: Optional[str] = None


class TeamCreate(TeamBase):
    pass


class TeamResponse(TeamBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# --- User Schemas ---
class UserBase(BaseModel):
    email: EmailStr
    full_name: str


class UserCreate(UserBase):
    password: str
    role: Optional[RoleEnum] = RoleEnum.EMPLOYEE
    team_id: Optional[int] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    team_id: Optional[int] = None
    password: Optional[str] = None


class UserRoleUpdate(BaseModel):
    role: RoleEnum


class UserStatusUpdate(BaseModel):
    is_active: bool


class UserResponse(UserBase):
    id: int
    role: RoleEnum
    team_id: Optional[int] = None
    is_active: bool
    created_at: datetime
    team: Optional[TeamResponse] = None

    model_config = ConfigDict(from_attributes=True)


# --- Authentication / Token Schemas ---
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenPayload(BaseModel):
    sub: Optional[str] = None
    role: Optional[str] = None
    exp: Optional[int] = None
