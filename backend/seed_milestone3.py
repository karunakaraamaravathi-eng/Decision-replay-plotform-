"""
Seed script for Milestone 3 (Weeks 5-6) of the Expert Decision Replay Platform.
Populates:
- Core role-based users and teams
- Decisions in Draft, Under Review, Approved, and Rejected states
- Evaluated alternatives and threaded discussion comments
- Multi-level approval chains (Level 1 Reviewer -> Level 2 Manager)
- Approval history audit trails
- In-app notification queues for employees, reviewers, managers, and admins
- Audit logs capturing system compliance and user activity events
"""
import sys
import os
import json
from datetime import datetime, timedelta

# Ensure backend root is on PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, Base, SessionLocal
from app.models import (
    User,
    Team,
    RoleEnum,
    Decision,
    DecisionStatus,
    Alternative,
    Comment,
    CommentType,
    DecisionVersion,
    Approval,
    ApprovalHistory,
    ApprovalStatus,
    Notification,
    AuditLog,
    NotificationType,
    AuditAction,
    AuditResourceType,
    utc_now
)
from app.auth import get_password_hash


def seed():
    print("Resetting and initializing database schema for Milestone 3...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Clear existing tables for fresh deterministic state if desired
        db.query(ApprovalHistory).delete()
        db.query(Approval).delete()
        db.query(Notification).delete()
        db.query(AuditLog).delete()
        db.query(Comment).delete()
        db.query(Alternative).delete()
        db.query(DecisionVersion).delete()
        db.query(Decision).delete()
        db.query(User).delete()
        db.query(Team).delete()
        db.commit()

        print("Creating Teams...")
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
        db.add_all([engineering_team, product_team, governance_team])
        db.commit()

        print("Creating Users for all roles...")
        users = [
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
                team_id=engineering_team.id,
                is_active=True
            ),
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
        db.add_all(users)
        db.commit()

        admin_u = db.query(User).filter(User.email == "admin@expert.com").first()
        mgr_u = db.query(User).filter(User.email == "manager@expert.com").first()
        rev_u = db.query(User).filter(User.email == "reviewer@expert.com").first()
        emp_u = db.query(User).filter(User.email == "employee@expert.com").first()

        print("Creating Decisions with Multi-Status Lifecycle...")
        # 1. Approved Decision (Passed L1 Reviewer + L2 Manager)
        d1 = Decision(
            title="Migration from Monolith to Event-Driven Microservices Architecture",
            problem_statement="The legacy monolithic application suffers from deployment bottlenecks, resource contention, and scaling issues during peak transactions. An event-driven microservices pattern with Apache Kafka is required to ensure independent service elasticity.",
            category="Architecture",
            status=DecisionStatus.APPROVED,
            created_by_id=emp_u.id
        )

        # 2. Under Review Decision (Level 1 Reviewer pending)
        d2 = Decision(
            title="Primary Database Selection: PostgreSQL vs MongoDB for Decision Graph Store",
            problem_statement="Evaluating relational schema stability with JSONB capabilities versus native document flexibility for versioned decision replay snapshots and compliance audit trails.",
            category="Data & Storage",
            status=DecisionStatus.UNDER_REVIEW,
            created_by_id=emp_u.id
        )

        # 3. Draft Decision
        d3 = Decision(
            title="Zero Trust Enterprise Authentication & SSO Integration",
            problem_statement="Standardizing organization-wide identity access management, JWT token rotation policies, and strict Role-Based Access Control (RBAC) across distributed services.",
            category="Security",
            status=DecisionStatus.DRAFT,
            created_by_id=emp_u.id
        )

        # 4. Rejected Decision (Violated compliance requirements)
        d4 = Decision(
            title="Public Cloud Cold Storage Tier Migration without At-Rest HSM Encryption",
            problem_statement="Cost reduction initiative proposing migration of historical compliance artifacts to commodity unencrypted cloud cold tier buckets.",
            category="Compliance",
            status=DecisionStatus.REJECTED,
            created_by_id=emp_u.id
        )

        db.add_all([d1, d2, d3, d4])
        db.commit()
        db.refresh(d1)
        db.refresh(d2)
        db.refresh(d3)
        db.refresh(d4)

        print("Adding Alternatives & Trade-off scoring...")
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

        print("Adding Discussion Comments & Version Snapshots...")
        c1 = Comment(
            decision_id=d1.id,
            author_id=rev_u.id,
            comment_type=CommentType.MEETING_NOTE,
            content="Architecture Review Board meeting sync completed. Kafka event bus approved for microservice messaging."
        )
        c2 = Comment(
            decision_id=d1.id,
            author_id=emp_u.id,
            comment_type=CommentType.RATIONALE,
            content="Event-driven architecture chosen due to high throughput benchmark results and clean separation of concerns."
        )
        db.add_all([c1, c2])

        v1 = DecisionVersion(
            decision_id=d1.id,
            version_number=1,
            snapshot_data=json.dumps({
                "id": d1.id,
                "title": d1.title,
                "problem_statement": d1.problem_statement,
                "category": d1.category,
                "status": d1.status.value,
                "created_by_id": d1.created_by_id
            }),
            changed_by_id=emp_u.id,
            change_summary="Initial formulation and proposal"
        )
        db.add(v1)
        db.commit()

        print("Adding Multi-Level Approvals & History Chains...")
        # d1 Approvals: Level 1 Reviewer Approved + Level 2 Manager Approved
        app1_l1 = Approval(
            decision_id=d1.id,
            approver_id=rev_u.id,
            level=1,
            status=ApprovalStatus.APPROVED,
            comments="Architecture design validated against decoupling requirements. Passed Level 1.",
            created_at=utc_now() - timedelta(days=5),
            updated_at=utc_now() - timedelta(days=4)
        )
        app1_l2 = Approval(
            decision_id=d1.id,
            approver_id=mgr_u.id,
            level=2,
            status=ApprovalStatus.APPROVED,
            comments="Budget allocation approved. Ready for Q3 production execution.",
            created_at=utc_now() - timedelta(days=4),
            updated_at=utc_now() - timedelta(days=3)
        )
        db.add_all([app1_l1, app1_l2])

        hist1 = ApprovalHistory(
            decision_id=d1.id,
            approver_id=emp_u.id,
            level=1,
            action="SUBMITTED",
            comments="Decision formulated and submitted for architectural review.",
            created_at=utc_now() - timedelta(days=5)
        )
        hist2 = ApprovalHistory(
            decision_id=d1.id,
            approver_id=rev_u.id,
            level=1,
            action="APPROVED",
            comments="Level 1 technical validation passed.",
            created_at=utc_now() - timedelta(days=4)
        )
        hist3 = ApprovalHistory(
            decision_id=d1.id,
            approver_id=mgr_u.id,
            level=2,
            action="APPROVED",
            comments="Level 2 executive manager approval granted.",
            created_at=utc_now() - timedelta(days=3)
        )
        db.add_all([hist1, hist2, hist3])

        # d2 Approvals: Level 1 Pending
        app2_l1 = Approval(
            decision_id=d2.id,
            approver_id=rev_u.id,
            level=1,
            status=ApprovalStatus.PENDING,
            comments=None,
            created_at=utc_now() - timedelta(days=1)
        )
        db.add(app2_l1)
        hist4 = ApprovalHistory(
            decision_id=d2.id,
            approver_id=emp_u.id,
            level=1,
            action="SUBMITTED",
            comments="Submitted for database technology evaluation.",
            created_at=utc_now() - timedelta(days=1)
        )
        db.add(hist4)

        # d4 Approvals: Level 1 Rejected
        app4_l1 = Approval(
            decision_id=d4.id,
            approver_id=rev_u.id,
            level=1,
            status=ApprovalStatus.REJECTED,
            comments="Rejected due to enterprise compliance failure: Unencrypted cold storage violates ISO 27001 policies.",
            created_at=utc_now() - timedelta(days=2),
            updated_at=utc_now() - timedelta(days=1)
        )
        db.add(app4_l1)
        hist5 = ApprovalHistory(
            decision_id=d4.id,
            approver_id=rev_u.id,
            level=1,
            action="REJECTED",
            comments="Rejected: ISO 27001 data sovereignty violations.",
            created_at=utc_now() - timedelta(days=1)
        )
        db.add(hist5)

        print("Generating Notifications...")
        notifications = [
            Notification(
                user_id=rev_u.id,
                title="Level 1 Review Required",
                message=f"'{d2.title}' has been assigned to you for technical verification.",
                type=NotificationType.APPROVAL_REQUEST.value,
                link=f"/decisions/{d2.id}",
                is_read=False,
                created_at=utc_now() - timedelta(hours=8)
            ),
            Notification(
                user_id=mgr_u.id,
                title="Review Queue SLA Alert",
                message=f"1 decision in your team queue is approaching turnaround SLA.",
                type=NotificationType.ESCALATION.value,
                link=f"/decisions/{d2.id}",
                is_read=False,
                created_at=utc_now() - timedelta(hours=4)
            ),
            Notification(
                user_id=emp_u.id,
                title="Decision Approved",
                message=f"'{d1.title}' has received final Level 2 approval.",
                type=NotificationType.DECISION_UPDATE.value,
                link=f"/decisions/{d1.id}",
                is_read=True,
                created_at=utc_now() - timedelta(days=3)
            ),
            Notification(
                user_id=emp_u.id,
                title="Decision Rejected",
                message=f"'{d4.title}' was rejected during Level 1 review: ISO 27001 non-compliance.",
                type=NotificationType.DECISION_UPDATE.value,
                link=f"/decisions/{d4.id}",
                is_read=False,
                created_at=utc_now() - timedelta(days=1)
            ),
            Notification(
                user_id=admin_u.id,
                title="Monthly Compliance Audit Ready",
                message="System audit logs and turnaround metrics generated for executive review.",
                type=NotificationType.SYSTEM.value,
                link="/reports",
                is_read=False,
                created_at=utc_now() - timedelta(hours=1)
            ),
        ]
        db.add_all(notifications)

        print("Generating Audit Logs...")
        logs = [
            AuditLog(
                user_id=emp_u.id,
                action="CREATE",
                resource_type="DECISION",
                resource_id=str(d1.id),
                details=json.dumps({"title": d1.title, "category": d1.category}),
                ip_address="192.168.1.10",
                timestamp=utc_now() - timedelta(days=6)
            ),
            AuditLog(
                user_id=emp_u.id,
                action="SUBMIT",
                resource_type="DECISION",
                resource_id=str(d1.id),
                details=json.dumps({"assigned_level": 1, "reviewer": rev_u.full_name}),
                ip_address="192.168.1.10",
                timestamp=utc_now() - timedelta(days=5)
            ),
            AuditLog(
                user_id=rev_u.id,
                action="APPROVE",
                resource_type="APPROVAL",
                resource_id=str(d1.id),
                details=json.dumps({"level": 1, "status": "APPROVED", "comments": "Level 1 verified"}),
                ip_address="192.168.1.15",
                timestamp=utc_now() - timedelta(days=4)
            ),
            AuditLog(
                user_id=mgr_u.id,
                action="APPROVE",
                resource_type="DECISION",
                resource_id=str(d1.id),
                details=json.dumps({"level": 2, "final_status": "Approved", "budget_approved": True}),
                ip_address="192.168.1.20",
                timestamp=utc_now() - timedelta(days=3)
            ),
            AuditLog(
                user_id=emp_u.id,
                action="SUBMIT",
                resource_type="DECISION",
                resource_id=str(d2.id),
                details=json.dumps({"assigned_level": 1, "reviewer": rev_u.full_name}),
                ip_address="192.168.1.10",
                timestamp=utc_now() - timedelta(days=1)
            ),
            AuditLog(
                user_id=rev_u.id,
                action="REJECT",
                resource_type="DECISION",
                resource_id=str(d4.id),
                details=json.dumps({"level": 1, "reason": "ISO 27001 compliance violation"}),
                ip_address="192.168.1.15",
                timestamp=utc_now() - timedelta(days=1)
            ),
            AuditLog(
                user_id=admin_u.id,
                action="EXPORT",
                resource_type="REPORT",
                resource_id="decisions_pdf",
                details=json.dumps({"format": "pdf", "total_records": 4}),
                ip_address="192.168.1.2",
                timestamp=utc_now() - timedelta(hours=2)
            ),
        ]
        db.add_all(logs)

        db.commit()
        print("Successfully seeded Milestone 3 database!")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    seed()
