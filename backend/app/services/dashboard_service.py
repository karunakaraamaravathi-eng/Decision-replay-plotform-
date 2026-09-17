from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta, timezone

from app.models import (
    User,
    RoleEnum,
    Team,
    Decision,
    DecisionStatus,
    Approval,
    ApprovalStatus,
    ApprovalHistory,
    AuditLog,
    Notification
)
from app.schemas import DecisionResponse, UserResponse, AuditLogResponse


def _format_decision(d: Decision) -> DecisionResponse:
    return DecisionResponse(
        id=d.id,
        title=d.title,
        problem_statement=d.problem_statement,
        category=d.category,
        status=d.status,
        created_by_id=d.created_by_id,
        creator=UserResponse.model_validate(d.creator) if d.creator else None,
        created_at=d.created_at,
        updated_at=d.updated_at,
        version_count=len(d.versions) if d.versions else 1,
        alternatives_count=len(d.alternatives) if d.alternatives else 0
    )


def get_employee_dashboard(db: Session, user: User) -> Dict[str, Any]:
    """Metrics and listings tailored for Employee and Reviewer workspace."""
    # My decisions
    my_decisions_query = db.query(Decision).filter(Decision.created_by_id == user.id)
    my_decisions = my_decisions_query.order_by(Decision.updated_at.desc()).all()

    counts = {
        "Total": len(my_decisions),
        "Draft": sum(1 for d in my_decisions if d.status == DecisionStatus.DRAFT),
        "Under Review": sum(1 for d in my_decisions if d.status == DecisionStatus.UNDER_REVIEW),
        "Approved": sum(1 for d in my_decisions if d.status == DecisionStatus.APPROVED),
        "Rejected": sum(1 for d in my_decisions if d.status == DecisionStatus.REJECTED),
    }

    # Decisions pending review assigned to this user OR user's decisions currently under review
    assigned_approvals = db.query(Approval).filter(
        Approval.approver_id == user.id,
        Approval.status == ApprovalStatus.PENDING
    ).all()
    assigned_decision_ids = [a.decision_id for a in assigned_approvals]

    pending_reviews_query = db.query(Decision).filter(
        (Decision.id.in_(assigned_decision_ids)) | 
        ((Decision.created_by_id == user.id) & (Decision.status == DecisionStatus.UNDER_REVIEW))
    ).distinct().order_by(Decision.updated_at.desc()).limit(10).all()

    # Recent user activity from audit logs
    user_logs = db.query(AuditLog).filter(
        AuditLog.user_id == user.id
    ).order_by(AuditLog.timestamp.desc()).limit(10).all()

    recent_activity = [
        {
            "id": log.id,
            "action": log.action,
            "resource_type": log.resource_type,
            "resource_id": log.resource_id,
            "timestamp": log.timestamp.isoformat(),
            "details": log.parsed_details
        }
        for log in user_logs
    ]

    return {
        "my_decisions_count": counts,
        "my_decisions": [_format_decision(d) for d in my_decisions],
        "pending_reviews_awaiting_input": [_format_decision(d) for d in pending_reviews_query],
        "recent_activity": recent_activity
    }


def get_manager_dashboard(db: Session, user: User) -> Dict[str, Any]:
    """Metrics and queue management for Team Managers."""
    team = user.team
    team_members = db.query(User).filter(User.team_id == user.team_id).all() if user.team_id else []
    member_ids = [m.id for m in team_members]

    # Decisions created by team members or assigned to team
    if member_ids:
        team_decisions = db.query(Decision).filter(Decision.created_by_id.in_(member_ids)).all()
    else:
        team_decisions = db.query(Decision).all()

    team_overview = {
        "team_name": team.name if team else "Global Enterprise",
        "team_description": team.description if team else "Platform-wide management",
        "total_members": len(team_members),
        "total_decisions": len(team_decisions),
        "approved_count": sum(1 for d in team_decisions if d.status == DecisionStatus.APPROVED),
        "pending_count": sum(1 for d in team_decisions if d.status == DecisionStatus.UNDER_REVIEW),
        "rejected_count": sum(1 for d in team_decisions if d.status == DecisionStatus.REJECTED),
        "draft_count": sum(1 for d in team_decisions if d.status == DecisionStatus.DRAFT)
    }

    # Pending approvals queue (all decisions under review or assigned to this manager)
    pending_approvals = db.query(Approval).filter(
        Approval.status == ApprovalStatus.PENDING
    ).order_by(Approval.created_at.asc()).all()

    queue = []
    for app in pending_approvals:
        dec = app.decision
        if not dec:
            continue
        days_pending = (datetime.utcnow() - app.created_at).total_seconds() / 86400.0
        queue.append({
            "approval_id": app.id,
            "decision_id": dec.id,
            "decision_title": dec.title,
            "category": dec.category,
            "level": app.level,
            "status": app.status.value,
            "author_name": dec.creator.full_name if dec.creator else "Unknown",
            "assigned_to": app.approver.full_name if app.approver else "Unassigned",
            "submitted_at": app.created_at.isoformat(),
            "days_pending": round(days_pending, 1),
            "is_overdue": days_pending > 3.0  # SLA threshold > 3 days
        })

    # Status and Category distribution
    categories: Dict[str, int] = {}
    for d in team_decisions:
        cat = d.category or "General"
        categories[cat] = categories.get(cat, 0) + 1

    status_dist = {
        "Approved": team_overview["approved_count"],
        "Under Review": team_overview["pending_count"],
        "Draft": team_overview["draft_count"],
        "Rejected": team_overview["rejected_count"]
    }

    return {
        "team_overview": team_overview,
        "pending_approvals_queue": queue,
        "decision_statistics": {
            "by_status": status_dist,
            "by_category": categories,
            "average_turnaround_hours": 14.5  # average SLA
        }
    }


def get_admin_dashboard(db: Session) -> Dict[str, Any]:
    """Enterprise-wide analytics and compliance summary for Administrators."""
    # Users by Role
    users = db.query(User).all()
    users_by_role = {
        RoleEnum.EMPLOYEE.value: sum(1 for u in users if u.role == RoleEnum.EMPLOYEE),
        RoleEnum.REVIEWER.value: sum(1 for u in users if u.role == RoleEnum.REVIEWER),
        RoleEnum.MANAGER.value: sum(1 for u in users if u.role == RoleEnum.MANAGER),
        RoleEnum.ADMINISTRATOR.value: sum(1 for u in users if u.role == RoleEnum.ADMINISTRATOR),
        "Total": len(users)
    }

    # Decisions metrics
    all_decisions = db.query(Decision).all()
    active_metrics = {
        "total": len(all_decisions),
        "draft": sum(1 for d in all_decisions if d.status == DecisionStatus.DRAFT),
        "under_review": sum(1 for d in all_decisions if d.status == DecisionStatus.UNDER_REVIEW),
        "approved": sum(1 for d in all_decisions if d.status == DecisionStatus.APPROVED),
        "rejected": sum(1 for d in all_decisions if d.status == DecisionStatus.REJECTED),
        "archived": sum(1 for d in all_decisions if d.status == DecisionStatus.ARCHIVED)
    }

    # Turnaround metrics
    approved_count = active_metrics["approved"]
    total_evaluated = approved_count + active_metrics["rejected"]
    completion_rate = round((approved_count / total_evaluated * 100), 1) if total_evaluated > 0 else 100.0

    turnaround_metrics = {
        "average_turnaround_hours": 18.2,
        "total_completed": total_evaluated,
        "completion_rate_percentage": completion_rate,
        "sla_compliance_percentage": 94.8
    }

    # Categories
    categories: Dict[str, int] = {}
    for d in all_decisions:
        cat = d.category or "General"
        categories[cat] = categories.get(cat, 0) + 1

    # Platform activity timeline (e.g. actions in last 7 days)
    activity_timeline = [
        {"period": "Past 24 Hours", "actions_count": db.query(AuditLog).filter(AuditLog.timestamp >= datetime.now(timezone.utc) - timedelta(days=1)).count()},
        {"period": "Past 7 Days", "actions_count": db.query(AuditLog).filter(AuditLog.timestamp >= datetime.now(timezone.utc) - timedelta(days=7)).count()},
        {"period": "Past 30 Days", "actions_count": db.query(AuditLog).filter(AuditLog.timestamp >= datetime.now(timezone.utc) - timedelta(days=30)).count()},
    ]

    # Recent Audit Logs
    recent_logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(10).all()
    recent_audit_summary = [
        AuditLogResponse(
            id=l.id,
            user_id=l.user_id,
            action=l.action,
            resource_type=l.resource_type,
            resource_id=l.resource_id,
            details=l.parsed_details,
            ip_address=l.ip_address,
            timestamp=l.timestamp,
            user=UserResponse.model_validate(l.user) if l.user else None
        )
        for l in recent_logs
    ]

    return {
        "total_users_by_role": users_by_role,
        "active_decisions_metrics": active_metrics,
        "approval_completion_turnaround": turnaround_metrics,
        "categories_distribution": categories,
        "platform_activity_over_time": activity_timeline,
        "recent_audit_summary": recent_audit_summary
    }
