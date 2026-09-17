from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.config import settings
from app.database import engine, Base, SessionLocal
from app.models import User, Team, RoleEnum
from app.auth import get_password_hash
from app.routers import (
    auth,
    users,
    teams,
    decisions,
    discussions,
    alternatives,
    attachments,
    notifications,
    audit,
    dashboards,
    reports
)


def seed_initial_data(db: Session):
    """Seed initial sample teams, role-based test users, and sample decision records if database is empty."""
    from app.models import (
        Decision,
        Alternative,
        Comment,
        DecisionVersion,
        DecisionStatus,
        CommentType,
        Approval,
        ApprovalHistory,
        ApprovalStatus,
        Notification,
        AuditLog,
        NotificationType,
        AuditAction,
        AuditResourceType
    )
    import json

    # Seed Teams
    if db.query(Team).count() == 0:
        engineering_team = Team(
            name="Platform Architecture & Engineering",
            description="Core infrastructure and platform architecture decision unit"
        )
        product_team = Team(
            name="Product Strategy & UX",
            description="Product roadmap, specifications, and design choices"
        )
        governance_team = Team(
            name="Executive Governance & Risk",
            description="Strategic decisions, compliance, and enterprise oversight"
        )
        core_arch_team = Team(
            name="Core Architecture & Engineering Leadership",
            description="Cross-functional technical leadership directing enterprise system architecture, cloud platforms, infrastructure resilience, and security compliance."
        )
        db.add_all([engineering_team, product_team, governance_team, core_arch_team])
        db.commit()
        db.refresh(engineering_team)
        db.refresh(product_team)
        db.refresh(governance_team)
        db.refresh(core_arch_team)

        # Seed Users for every Role (supporting both @expert.com and @decisionreplay.com)
        default_users = [
            # Core Engineering Leadership Team (Karuna, Karan, Hasan, Gopi, Sree, Madhu)
            User(
                email="karuna@expert.com",
                hashed_password=get_password_hash("Password123!"),
                full_name="Karunakara Amaravathi",
                role=RoleEnum.EMPLOYEE,
                team_id=core_arch_team.id,
                is_active=True
            ),
            User(
                email="karan@expert.com",
                hashed_password=get_password_hash("Password123!"),
                full_name="Karan Saini",
                role=RoleEnum.REVIEWER,
                team_id=core_arch_team.id,
                is_active=True
            ),
            User(
                email="hasan@expert.com",
                hashed_password=get_password_hash("Password123!"),
                full_name="Mohd Hasan Rizvi",
                role=RoleEnum.REVIEWER,
                team_id=core_arch_team.id,
                is_active=True
            ),
            User(
                email="gopi@expert.com",
                hashed_password=get_password_hash("Password123!"),
                full_name="Gopinath Venkat",
                role=RoleEnum.MANAGER,
                team_id=core_arch_team.id,
                is_active=True
            ),
            User(
                email="sree@expert.com",
                hashed_password=get_password_hash("Password123!"),
                full_name="Sreeram Krishnamurthy",
                role=RoleEnum.EMPLOYEE,
                team_id=core_arch_team.id,
                is_active=True
            ),
            User(
                email="madhu@expert.com",
                hashed_password=get_password_hash("Password123!"),
                full_name="Madhusudhan Rao",
                role=RoleEnum.ADMINISTRATOR,
                team_id=core_arch_team.id,
                is_active=True
            ),
            # Expert accounts (Used in Quick Login & Verification Script)
            User(
                email="admin@expert.com",
                hashed_password=get_password_hash("AdminPassword123!"),
                full_name="Sarah Connor (Administrator)",
                role=RoleEnum.ADMINISTRATOR,
                team_id=governance_team.id,
                is_active=True
            ),
            User(
                email="manager@expert.com",
                hashed_password=get_password_hash("ManagerPassword123!"),
                full_name="Alex Mercer (Engineering Manager)",
                role=RoleEnum.MANAGER,
                team_id=engineering_team.id,
                is_active=True
            ),
            User(
                email="reviewer@expert.com",
                hashed_password=get_password_hash("ReviewerPassword123!"),
                full_name="Elena Vance (Senior Reviewer)",
                role=RoleEnum.REVIEWER,
                team_id=product_team.id,
                is_active=True
            ),
            User(
                email="employee@expert.com",
                hashed_password=get_password_hash("EmployeePassword123!"),
                full_name="Karunakara.A (Staff Engineer)",
                role=RoleEnum.EMPLOYEE,
                team_id=core_arch_team.id,
                is_active=True
            ),
            # DecisionReplay accounts
            User(
                email="admin@decisionreplay.com",
                hashed_password=get_password_hash("Admin@123"),
                full_name="System Administrator",
                role=RoleEnum.ADMINISTRATOR,
                team_id=governance_team.id,
                is_active=True
            ),
            User(
                email="manager@decisionreplay.com",
                hashed_password=get_password_hash("Manager@123"),
                full_name="Platform Manager",
                role=RoleEnum.MANAGER,
                team_id=engineering_team.id,
                is_active=True
            ),
        ]
        db.add_all(default_users)
        db.commit()
        print("Database initialized and seeded with default teams and role accounts.")

    # Seed Sample Decisions if empty
    if db.query(Decision).count() == 0:
        admin_user = db.query(User).filter(User.email == "admin@expert.com").first()
        manager_user = db.query(User).filter(User.email == "manager@expert.com").first()
        reviewer_user = db.query(User).filter(User.email == "reviewer@expert.com").first()
        employee_user = db.query(User).filter(User.email == "employee@expert.com").first()
        creator_id = admin_user.id if admin_user else 1

        d1 = Decision(
            title="Migration from Monolith to Event-Driven Microservices Architecture",
            problem_statement="The legacy monolith is experiencing tight coupling, deployment bottlenecks, and scaling limitations during peak traffic events. We need a decoupled event-driven architecture.",
            category="Architecture",
            status=DecisionStatus.APPROVED,
            created_by_id=creator_id
        )
        d2 = Decision(
            title="Primary Database Selection: PostgreSQL vs MongoDB for Decision Graph Store",
            problem_statement="Evaluating relational schema stability vs document flexibility for complex decision replay snapshots and audit histories across microservices.",
            category="Data & Storage",
            status=DecisionStatus.UNDER_REVIEW,
            created_by_id=manager_user.id if manager_user else creator_id
        )
        d3 = Decision(
            title="Zero Trust Enterprise Authentication & SSO Integration",
            problem_statement="Standardizing identity access management, JWT token rotation, and Role-Based Access Control (RBAC) across organizational units.",
            category="Security",
            status=DecisionStatus.DRAFT,
            created_by_id=employee_user.id if employee_user else creator_id
        )
        d4 = Decision(
            title="Public Cloud Cold Storage Tier Migration without At-Rest HSM Encryption",
            problem_statement="Cost reduction initiative proposing migration of archived artifacts to commodity cold tier without dedicated cloud hardware security module encryption keys.",
            category="Compliance",
            status=DecisionStatus.REJECTED,
            created_by_id=employee_user.id if employee_user else creator_id
        )
        db.add_all([d1, d2, d3, d4])
        db.commit()
        db.refresh(d1)
        db.refresh(d2)
        db.refresh(d3)
        db.refresh(d4)

        # Seed Alternatives for d1
        alt1 = Alternative(
            decision_id=d1.id,
            title="Event-Driven Microservices with Kafka & FastAPI",
            description="Asynchronous microservices utilizing Apache Kafka for event bus streaming and FastAPI for lightweight REST endpoints.",
            pros=json.dumps(["High throughput and horizontal scaling", "Independent service deployment cycles", "Fault isolation across boundaries"]),
            cons=json.dumps(["Eventual consistency management complexity", "Higher operational infrastructure overhead"]),
            estimated_cost=45000.0,
            feasibility_score=9,
            risk_assessment="Low to Moderate risk. Team has strong Python/FastAPI expertise."
        )
        alt2 = Alternative(
            decision_id=d1.id,
            title="Modular Monolith with Redis Caching",
            description="Refactoring monolith into strict domain boundary modules inside a single deployment unit backed by Redis pub/sub.",
            pros=json.dumps(["Lower initial migration cost", "Simpler debugging and deployment"]),
            cons=json.dumps(["Does not eliminate single point of deployment failure", "Limited long-term horizontal scaling"]),
            estimated_cost=15000.0,
            feasibility_score=7,
            risk_assessment="Low risk in short term, but high technical debt risk in 2+ years."
        )

        # Seed Alternatives for d2
        alt3 = Alternative(
            decision_id=d2.id,
            title="PostgreSQL 16 with JSONB Support",
            description="Relational database foundation with JSONB document columns for audit snapshots.",
            pros=json.dumps(["Strict ACID compliance for audit trails", "High-performance JSON indexing"]),
            cons=json.dumps(["Schema migrations required for relational column updates"]),
            estimated_cost=12000.0,
            feasibility_score=9,
            risk_assessment="Very low risk. Industry standard."
        )
        alt4 = Alternative(
            decision_id=d2.id,
            title="MongoDB Atlas Cloud",
            description="Fully managed document store for unstructured decision payloads.",
            pros=json.dumps(["Native document hierarchy", "Flexible schema evolution"]),
            cons=json.dumps(["Higher cloud subscription cost", "No native cross-document transactions"]),
            estimated_cost=22000.0,
            feasibility_score=8,
            risk_assessment="Moderate cost risk over time."
        )
        db.add_all([alt1, alt2, alt3, alt4])
        db.commit()

        # Seed Comments for d1
        c1 = Comment(
            decision_id=d1.id,
            author_id=reviewer_user.id if reviewer_user else creator_id,
            comment_type=CommentType.MEETING_NOTE,
            content="Architecture Review Board meeting sync completed. Kafka event bus approved for microservice messaging."
        )
        c2 = Comment(
            decision_id=d1.id,
            author_id=creator_id,
            comment_type=CommentType.RATIONALE,
            content="Event-driven architecture chosen due to high throughput benchmark results and clean separation of concerns."
        )
        db.add_all([c1, c2])
        db.commit()

        # Seed Initial Version Snapshot for d1
        snap_data = json.dumps({
            "id": d1.id,
            "title": d1.title,
            "problem_statement": d1.problem_statement,
            "category": d1.category,
            "status": d1.status.value,
            "created_by_id": d1.created_by_id
        })
        v1 = DecisionVersion(
            decision_id=d1.id,
            version_number=1,
            snapshot_data=snap_data,
            changed_by_id=creator_id,
            change_summary="Initial decision formulation and baseline snapshot"
        )
        db.add(v1)
        db.commit()

        # Seed Milestone 3: Multi-Level Approvals & History
        if reviewer_user and manager_user:
            # d1: Passed Level 1 and Level 2 -> Approved
            app1_l1 = Approval(
                decision_id=d1.id,
                approver_id=reviewer_user.id,
                level=1,
                status=ApprovalStatus.APPROVED,
                comments="Technical feasibility review completed. Event-driven architecture verified."
            )
            app1_l2 = Approval(
                decision_id=d1.id,
                approver_id=manager_user.id,
                level=2,
                status=ApprovalStatus.APPROVED,
                comments="Budget and engineering capacity approved for Phase 1 implementation."
            )
            db.add_all([app1_l1, app1_l2])

            hist1 = ApprovalHistory(
                decision_id=d1.id,
                approver_id=creator_id,
                level=1,
                action="SUBMITTED",
                comments="Initial submission for architecture board review."
            )
            hist2 = ApprovalHistory(
                decision_id=d1.id,
                approver_id=reviewer_user.id,
                level=1,
                action="APPROVED",
                comments="Level 1 approved."
            )
            hist3 = ApprovalHistory(
                decision_id=d1.id,
                approver_id=manager_user.id,
                level=2,
                action="APPROVED",
                comments="Final Level 2 Manager approval granted."
            )
            db.add_all([hist1, hist2, hist3])

            # d2: Under Review at Level 1
            app2_l1 = Approval(
                decision_id=d2.id,
                approver_id=reviewer_user.id,
                level=1,
                status=ApprovalStatus.PENDING,
                comments=None
            )
            db.add(app2_l1)
            hist4 = ApprovalHistory(
                decision_id=d2.id,
                approver_id=manager_user.id,
                level=1,
                action="SUBMITTED",
                comments="Submitted for database technology review."
            )
            db.add(hist4)

            # d4: Rejected at Level 1
            app4_l1 = Approval(
                decision_id=d4.id,
                approver_id=reviewer_user.id,
                level=1,
                status=ApprovalStatus.REJECTED,
                comments="Rejected: Non-compliant with ISO 27001 data sovereignty requirements."
            )
            db.add(app4_l1)
            hist5 = ApprovalHistory(
                decision_id=d4.id,
                approver_id=reviewer_user.id,
                level=1,
                action="REJECTED",
                comments="Rejected: Non-compliant with ISO 27001 data sovereignty requirements."
            )
            db.add(hist5)

            # Seed Notifications
            n1 = Notification(
                user_id=reviewer_user.id,
                title="Review Requested",
                message=f"'{d2.title}' is awaiting your Level 1 review.",
                type=NotificationType.APPROVAL_REQUEST.value,
                link=f"/decisions/{d2.id}",
                is_read=False
            )
            n2 = Notification(
                user_id=manager_user.id,
                title="SLA Alert",
                message=f"Decision '{d2.title}' pending review in your team queue.",
                type=NotificationType.ESCALATION.value,
                link=f"/decisions/{d2.id}",
                is_read=False
            )
            n3 = Notification(
                user_id=creator_id,
                title="Decision Approved",
                message=f"'{d1.title}' has received final organizational approval.",
                type=NotificationType.DECISION_UPDATE.value,
                link=f"/decisions/{d1.id}",
                is_read=True
            )
            db.add_all([n1, n2, n3])

            # Seed Audit Logs
            log1 = AuditLog(
                user_id=creator_id,
                action="SUBMIT",
                resource_type="DECISION",
                resource_id=str(d1.id),
                details=json.dumps({"action": "Submission for review", "level": 1}),
                ip_address="127.0.0.1"
            )
            log2 = AuditLog(
                user_id=manager_user.id,
                action="APPROVE",
                resource_type="APPROVAL",
                resource_id=str(d1.id),
                details=json.dumps({"level": 2, "status": "Approved"}),
                ip_address="127.0.0.1"
            )
            log3 = AuditLog(
                user_id=reviewer_user.id,
                action="REJECT",
                resource_type="DECISION",
                resource_id=str(d4.id),
                details=json.dumps({"reason": "Compliance failure"}),
                ip_address="127.0.0.1"
            )
            db.add_all([log1, log2, log3])

        db.commit()
        print("Seeded Milestone 3 sample decisions, multi-level approvals, notifications, and audit logs.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables and seed data
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_initial_data(db)
    finally:
        db.close()
    yield
    # Shutdown logic if needed


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Backend API for the Expert Decision Replay Platform - Milestone 1, 2 & 3",
    lifespan=lifespan
)

# Configure CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(users.router, prefix=settings.API_V1_STR)
app.include_router(teams.router, prefix=settings.API_V1_STR)
app.include_router(decisions.router, prefix=settings.API_V1_STR)
app.include_router(discussions.router, prefix=settings.API_V1_STR)
app.include_router(alternatives.router, prefix=settings.API_V1_STR)
app.include_router(attachments.router, prefix=settings.API_V1_STR)
app.include_router(notifications.router, prefix=settings.API_V1_STR)
app.include_router(audit.router, prefix=settings.API_V1_STR)
app.include_router(dashboards.router, prefix=settings.API_V1_STR)
app.include_router(reports.router, prefix=settings.API_V1_STR)


@app.get("/")
def root():
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "operational",
        "docs_url": "/docs",
        "api_v1": settings.API_V1_STR
    }


@app.get(f"{settings.API_V1_STR}/health")
def health_check():
    return {"status": "healthy", "database": "connected"}
