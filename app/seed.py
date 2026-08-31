import os
import sys

# Ensure workspace root is in sys.path when running file directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy.orm import Session
from app.models import User, Team, AuditLog
from app.auth import hash_password

def seed_database(db: Session):
    """Seed default teams, users across all 4 roles, audit logs, decisions, alternatives, comments, and attachments."""
    from app.models import Decision
    try:
        if db.query(User).first() and db.query(Decision).first():
            print("[SEED] Database already populated with users and decisions. Skipping initial seed.")
            return
    except Exception:
        pass

    print("[SEED] Seeding initial database records...")

    # 1. Create Core Teams if not present
    team_eng = db.query(Team).filter(Team.name == "Core Architecture Team").first()
    if not team_eng:
        team_eng = Team(name="Core Architecture Team", description="Handles core platform design and architecture standards.")
        team_devops = Team(name="DevOps & Infrastructure", description="Manages deployment, containers, and cloud infrastructure.")
        team_security = Team(name="Security & Compliance", description="Oversees audit logs, RBAC, and system security.")
        
        db.add_all([team_eng, team_devops, team_security])
        db.commit()

        db.refresh(team_eng)
        db.refresh(team_devops)
        db.refresh(team_security)
    else:
        team_devops = db.query(Team).filter(Team.name == "DevOps & Infrastructure").first()
        team_security = db.query(Team).filter(Team.name == "Security & Compliance").first()

    # 2. Create Users if not present
    users = db.query(User).all()
    if not users:
        users = [
            User(
                email="admin@expert.org",
                hashed_password=hash_password("admin123"),
                full_name="Alice Vance (System Administrator)",
                role="Administrator",
                department="IT Operations",
                team_id=team_security.id
            ),
            User(
                email="manager@expert.org",
                hashed_password=hash_password("manager123"),
                full_name="Bob Miller (Engineering Manager)",
                role="Manager",
                department="Engineering",
                team_id=team_eng.id
            ),
            User(
                email="reviewer@expert.org",
                hashed_password=hash_password("reviewer123"),
                full_name="Carol Smith (Senior Reviewer)",
                role="Reviewer",
                department="Architecture Review Board",
                team_id=team_eng.id
            ),
            User(
                email="employee@expert.org",
                hashed_password=hash_password("emp123"),
                full_name="David Chen (Software Engineer)",
                role="Employee",
                department="Engineering",
                team_id=team_eng.id
            ),
            User(
                email="infra.lead@expert.org",
                hashed_password=hash_password("infra123"),
                full_name="Eva Green (DevOps Lead)",
                role="Manager",
                department="Infrastructure",
                team_id=team_devops.id
            )
        ]

        db.add_all(users)
        db.commit()
        for u in users:
            db.refresh(u)


    # 3. Seed Decisions & Milestone 2 Features
    from app.models import Decision, Alternative, DecisionVersion, Comment, Attachment

    d1 = Decision(
        title="Database Engine Selection for Replay Engine",
        problem_statement="Choose between PostgreSQL and MongoDB for high-throughput decision audit logging and version timeline queries.",
        category="Architecture",
        status="Approved",
        rationale="PostgreSQL provides ACID compliance, strong JSONB querying capabilities, and relational integrity for multi-level approval workflows.",
        creator_id=users[1].id, # Manager
        team_id=team_eng.id,
        version=2
    )

    d2 = Decision(
        title="Cloud Infrastructure Deployment Model",
        problem_statement="Evaluate Docker containerization vs AWS ECS vs Serverless functions for deploying application components.",
        category="Infrastructure",
        status="Under Review",
        rationale="Docker containerization ensures portable local testing and simple cloud deployment via Docker Compose or Kubernetes.",
        creator_id=users[4].id, # DevOps Lead
        team_id=team_devops.id,
        version=1
    )

    d3 = Decision(
        title="Zero-Trust Authentication & RBAC Policy",
        problem_statement="Implement JWT with short token expiry and role-based permissions across Employee, Reviewer, Manager, and Admin roles.",
        category="Security",
        status="Approved",
        rationale="JWT tokens combined with FastAPI dependencies provide seamless stateless validation and granular route protection.",
        creator_id=users[0].id, # Admin
        team_id=team_security.id,
        version=1
    )

    db.add_all([d1, d2, d3])
    db.commit()
    for d in [d1, d2, d3]:
        db.refresh(d)

    # 4. Alternatives for Decision 1
    alts_d1 = [
        Alternative(
            decision_id=d1.id,
            title="Option A: PostgreSQL with JSONB",
            description="Relational database with structured tables for users, teams, and JSONB fields for dynamic metadata.",
            pros="ACID compliance, strict FK constraints, high performance JSON indexing, native SQL support.",
            cons="Requires explicit migration scripts for schema alterations.",
            estimated_cost=150.0,
            risk_level="Low",
            feasibility_score=9
        ),
        Alternative(
            decision_id=d1.id,
            title="Option B: MongoDB Enterprise",
            description="NoSQL document database holding decision objects as JSON documents.",
            pros="Schemaless flexibility, rapid document prototyping.",
            cons="Complex multi-table join support, weaker constraint enforcement.",
            estimated_cost=280.0,
            risk_level="Medium",
            feasibility_score=6
        )
    ]

    # Alternatives for Decision 2
    alts_d2 = [
        Alternative(
            decision_id=d2.id,
            title="Option A: Docker & FastAPI Service Containers",
            description="Package backend and web SPA into lightweight Docker containers using Uvicorn ASGI server.",
            pros="Vendor-neutral, rapid local debugging, easy horizontal scaling.",
            cons="Requires container orchestration setup for multi-node clusters.",
            estimated_cost=100.0,
            risk_level="Low",
            feasibility_score=9
        ),
        Alternative(
            decision_id=d2.id,
            title="Option B: AWS Lambda Serverless Functions",
            description="Deconstruct API routes into AWS Lambda functions behind API Gateway.",
            pros="Zero server management, automatic scaling.",
            cons="Vendor lock-in, cold start latency, database connection pooling challenges.",
            estimated_cost=320.0,
            risk_level="High",
            feasibility_score=5
        )
    ]

    db.add_all(alts_d1 + alts_d2)

    # 5. Version History Snapshots
    v1_d1 = DecisionVersion(
        decision_id=d1.id,
        version=1,
        title="Database Engine Selection for Replay Engine (Draft)",
        problem_statement="Initial draft comparing PostgreSQL and MongoDB.",
        category="Architecture",
        status="Draft",
        rationale="Initial evaluation phase.",
        change_summary="Initial decision proposal created.",
        created_by_id=users[1].id
    )
    v2_d1 = DecisionVersion(
        decision_id=d1.id,
        version=2,
        title=d1.title,
        problem_statement=d1.problem_statement,
        category=d1.category,
        status="Approved",
        rationale=d1.rationale,
        change_summary="Finalized decision approval after ARB review board meeting.",
        created_by_id=users[2].id # Senior Reviewer
    )

    v1_d2 = DecisionVersion(
        decision_id=d2.id,
        version=1,
        title=d2.title,
        problem_statement=d2.problem_statement,
        category=d2.category,
        status=d2.status,
        rationale=d2.rationale,
        change_summary="Initial container strategy submission.",
        created_by_id=users[4].id
    )

    db.add_all([v1_d1, v2_d1, v1_d2])

    # 6. Discussion Comments
    comments = [
        Comment(
            decision_id=d1.id,
            user_id=users[2].id, # Reviewer
            content="The PostgreSQL benchmark tests showed sub-10ms response times for complex version queries. Highly recommend proceeding."
        ),
        Comment(
            decision_id=d1.id,
            user_id=users[3].id, # Employee
            content="Agreed. SQLAlchemy ORM integrations were clean and simplified model definitions."
        ),
        Comment(
            decision_id=d2.id,
            user_id=users[1].id, # Manager
            content="Please ensure the Dockerfile uses multi-stage builds to keep production images compact."
        )
    ]
    db.add_all(comments)

    # 7. Sample Attachments Metadata
    attachments = [
        Attachment(
            decision_id=d1.id,
            uploaded_by_id=users[1].id,
            filename="PostgreSQL_vs_MongoDB_Benchmark.pdf",
            file_path="static/uploads/decision_1_PostgreSQL_vs_MongoDB_Benchmark.pdf",
            file_size=204850,
            content_type="application/pdf"
        ),
        Attachment(
            decision_id=d2.id,
            uploaded_by_id=users[4].id,
            filename="Architecture_Diagram_V2.png",
            file_path="static/uploads/decision_2_Architecture_Diagram_V2.png",
            file_size=512400,
            content_type="image/png"
        )
    ]
    db.add_all(attachments)

    # 8. Sample Audit Log Entries
    audit_logs = [
        AuditLog(user_id=1, action="SYSTEM_INIT", entity_type="System", entity_id=1, details="Initial Milestone 1 & 2 platform setup completed."),
        AuditLog(user_id=1, action="USER_CREATE", entity_type="User", entity_id=2, details="Created Manager user account: manager@expert.org"),
        AuditLog(user_id=2, action="TEAM_CREATE", entity_type="Team", entity_id=1, details="Initialized Core Architecture Team"),
        AuditLog(user_id=2, action="DECISION_CREATE", entity_type="Decision", entity_id=d1.id, details=f"Created decision '{d1.title}'"),
        AuditLog(user_id=3, action="DECISION_UPDATE", entity_type="Decision", entity_id=d1.id, details="Approved decision and bumped version to 2")
    ]

    db.add_all(audit_logs)
    db.commit()

    print("[SEED] Milestone 1 & 2 Seeding completed successfully!")

if __name__ == "__main__":
    import os
    import sys
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    
    from app.database import engine, Base, SessionLocal
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_database(db)
        print("[*] Current seeded users:")
        for u in db.query(User).all():
            print(f"  - {u.full_name} ({u.role}) -> {u.email}")
    finally:
        db.close()

