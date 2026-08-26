from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List
from datetime import datetime

# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    user_id: int
    full_name: str
    email: str

class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None
    user_id: Optional[int] = None

class TokenVerifyResponse(BaseModel):
    valid: bool
    user_id: int
    email: str
    role: str
    full_name: str

class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=4, description="New password must be at least 4 characters")

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: Optional[str] = "Employee"
    department: Optional[str] = "Engineering"

class UserCreate(UserBase):
    password: str = Field(..., min_length=4, description="Password must be at least 4 characters")

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserUpdateRole(BaseModel):
    role: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    team_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)

# Team Schemas
class TeamBase(BaseModel):
    name: str
    description: Optional[str] = None

class TeamCreate(TeamBase):
    manager_id: Optional[int] = None

class TeamResponse(TeamBase):
    id: int
    manager_id: Optional[int] = None
    created_at: datetime
    member_count: Optional[int] = 0

    model_config = ConfigDict(from_attributes=True)

# Audit Log Schemas
class AuditLogResponse(BaseModel):
    id: int
    user_id: Optional[int]
    action: str
    entity_type: str
    entity_id: Optional[int]
    details: Optional[str]
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)

# System Stats Schema
class SystemStats(BaseModel):
    total_users: int
    roles_breakdown: dict
    total_teams: int
    active_sessions: int
    system_status: str = "Healthy"
