#!/usr/bin/env python
"""
Seed script to establish the Core Architecture & Engineering Leadership Team
with professional engineering personas: Karuna, Karan, Hasan, Gopi, Sree, and Madhu.
"""
import sys
from pathlib import Path
from datetime import datetime, timezone

# Ensure backend directory is in sys.path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from app.database import SessionLocal, engine, Base
from app.models import (
    User,
    Team,
    RoleEnum,
    Decision,
    DecisionStatus,
    DecisionVersion,
    Alternative,
    Comment,
    CommentType,
    Approval,
    ApprovalHistory,
    ApprovalStatus,
    AuditLog,
    AuditAction,
    AuditResourceType,
    Notification,
    NotificationType
)
from app.auth import get_password_hash


def seed_team_and_members():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        print("[*] Checking / Creating Core Architecture & Engineering Leadership Team...")
        
        team_name = "Core Architecture & Engineering Leadership"
        team = db.query(Team).filter(Team.name == team_name).first()
        if not team:
            team = Team(
                name=team_name,
                description="Cross-functional technical leadership directing enterprise system architecture, cloud platforms, infrastructure resilience, and security compliance."
            )
            db.add(team)
            db.commit()
            db.refresh(team)
            print(f" -> Created team: {team.name} (ID: {team.id})")
        else:
            print(f" -> Existing team found: {team.name} (ID: {team.id})")

        # 6 Professional Team Members
        members_spec = [
            {
                "email": "karuna@expert.com",
                "full_name": "Karunakara Amaravathi",
                "role": RoleEnum.EMPLOYEE,
                "title": "Principal Systems Architect"
            },
            {
                "email": "karan@expert.com",
                "full_name": "Karan Saini",
                "role": RoleEnum.REVIEWER,
                "title": "Lead Cloud Solutions Architect"
            },
            {
                "email": "hasan@expert.com",
                "full_name": "Mohd Hasan Rizvi",
                "role": RoleEnum.REVIEWER,
                "title": "Senior DevOps & Platform Engineer"
            },
            {
                "email": "gopi@expert.com",
                "full_name": "Gopinath Venkat",
                "role": RoleEnum.MANAGER,
                "title": "Principal Security & Governance Manager"
            },
            {
                "email": "sree@expert.com",
                "full_name": "Sreeram Krishnamurthy",
                "role": RoleEnum.EMPLOYEE,
                "title": "Staff Data & Storage Architect"
            },
            {
                "email": "madhu@expert.com",
                "full_name": "Madhusudhan Rao",
                "role": RoleEnum.ADMINISTRATOR,
                "title": "Director of Enterprise Engineering"
            }
        ]

        user_map = {}
        for spec in members_spec:
            user = db.query(User).filter(User.email == spec["email"]).first()
            if not user:
                user = User(
                    email=spec["email"],
                    hashed_password=get_password_hash("Password123!"),
                    full_name=spec["full_name"],
                    role=spec["role"],
                    team_id=team.id,
                    is_active=True
                )
                db.add(user)
                db.commit()
                db.refresh(user)
                print(f" -> Created member: {user.full_name} ({user.email}) - {spec['role'].value}")
            else:
                user.team_id = team.id
                user.role = spec["role"]
                user.full_name = spec["full_name"]
                db.commit()
                db.refresh(user)
                print(f" -> Updated member: {user.full_name} ({user.email})")
            user_map[spec["email"]] = user

        # Also ensure existing employee@expert.com is assigned to this team
        existing_emp = db.query(User).filter(User.email == "employee@expert.com").first()
        if existing_emp:
            existing_emp.team_id = team.id
            existing_emp.full_name = "Karunakara.A (Principal Systems Architect)"
            db.commit()

        # Seed sample decisions authored by team members to enrich dashboard analytics & charts
        sample_decisions = [
            {
                "title": "Global Multi-Region Active-Active RTO Strategy",
                "problem": "Current single-region deployment risks multi-hour outages during provider connectivity failures.",
                "category": "Cloud Infrastructure",
                "status": DecisionStatus.UNDER_REVIEW,
                "author": user_map["karuna@expert.com"],
                "approver": user_map["karan@expert.com"],
                "manager": user_map["gopi@expert.com"],
                "step": 1
            },
            {
                "title": "Zero Trust Service Mesh Implementation with Envoy",
                "problem": "East-west microservice traffic requires mutual TLS, automated certificate rotation, and RBAC authorization.",
                "category": "Security & Identity",
                "status": DecisionStatus.APPROVED,
                "author": user_map["hasan@expert.com"],
                "approver": user_map["karan@expert.com"],
                "manager": user_map["gopi@expert.com"],
                "step": 2
            },
            {
                "title": "Distributed Transaction Isolation: Dual Write vs Outbox Pattern",
                "problem": "Microservices producing payment and order events occasionally encounter dual-write inconsistencies.",
                "category": "Architecture Patterns",
                "status": DecisionStatus.APPROVED,
                "author": user_map["sree@expert.com"],
                "approver": user_map["hasan@expert.com"],
                "manager": user_map["madhu@expert.com"],
                "step": 2
            },
            {
                "title": "Automated Ephemeral Developer Sandbox Environments",
                "problem": "Engineers spend 2+ hours setting up local stacks, blocking onboarding velocity.",
                "category": "Developer Experience",
                "status": DecisionStatus.DRAFT,
                "author": user_map["karan@expert.com"],
                "approver": None,
                "manager": None,
                "step": 0
            },
            {
                "title": "Synchronous Distributed ACID Locking over WebSocket",
                "problem": "Attempt to enforce distributed ACID state across stateful websocket clients.",
                "category": "Reliability Engineering",
                "status": DecisionStatus.REJECTED,
                "author": user_map["sree@expert.com"],
                "approver": user_map["karuna@expert.com"],
                "manager": user_map["gopi@expert.com"],
                "step": 1
            }
        ]

        for item in sample_decisions:
            existing_dec = db.query(Decision).filter(Decision.title == item["title"]).first()
            if not existing_dec:
                dec = Decision(
                    title=item["title"],
                    problem_statement=item["problem"],
                    category=item["category"],
                    status=item["status"],
                    created_by_id=item["author"].id
                )
                db.add(dec)
                db.commit()
                db.refresh(dec)

                # Snapshot Version 1
                import json
                ver = DecisionVersion(
                    decision_id=dec.id,
                    version_number=1,
                    snapshot_data=json.dumps({
                        "title": dec.title,
                        "problem_statement": dec.problem_statement,
                        "category": dec.category,
                        "status": dec.status.value
                    }),
                    changed_by_id=item["author"].id,
                    change_summary="Initial formal architectural formulation"
                )
                db.add(ver)

                # Audit log
                log = AuditLog(
                    user_id=item["author"].id,
                    action=AuditAction.CREATE,
                    resource_type=AuditResourceType.DECISION,
                    resource_id=dec.id,
                    ip_address="127.0.0.1",
                    details=f'{{"title": "{dec.title}", "author": "{item["author"].full_name}"}}'
                )
                db.add(log)

                # Approval records
                if item["approver"] and item["status"] in [DecisionStatus.UNDER_REVIEW, DecisionStatus.APPROVED, DecisionStatus.REJECTED]:
                    app_status = ApprovalStatus.APPROVED if item["status"] == DecisionStatus.APPROVED else (
                        ApprovalStatus.REJECTED if item["status"] == DecisionStatus.REJECTED else ApprovalStatus.PENDING
                    )
                    approval = Approval(
                        decision_id=dec.id,
                        approver_id=item["approver"].id,
                        level=item["step"],
                        status=app_status
                    )
                    db.add(approval)
                    db.commit()

                    hist = ApprovalHistory(
                        decision_id=dec.id,
                        approver_id=item["approver"].id,
                        level=item["step"],
                        action="APPROVED" if app_status == ApprovalStatus.APPROVED else ("REJECTED" if app_status == ApprovalStatus.REJECTED else "SUBMITTED"),
                        comments="Formal architectural review decision recorded."
                    )
                    db.add(hist)

                db.commit()
                print(f" -> Created decision: {dec.title} ({dec.status.value})")

        print("\n[SUCCESS] Core Architecture & Engineering Leadership Team and 6 members successfully seeded!")
    finally:
        db.close()


if __name__ == "__main__":
    seed_team_and_members()
