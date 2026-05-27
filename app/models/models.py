"""Database models using SQLAlchemy."""
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Integer,
    JSON,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func


class UserRole(str, Enum):
    """User roles."""
    ADMIN = "admin"
    TEACHER = "teacher"
    STUDENT = "student"


class ExamStatus(str, Enum):
    """Exam statuses."""
    DRAFT = "draft"
    PUBLISHED = "published"
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class Base(DeclarativeBase):
    """Base model."""
    pass


class Tenant(Base):
    """Multi-tenant organization."""
    __tablename__ = "tenants"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True)
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    domain: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    logo_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    settings: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    users: Mapped[list["User"]] = relationship("User", back_populates="tenant", lazy="selectin")
    exams: Mapped[list["Exam"]] = relationship("Exam", back_populates="tenant", lazy="selectin")


class User(Base):
    """User model."""
    __tablename__ = "users"
    __table_args__ = (UniqueConstraint("tenant_id", "email", name="uq_user_tenant_email"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"))
    email: Mapped[str] = mapped_column(String(255), index=True)
    username: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(SQLEnum(UserRole), default=UserRole.STUDENT)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    department: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="users")
    created_exams: Mapped[list["Exam"]] = relationship("Exam", back_populates="created_by_user", foreign_keys="Exam.created_by")
    exam_sessions: Mapped[list["ExamSession"]] = relationship("ExamSession", back_populates="user", lazy="selectin")


class Exam(Base):
    """Exam model."""
    __tablename__ = "exams"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"))
    created_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    title: Mapped[str] = mapped_column(String(500))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    instructions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    duration_minutes: Mapped[int] = mapped_column(Integer)
    passing_score: Mapped[int] = mapped_column(Integer, default=60)
    questions: Mapped[dict] = mapped_column(JSON)
    shuffle_questions: Mapped[bool] = mapped_column(Boolean, default=False)
    shuffle_options: Mapped[bool] = mapped_column(Boolean, default=False)
    show_results: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[ExamStatus] = mapped_column(SQLEnum(ExamStatus), default=ExamStatus.DRAFT)
    scheduled_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="exams")
    created_by_user: Mapped[Optional["User"]] = relationship("User", back_populates="created_exams", foreign_keys=[created_by])
    sessions: Mapped[list["ExamSession"]] = relationship("ExamSession", back_populates="exam", lazy="selectin")


class ExamSession(Base):
    """Exam session model."""
    __tablename__ = "exam_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    exam_id: Mapped[int] = mapped_column(ForeignKey("exams.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    answers: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    score: Mapped[Optional[float]] = mapped_column(Numeric(5, 2), nullable=True)
    total_correct: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    total_questions: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    is_flagged: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    exam: Mapped["Exam"] = relationship("Exam", back_populates="sessions")
    user: Mapped["User"] = relationship("User", back_populates="exam_sessions")
    behavior_events: Mapped[list["BehaviorEvent"]] = relationship("BehaviorEvent", back_populates="session", lazy="selectin", cascade="all, delete-orphan")


class BehaviorEvent(Base):
    """AI behavior event log."""
    __tablename__ = "behavior_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("exam_sessions.id"))
    event_type: Mapped[str] = mapped_column(String(100))
    severity: Mapped[float] = mapped_column(Numeric(3, 2), default=0.0)
    details: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    frame_data: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Base64 encoded frame
    timestamp: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    session: Mapped["ExamSession"] = relationship("ExamSession", back_populates="behavior_events")


class Report(Base):
    """Analytics reports."""
    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"))
    report_type: Mapped[str] = mapped_column(String(100))
    title: Mapped[str] = mapped_column(String(500))
    filters: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    data: Mapped[dict] = mapped_column(JSON)
    generated_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


# Alias exports for backward compatibility
UserModel = User
ExamModel = Exam
ExamSessionModel = ExamSession
BehaviorEventModel = BehaviorEvent