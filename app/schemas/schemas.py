"""Pydantic schemas for API request/response validation."""
from datetime import datetime
from typing import Optional, Union

from pydantic import BaseModel, EmailStr, Field, config_dict

from app.models.models import UserRole, ExamStatus


class ConfigMixin:
    """Shared config for schemas."""
    model_config = config_dict(from_attributes=True)


# User Schemas
class UserBase(ConfigMixin, BaseModel):
    """Base user schema."""
    email: EmailStr
    username: Optional[str] = None
    full_name: Optional[str] = None
    role: UserRole = UserRole.STUDENT
    department: Optional[str] = None


class UserCreate(UserBase):
    """User creation schema."""
    password: str = Field(..., min_length=8)
    tenant_id: Optional[int] = None


class UserUpdate(BaseModel):
    """User update schema."""
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    avatar_url: Optional[str] = None


class UserResponse(UserBase):
    """User response schema."""
    id: int
    tenant_id: int
    is_active: bool
    email_verified: bool
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserBrief(BaseModel):
    """Brief user info."""
    id: int
    email: str
    username: Optional[str] = None
    full_name: Optional[str] = None
    role: str

    class Config:
        from_attributes = True


# Auth Schemas
class LoginRequest(BaseModel):
    """Login request schema."""
    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema."""
    refresh_token: str


class TokenResponse(BaseModel):
    """Token response schema."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


# Tenant Schemas
class TenantCreate(BaseModel):
    """Tenant creation schema."""
    name: str = Field(..., min_length=2, max_length=255)
    slug: str = Field(..., min_length=2, max_length=100)
    domain: Optional[str] = None


class TenantUpdate(BaseModel):
    """Tenant update schema."""
    name: Optional[str] = None
    domain: Optional[str] = None
    logo_url: Optional[str] = None
    settings: Optional[dict] = None


class TenantResponse(TenantCreate):
    """Tenant response schema."""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


# Question Schemas
class Question(BaseModel):
    """Question schema."""
    id: int
    question: str
    options: list[str]
    correct: int


class QuestionSet(BaseModel):
    """Question set schema."""
    questions: list[Question]


# Exam Schemas
class ExamBase(ConfigMixin, BaseModel):
    """Base exam schema."""
    title: str = Field(..., max_length=500)
    description: Optional[str] = None
    instructions: Optional[str] = None
    duration_minutes: int = Field(..., gt=0)
    passing_score: int = Field(default=60, ge=0, le=100)
    shuffle_questions: bool = False
    shuffle_options: bool = False
    show_results: bool = False


class ExamCreate(ExamBase):
    """Exam creation schema."""
    questions: list[Question]
    scheduled_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None


class ExamUpdate(BaseModel):
    """Exam update schema."""
    title: Optional[str] = None
    description: Optional[str] = None
    instructions: Optional[str] = None
    duration_minutes: Optional[int] = Field(None, gt=0)
    passing_score: Optional[int] = Field(None, ge=0, le=100)
    shuffle_questions: Optional[bool] = None
    shuffle_options: Optional[bool] = None
    show_results: Optional[bool] = None
    status: Optional[ExamStatus] = None


class ExamResponse(ExamBase):
    """Exam response schema."""
    id: int
    tenant_id: int
    created_by: Optional[int] = None
    status: ExamStatus
    scheduled_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class ExamBrief(BaseModel):
    """Brief exam info."""
    id: int
    title: str
    status: str
    duration_minutes: int
    created_at: datetime


# Exam Session Schemas
class ExamStartRequest(BaseModel):
    """Exam start request."""
    exam_id: int


class AnswerSubmit(BaseModel):
    """Answer submission."""
    question_id: int
    selected_option: int


class ExamSessionSubmit(BaseModel):
    """Exam session submission."""
    answers: list[AnswerSubmit]


class ExamSessionResponse(BaseModel):
    """Exam session response."""
    id: int
    exam_id: int
    user_id: int
    score: Optional[float]
    total_correct: Optional[int]
    total_questions: Optional[int]
    is_completed: bool
    is_flagged: bool
    started_at: datetime
    submitted_at: Optional[datetime]

    class Config:
        from_attributes = True


# Behavior Event Schemas
class BehaviorEventResponse(BaseModel):
    """Behavior event response."""
    id: int
    session_id: int
    event_type: str
    severity: float
    details: Optional[dict]
    timestamp: datetime

    class Config:
        from_attributes = True


class BehaviorSummary(BaseModel):
    """Behavior analysis summary."""
    session_id: int
    total_events: int
    flagged: bool
    avg_severity: float
    events_by_type: dict


# Report Schemas
class ReportGenerateRequest(BaseModel):
    """Report generation request."""
    report_type: str
    filters: Optional[dict] = None


class ExamStats(BaseModel):
    """Exam statistics."""
    exam_id: int
    total_sessions: int
    completed_sessions: int
    avg_score: Optional[float]
    pass_rate: float
    flagged_sessions: int


class TenantStats(BaseModel):
    """Tenant analytics."""
    total_users: int
    total_exams: int
    total_sessions: int
    completion_rate: float
    avg_score: float
    exams: list[ExamStats]


# API Response Wrappers
class PaginatedResponse(BaseModel):
    """Paginated response wrapper."""
    items: list
    total: int
    page: int
    page_size: int
    total_pages: int


class MessageResponse(BaseModel):
    """Simple message response."""
    message: str


class ErrorResponse(BaseModel):
    """Error response."""
    error: str
    detail: Optional[str] = None