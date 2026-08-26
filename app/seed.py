from sqlalchemy.orm import Session
from app.models import User, Team, AuditLog
from app.auth import hash_password

def seed_database(db: Session):
    """Seed default teams, users across all 4 roles, and audit logs."""
    
    # Check if database already seeded
    if db.query(User).first():
        print("[SEED] Database already populated. Skipping initial seed.")
        return

    print("[SEED] Seeding initial database records...")

    # 1. Create Core Teams
    team_eng = Team(name="Core Architecture Team", description="Handles core platform design and architecture standards.")
    team_devops = Team(name="DevOps & Infrastructure", description="Manages deployment, containers, and cloud infrastructure.")
    team_security = Team(name="Security & Compliance", description="Oversees audit logs, RBAC, and system security.")
    
    db.add_all([team_eng, team_devops, team_security])
    db.commit()

    # Refresh teams to get IDs
    db.refresh(team_eng)
    db.refresh(team_devops)
    db.refresh(team_security)

    # 2. Create Users for all 4 Roles
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

    # 3. Create Sample Audit Log Entries
    audit_logs = [
        AuditLog(user_id=1, action="SYSTEM_INIT", entity_type="System", entity_id=1, details="Initial Milestone 1 platform setup completed."),
        AuditLog(user_id=1, action="USER_CREATE", entity_type="User", entity_id=2, details="Created Manager user account: manager@expert.org"),
        AuditLog(user_id=2, action="TEAM_CREATE", entity_type="Team", entity_id=1, details="Initialized Core Architecture Team")
    ]

    db.add_all(audit_logs)
    db.commit()

    print("[SEED] Seeding completed successfully!")
