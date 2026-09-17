from datetime import datetime
from typing import Optional, List, Any, Dict
from pydantic import BaseModel, EmailStr, ConfigDict, Field
from app.models import (
    RoleEnum,
    DecisionStatus,
    CommentType,
    ApprovalStatus,
    NotificationType,
    AuditAction,
    AuditResourceType
)


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


# --- Alternative Schemas ---
class AlternativeBase(BaseModel):
    title: str
    description: Optional[str] = None
    pros: Optional[List[str]] = Field(default_factory=list)
    cons: Optional[List[str]] = Field(default_factory=list)
    estimated_cost: Optional[float] = 0.0
    feasibility_score: Optional[int] = Field(default=5, ge=1, le=10)
    risk_assessment: Optional[str] = None


class AlternativeCreate(AlternativeBase):
    pass


class AlternativeUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    pros: Optional[List[str]] = None
    cons: Optional[List[str]] = None
    estimated_cost: Optional[float] = None
    feasibility_score: Optional[int] = Field(default=None, ge=1, le=10)
    risk_assessment: Optional[str] = None


class AlternativeResponse(BaseModel):
    id: int
    decision_id: int
    title: str
    description: Optional[str] = None
    pros: List[str] = Field(default_factory=list)
    cons: List[str] = Field(default_factory=list)
    estimated_cost: float = 0.0
    feasibility_score: int = 5
    risk_assessment: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AlternativeMetrics(BaseModel):
    total_alternatives: int
    highest_feasibility_alternative: Optional[str] = None
    lowest_cost_alternative: Optional[str] = None
    total_estimated_cost: float = 0.0
    average_feasibility: float = 0.0


class AlternativeComparisonResponse(BaseModel):
    decision_id: int
    decision_title: str
    metrics: AlternativeMetrics
    alternatives: List[AlternativeResponse]


# --- Comment & Discussion Schemas ---
class CommentCreate(BaseModel):
    content: str
    comment_type: Optional[CommentType] = CommentType.GENERAL_COMMENT
    parent_id: Optional[int] = None


class CommentResponse(BaseModel):
    id: int
    decision_id: int
    author_id: int
    parent_id: Optional[int] = None
    comment_type: CommentType
    content: str
    created_at: datetime
    author: Optional[UserResponse] = None
    replies: List["CommentResponse"] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


# --- Attachment Schemas ---
class AttachmentResponse(BaseModel):
    id: int
    decision_id: int
    comment_id: Optional[int] = None
    uploader_id: int
    file_name: str
    file_path: Optional[str] = None
    file_size: int
    mime_type: str
    download_url: Optional[str] = None
    uploaded_at: datetime
    uploader: Optional[UserResponse] = None

    model_config = ConfigDict(from_attributes=True)


# --- Decision Version Schemas ---
class DecisionVersionResponse(BaseModel):
    id: int
    decision_id: int
    version_number: int
    snapshot_data: Dict[str, Any]
    changed_by_id: Optional[int] = None
    change_summary: Optional[str] = None
    timestamp: datetime
    changed_by: Optional[UserResponse] = None

    model_config = ConfigDict(from_attributes=True)


# --- Decision Schemas ---
class DecisionBase(BaseModel):
    title: str
    problem_statement: str
    category: str
    status: Optional[DecisionStatus] = DecisionStatus.DRAFT


class DecisionCreate(DecisionBase):
    pass


class DecisionUpdate(BaseModel):
    title: Optional[str] = None
    problem_statement: Optional[str] = None
    category: Optional[str] = None
    status: Optional[DecisionStatus] = None
    change_summary: Optional[str] = None


class DecisionResponse(DecisionBase):
    id: int
    created_by_id: int
    creator: Optional[UserResponse] = None
    created_at: datetime
    updated_at: datetime
    version_count: int = 1
    alternatives_count: int = 0

    model_config = ConfigDict(from_attributes=True)


# --- Approval Schemas ---
class ApprovalSubmit(BaseModel):
    reviewer_id: Optional[int] = None
    comments: Optional[str] = None


class ApprovalAction(BaseModel):
    comments: Optional[str] = None


class ApprovalReject(BaseModel):
    comments: str = Field(..., min_length=3, description="Mandatory reason for rejection")


class ApprovalEscalate(BaseModel):
    reason: Optional[str] = None
    new_approver_id: Optional[int] = None


class ApprovalResponse(BaseModel):
    id: int
    decision_id: int
    approver_id: int
    level: int
    status: ApprovalStatus
    comments: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    approver: Optional[UserResponse] = None

    model_config = ConfigDict(from_attributes=True)


class ApprovalHistoryResponse(BaseModel):
    id: int
    decision_id: int
    approver_id: Optional[int] = None
    level: int
    action: str
    comments: Optional[str] = None
    created_at: datetime
    approver: Optional[UserResponse] = None

    model_config = ConfigDict(from_attributes=True)


class DecisionDetailResponse(DecisionResponse):
    versions: List[DecisionVersionResponse] = Field(default_factory=list)
    alternatives: List[AlternativeResponse] = Field(default_factory=list)
    comments: List[CommentResponse] = Field(default_factory=list)
    attachments: List[AttachmentResponse] = Field(default_factory=list)
    approvals: List[ApprovalResponse] = Field(default_factory=list)
    approval_history: List[ApprovalHistoryResponse] = Field(default_factory=list)
    current_approval_level: Optional[int] = 1

    model_config = ConfigDict(from_attributes=True)


# --- Notification Schemas ---
class NotificationResponse(BaseModel):
    id: int
    user_id: int
    title: str
    message: str
    type: str
    is_read: bool
    link: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NotificationUnreadCount(BaseModel):
    unread_count: int


# --- Audit Log Schemas ---
class AuditLogResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    action: str
    resource_type: str
    resource_id: Optional[str] = None
    details: Optional[Any] = None
    ip_address: Optional[str] = None
    timestamp: datetime
    user: Optional[UserResponse] = None

    model_config = ConfigDict(from_attributes=True)


class AuditLogListResponse(BaseModel):
    total: int
    items: List[AuditLogResponse]


# --- Dashboard Schemas ---
class EmployeeDashboardResponse(BaseModel):
    my_decisions_count: Dict[str, int]
    my_decisions: List[DecisionResponse]
    pending_reviews_awaiting_input: List[DecisionResponse]
    recent_activity: List[Dict[str, Any]]


class ManagerDashboardResponse(BaseModel):
    team_overview: Dict[str, Any]
    pending_approvals_queue: List[Dict[str, Any]]
    decision_statistics: Dict[str, Any]


class AdminDashboardResponse(BaseModel):
    total_users_by_role: Dict[str, int]
    active_decisions_metrics: Dict[str, Any]
    approval_completion_turnaround: Dict[str, Any]
    categories_distribution: Dict[str, int]
    platform_activity_over_time: List[Dict[str, Any]]
    recent_audit_summary: List[AuditLogResponse]

