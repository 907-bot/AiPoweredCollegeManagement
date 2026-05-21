"""REST API routes for the exam platform."""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.database import get_db
from app.models.models import (
    Exam,
    ExamSession,
    ExamStatus,
    User,
    UserRole,
    BehaviorEvent,
    Tenant,
)
from app.schemas.schemas import (
    UserCreate,
    UserResponse,
    TokenResponse,
    LoginRequest,
    ExamCreate,
    ExamResponse,
    ExamUpdate,
    ExamBrief,
    ExamSessionResponse,
    ExamSessionSubmit,
    ExamStats,
    TenantStats,
    MessageResponse,
    TenantCreate,
    TenantResponse,
    BehaviorSummary,
)
from app.core.security import (
    create_tokens,
    verify_password,
    get_password_hash,
    get_current_user_id,
)


router = APIRouter(prefix="/api/v1", tags=["api"])


# ============================================
# AUTH ROUTES
# ============================================


@router.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """Register a new user."""
    # Check email already exists
    stmt = select(User).where(User.email == user_data.email)
    result = await db.execute(stmt)
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create user
    user = User(
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name,
        password_hash=get_password_hash(user_data.password),
        role=user_data.role,
        department=user_data.department,
        tenant_id=user_data.tenant_id or 1,  # Default tenant
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user


@router.post("/auth/login", response_model=TokenResponse)
async def login(
    credentials: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """Authenticate user and return tokens."""
    stmt = select(User).where(User.email == credentials.email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated",
        )

    # Update last login
    user.last_login = datetime.utcnow()
    await db.commit()

    return create_tokens(str(user.id))


@router.post("/auth/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_token: str,
    db: AsyncSession = Depends(get_db),
):
    """Refresh access token."""
    from app.core.security import decode_token, create_tokens

    token_data = decode_token(refresh_token)
    if token_data.type != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )

    return create_tokens(token_data.sub)


# ============================================
# TENANT ROUTES
# ============================================


@router.post("/tenants", response_model=TenantResponse, status_code=status.HTTP_201_CREATED)
async def create_tenant(
    data: TenantCreate,
    db: AsyncSession = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id),
):
    """Create a new tenant (organization)."""
    # Check if admin
    stmt = select(User).where(User.id == int(current_user_id))
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user or user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    # Check slug uniqueness
    stmt = select(Tenant).where(Tenant.slug == data.slug)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Slug already exists",
        )

    tenant = Tenant(name=data.name, slug=data.slug, domain=data.domain)
    db.add(tenant)
    await db.commit()
    await db.refresh(tenant)

    return tenant


@router.get("/tenants/{tenant_id}", response_model=TenantResponse)
async def get_tenant(
    tenant_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get tenant details."""
    stmt = select(Tenant).where(Tenant.id == tenant_id)
    result = await db.execute(stmt)
    tenant = result.scalar_one_or_none()

    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    return tenant


# ============================================
# USER ROUTES
# ============================================


@router.get("/users/me", response_model=UserResponse)
async def get_current_user(
    db: AsyncSession = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id),
):
    """Get current user profile."""
    stmt = select(User).where(User.id == int(current_user_id))
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@router.get("/users", response_model=list[UserResponse])
async def list_users(
    db: AsyncSession = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id),
    role: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """List users (admin/teacher only)."""
    stmt = select(User).order_by(User.created_at.desc())

    if role:
        stmt = stmt.where(User.role == role)

    stmt = stmt.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(stmt)
    users = result.scalars().all()

    return users


# ============================================
# EXAM ROUTES
# ============================================


@router.post("/exams", response_model=ExamResponse, status_code=status.HTTP_201_CREATED)
async def create_exam(
    data: ExamCreate,
    db: AsyncSession = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id),
):
    """Create a new exam."""
    stmt = select(User).where(User.id == int(current_user_id))
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user or user.role not in [UserRole.ADMIN, UserRole.TEACHER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Teacher or admin access required",
        )

    exam = Exam(
        tenant_id=user.tenant_id,
        created_by=int(current_user_id),
        title=data.title,
        description=data.description,
        instructions=data.instructions,
        duration_minutes=data.duration_minutes,
        passing_score=data.passing_score,
        questions={"questions": [q.model_dump() for q in data.questions]},
        shuffle_questions=data.shuffle_questions,
        shuffle_options=data.shuffle_options,
        show_results=data.show_results,
        scheduled_at=data.scheduled_at,
        expires_at=data.expires_at,
    )
    db.add(exam)
    await db.commit()
    await db.refresh(exam)

    return exam


@router.get("/exams", response_model=list[ExamBrief])
async def list_exams(
    db: AsyncSession = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id),
    status_filter: Optional[ExamStatus] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """List available exams."""
    stmt = select(Exam).order_by(Exam.created_at.desc())

    if status_filter:
        stmt = stmt.where(Exam.status == status_filter)

    stmt = stmt.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(stmt)
    exams = result.scalars().all()

    return exams


@router.get("/exams/{exam_id}", response_model=ExamResponse)
async def get_exam(
    exam_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id),
):
    """Get exam details."""
    stmt = select(Exam).where(Exam.id == exam_id)
    result = await db.execute(stmt)
    exam = result.scalar_one_or_none()

    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")

    return exam


@router.patch("/exams/{exam_id}", response_model=ExamResponse)
async def update_exam(
    exam_id: int,
    data: ExamUpdate,
    db: AsyncSession = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id),
):
    """Update exam (teacher/admin only)."""
    stmt = select(Exam).where(Exam.id == exam_id)
    result = await db.execute(stmt)
    exam = result.scalar_one_or_none()

    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")

    # Check permission
    user_stmt = select(User).where(User.id == int(current_user_id))
    user_result = await db.execute(user_stmt)
    user = user_result.scalar_one_or_none()

    if not user or user.role not in [UserRole.ADMIN, UserRole.TEACHER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Teacher or admin access required",
        )

    # Update fields
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(exam, field, value)

    await db.commit()
    await db.refresh(exam)

    return exam


@router.delete("/exams/{exam_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_exam(
    exam_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id),
):
    """Delete exam (admin only)."""
    stmt = select(User).where(User.id == int(current_user_id))
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user or user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    exam_stmt = select(Exam).where(Exam.id == exam_id)
    exam_result = await db.execute(exam_stmt)
    exam = exam_result.scalar_one_or_none()

    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")

    await db.delete(exam)
    await db.commit()


# ============================================
# EXAM SESSION ROUTES
# ============================================


@router.post("/exams/{exam_id}/start", response_model=ExamSessionResponse)
async def start_exam_session(
    exam_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id),
):
    """Start an exam session."""
    # Get exam
    stmt = select(Exam).where(Exam.id == exam_id)
    result = await db.execute(stmt)
    exam = result.scalar_one_or_none()

    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")

    if exam.status not in [ExamStatus.PUBLISHED, ExamStatus.ACTIVE]:
        raise HTTPException(
            status_code=400,
            detail="Exam is not available",
        )

    # Check for existing incomplete session
    session_stmt = select(ExamSession).where(
        ExamSession.exam_id == exam_id,
        ExamSession.user_id == int(current_user_id),
        ExamSession.is_completed == False,
    )
    session_result = await db.execute(session_stmt)
    existing_session = session_result.scalar_one_or_none()

    if existing_session:
        return existing_session

    # Create session
    session = ExamSession(
        exam_id=exam_id,
        user_id=int(current_user_id),
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)

    return session


@router.post("/exams/{exam_id}/submit", response_model=ExamSessionResponse)
async def submit_exam(
    exam_id: int,
    data: ExamSessionSubmit,
    db: AsyncSession = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id),
):
    """Submit exam answers."""
    # Get session
    stmt = select(ExamSession).where(
        ExamSession.exam_id == exam_id,
        ExamSession.user_id == int(current_user_id),
        ExamSession.is_completed == False,
    )
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="No active session found")

    # Get exam and calculate score
    exam_stmt = select(Exam).where(Exam.id == exam_id)
    exam_result = await db.execute(exam_stmt)
    exam = exam_result.scalar_one_or_none()

    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")

    # Grade answers
    questions = exam.questions.get("questions", [])
    answers_dict = {a.question_id: a.selected_option for a in data.answers}
    correct_count = 0
    total = len(questions)

    for q in questions:
        q_id = q.get("id")
        if q_id in answers_dict and answers_dict[q_id] == q.get("correct"):
            correct_count += 1

    score = (correct_count / total * 100) if total > 0 else 0
    passed = score >= exam.passing_score

    # Update session
    session.answers = {a.model_dump() for a in data.answers}
    session.score = score
    session.total_correct = correct_count
    session.total_questions = total
    session.is_completed = True
    session.submitted_at = datetime.utcnow()

    await db.commit()
    await db.refresh(session)

    return session


@router.get("/exams/{exam_id}/sessions", response_model=list[ExamSessionResponse])
async def list_exam_sessions(
    exam_id: int,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """List exam sessions (teacher/admin only)."""
    stmt = select(ExamSession).where(
        ExamSession.exam_id == exam_id
    ).order_by(ExamSession.started_at.desc())

    stmt = stmt.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(stmt)
    sessions = result.scalars().all()

    return sessions


# ============================================
# BEHAVIOR MONITORING ROUTES
# ============================================


@router.get("/sessions/{session_id}/behavior", response_model=BehaviorSummary)
async def get_behavior_summary(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id),
):
    """Get behavior analysis summary for a session."""
    stmt = select(BehaviorEvent).where(BehaviorEvent.session_id == session_id)
    result = await db.execute(stmt)
    events = result.scalars().all()

    events_by_type = {}
    total_severity = 0

    for event in events:
        events_by_type[event.event_type] = events_by_type.get(event.event_type, 0) + 1
        total_severity += event.severity

    avg_severity = total_severity / len(events) if events else 0

    return BehaviorSummary(
        session_id=session_id,
        total_events=len(events),
        flagged=any(e.severity > 0.5 for e in events),
        avg_severity=avg_severity,
        events_by_type=events_by_type,
    )


# ============================================
# REPORTS & ANALYTICS ROUTES
# ============================================


@router.get("/analytics/exams/{exam_id}", response_model=ExamStats)
async def get_exam_analytics(
    exam_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id),
):
    """Get analytics for a specific exam."""
    stmt = select(ExamSession).where(ExamSession.exam_id == exam_id)
    result = await db.execute(stmt)
    sessions = result.scalars().all()

    total = len(sessions)
    completed = sum(1 for s in sessions if s.is_completed)
    scores = [s.score for s in sessions if s.score is not None]
    avg_score = sum(scores) / len(scores) if scores else 0
    passed = sum(1 for s in sessions if s.score and s.score >= 60)
    pass_rate = (passed / completed * 100) if completed > 0 else 0
    flagged = sum(1 for s in sessions if s.is_flagged)

    return ExamStats(
        exam_id=exam_id,
        total_sessions=total,
        completed_sessions=completed,
        avg_score=avg_score,
        pass_rate=pass_rate,
        flagged_sessions=flagged,
    )


@router.get("/analytics/tenant", response_model=TenantStats)
async def get_tenant_analytics(
    db: AsyncSession = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id),
):
    """Get overall tenant analytics."""
    # Get current user's tenant
    user_stmt = select(User).where(User.id == int(current_user_id))
    user_result = await db.execute(user_stmt)
    user = user_result.scalar_one()

    # Get stats
    from sqlalchemy import func

    user_stmt = select(func.count(User.id)).where(User.tenant_id == user.tenant_id)
    user_result = await db.execute(user_stmt)
    total_users = user_result.scalar()

    exam_stmt = select(func.count(Exam.id)).where(Exam.tenant_id == user.tenant_id)
    exam_result = await db.execute(exam_stmt)
    total_exams = exam_result.scalar()

    session_stmt = select(ExamSession).options(
        selectinload(ExamSession.exam)
    ).join(Exam).where(Exam.tenant_id == user.tenant_id)
    session_result = await db.execute(session_stmt)
    all_sessions = session_result.scalars().all()

    total_sessions = len(all_sessions)
    completed = sum(1 for s in all_sessions if s.is_completed)
    scores = [s.score for s in all_sessions if s.score is not None]
    avg_score = sum(scores) / len(scores) if scores else 0

    return TenantStats(
        total_users=total_users,
        total_exams=total_exams,
        total_sessions=total_sessions,
        completion_rate=(completed / total_sessions * 100) if total_sessions > 0 else 0,
        avg_score=avg_score,
        exams=[],  # Will be populated via separate endpoint
    )


# ============================================
# HEALTH CHECK
# ============================================


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.utcnow()}