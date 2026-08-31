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

# Alternative Schemas
class AlternativeBase(BaseModel):
    title: str
    description: Optional[str] = None
    pros: Optional[str] = None
    cons: Optional[str] = None
    estimated_cost: Optional[float] = 0.0
    risk_level: Optional[str] = "Low" # Low, Medium, High
    feasibility_score: Optional[int] = 5 # 1-10

class AlternativeCreate(AlternativeBase):
    pass

class AlternativeResponse(AlternativeBase):
    id: int
    decision_id: int

    model_config = ConfigDict(from_attributes=True)

# Comment Schemas
class CommentCreate(BaseModel):
    content: str
    parent_id: Optional[int] = None

class CommentResponse(BaseModel):
    id: int
    decision_id: int
    user_id: int
    parent_id: Optional[int] = None
    content: str
    created_at: datetime
    author_name: Optional[str] = None
    author_role: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

# Attachment Schemas
class AttachmentResponse(BaseModel):
    id: int
    decision_id: int
    uploaded_by_id: int
    filename: str
    file_path: str
    file_size: int
    content_type: Optional[str] = None
    uploaded_at: datetime
    uploader_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

# Decision Version Schemas
class DecisionVersionResponse(BaseModel):
    id: int
    decision_id: int
    version: int
    title: str
    problem_statement: str
    category: str
    status: str
    rationale: Optional[str] = None
    change_summary: Optional[str] = None
    created_by_id: Optional[int] = None
    created_at: datetime
    created_by_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

# Decision Schemas
class DecisionBase(BaseModel):
    title: str
    problem_statement: str
    category: str # Architecture, Infrastructure, Security, Process
    status: Optional[str] = "Draft" # Draft, Under Review, Approved, Rejected, Archived
    rationale: Optional[str] = None

class DecisionCreate(DecisionBase):
    team_id: Optional[int] = None
    alternatives: Optional[List[AlternativeCreate]] = []

class DecisionUpdate(BaseModel):
    title: Optional[str] = None
    problem_statement: Optional[str] = None
    category: Optional[str] = None
    status: Optional[str] = None
    rationale: Optional[str] = None
    change_summary: Optional[str] = "Updated decision details"

class DecisionResponse(DecisionBase):
    id: int
    creator_id: int
    team_id: Optional[int] = None
    version: int
    created_at: datetime
    updated_at: datetime
    creator_name: Optional[str] = None
    team_name: Optional[str] = None
    alternatives: List[AlternativeResponse] = []
    comments_count: Optional[int] = 0
    attachments_count: Optional[int] = 0

    model_config = ConfigDict(from_attributes=True)

