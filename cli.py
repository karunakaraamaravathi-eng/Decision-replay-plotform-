#!/usr/bin/env python
"""
Expert Decision Replay Platform - Terminal CLI
A unified terminal management interface for running the platform, managing approval workflows,
inspecting audit logs, generating compliance reports, and seeding demo data.
"""

import sys
import os
import argparse
import subprocess
from pathlib import Path

# Add backend directory to sys.path so we can import app modules directly
ROOT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = ROOT_DIR / "backend"
FRONTEND_DIR = ROOT_DIR / "frontend"
sys.path.insert(0, str(BACKEND_DIR))

from app.database import SessionLocal, engine
from app.models import Decision, User, Approval, ApprovalHistory, AuditLog, Notification, RoleEnum
from app.services import approval_service, audit_service, report_service


def cmd_status(args):
    """Check platform and database health."""
    db = SessionLocal()
    try:
        users_count = db.query(User).count()
        decisions_count = db.query(Decision).count()
        approvals_count = db.query(Approval).count()
        audit_count = db.query(AuditLog).count()
        notifications_count = db.query(Notification).count()

        print("=================================================================")
        print("  EXPERT DECISION REPLAY PLATFORM - SYSTEM STATUS")
        print("=================================================================")
        print(f" Database:      {engine.url}")
        print(f" Total Users:   {users_count}")
        print(f" Decisions:     {decisions_count}")
        print(f" Approvals:     {approvals_count}")
        print(f" Audit Events:  {audit_count}")
        print(f" Notifications: {notifications_count}")
        print(" Status:        HEALTHY / ONLINE")
        print("=================================================================")
    finally:
        db.close()


def cmd_decisions_list(args):
    """List decisions in a formatted table."""
    db = SessionLocal()
    try:
        decisions = db.query(Decision).order_by(Decision.id.asc()).all()
        if not decisions:
            print("No decisions found in system.")
            return

        print(f"{'ID':<5} {'STATUS':<15} {'LVL':<5} {'CATEGORY':<18} {'AUTHOR':<15} {'TITLE'}")
        print("-" * 80)
        for d in decisions:
            creator_name = d.creator.full_name if d.creator else f"User #{d.created_by_id}"
            title = (d.title[:30] + "...") if len(d.title) > 30 else d.title
            pending_app = next((a for a in d.approvals if a.status.value == "PENDING"), None)
            lvl = pending_app.level if pending_app else (d.approvals[-1].level if d.approvals else 1)
            status_val = d.status.value if hasattr(d.status, 'value') else str(d.status)
            print(f"#{d.id:<4} {status_val:<15} {lvl:<5} {d.category:<18} {creator_name:<15} {title}")
    finally:
        db.close()


def cmd_decisions_show(args):
    """Show details of a single decision."""
    db = SessionLocal()
    try:
        d = db.query(Decision).filter(Decision.id == args.id).first()
        if not d:
            print(f"[ERROR] Decision #{args.id} not found.")
            return

        print("=================================================================")
        print(f" DECISION #{d.id}: {d.title}")
        status_val = d.status.value if hasattr(d.status, 'value') else str(d.status)
        pending_app = next((a for a in d.approvals if a.status.value == "PENDING"), None)
        lvl = pending_app.level if pending_app else (d.approvals[-1].level if d.approvals else 1)
        print(f" Status:        {status_val} (Current Level: {lvl})")
        print(f" Category:      {d.category}")
        print(f" Created:       {d.created_at}")
        print(f" Author:        {d.creator.full_name if d.creator else d.created_by_id}")
        print("\n PROBLEM STATEMENT:")
        print(f" {d.problem_statement}")
        print("\n EVALUATED ALTERNATIVES:")
        for alt in d.alternatives:
            print(f"  - Option: {alt.title} | Feasibility: {alt.feasibility_score}/10 | Est Cost: ${alt.estimated_cost:,}")
        print("\n APPROVALS QUEUE:")
        for app in d.approvals:
            approver_name = app.approver.full_name if app.approver else "Unassigned"
            print(f"  - Level {app.level}: {app.status} by {approver_name} ({app.comments or 'No comments'})")
    finally:
        db.close()


def cmd_workflow_approve(args):
    """Approve a decision."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.role.in_([RoleEnum.MANAGER, RoleEnum.REVIEWER, RoleEnum.ADMINISTRATOR])).first()
        if not user:
            print("[ERROR] No authorized user found for approval.")
            return

        res = approval_service.advance_approval(
            db=db,
            decision_id=args.id,
            approver=user,
            comments=args.notes or "Approved via CLI Terminal"
        )
        print(f"[SUCCESS] Decision #{args.id} approved at Level {res.level}.")
        print(f"Outcome: Status is now '{res.decision_status}'.")
    finally:
        db.close()


def cmd_workflow_reject(args):
    """Reject a decision."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.role.in_([RoleEnum.MANAGER, RoleEnum.REVIEWER, RoleEnum.ADMINISTRATOR])).first()
        if not user:
            print("[ERROR] No authorized user found.")
            return

        res = approval_service.reject_approval(
            db=db,
            decision_id=args.id,
            approver=user,
            comments=args.reason
        )
        print(f"[REJECTED] Decision #{args.id} rejected. Reason: '{args.reason}'. Status: '{res.decision_status}'.")
    finally:
        db.close()


def cmd_workflow_escalate(args):
    """Escalate a decision."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.role.in_([RoleEnum.MANAGER, RoleEnum.REVIEWER, RoleEnum.ADMINISTRATOR])).first()
        if not user:
            print("[ERROR] No authorized user found.")
            return

        res = approval_service.escalate_approval(
            db=db,
            decision_id=args.id,
            approver=user,
            comments=args.reason
        )
        print(f"[ESCALATED] Decision #{args.id} escalated. Reason: '{args.reason}'. Current Level: {res.level}.")
    finally:
        db.close()


def cmd_audit_tail(args):
    """Tail recent audit logs."""
    db = SessionLocal()
    try:
        logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(args.n).all()
        print(f"{'TIMESTAMP':<22} {'ACTION':<10} {'RESOURCE':<12} {'RES_ID':<8} {'USER_ID':<8} {'IP'}")
        print("-" * 80)
        for l in reversed(logs):
            ts = l.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            act = l.action.value if hasattr(l.action, 'value') else str(l.action)
            res = l.resource_type.value if hasattr(l.resource_type, 'value') else str(l.resource_type)
            print(f"{ts:<22} {act:<10} {res:<12} #{str(l.resource_id):<7} #{str(l.user_id):<7} {l.ip_address or '127.0.0.1'}")
    finally:
        db.close()


def cmd_seed(args):
    """Seed Milestone 1, 2, and 3 data."""
    print("Running Milestone 3 database seeding script...")
    seed_script = BACKEND_DIR / "seed_milestone3.py"
    subprocess.run([sys.executable, str(seed_script)], check=True)


def cmd_run(args):
    """Start both FastAPI and Vite servers."""
    print("Starting backend and frontend services...")
    run_bat = ROOT_DIR / "run_all.bat"
    if sys.platform == "win32" and run_bat.exists():
        subprocess.run(["cmd.exe", "/c", str(run_bat)])
    else:
        print("Please start servers using start_backend.bat and start_frontend.bat")


def main():
    parser = argparse.ArgumentParser(
        description="Expert Decision Replay Platform - Terminal CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python cli.py status
  python cli.py decisions list
  python cli.py decisions show 1
  python cli.py approve 1 --notes "Architecture looks solid"
  python cli.py reject 1 --reason "Need benchmark testing against alternatives"
  python cli.py audit tail -n 15
  python cli.py seed
  python cli.py run
"""
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # status
    subparsers.add_parser("status", help="Display platform & database operational health")

    # decisions
    dec_parser = subparsers.add_parser("decisions", help="Manage and inspect architectural decisions")
    dec_sub = dec_parser.add_subparsers(dest="subcommand")
    dec_sub.add_parser("list", help="List all decisions")
    show_p = dec_sub.add_parser("show", help="Show decision details")
    show_p.add_argument("id", type=int, help="Decision ID")

    # approve
    app_p = subparsers.add_parser("approve", help="Approve decision at current verification tier")
    app_p.add_argument("id", type=int, help="Decision ID to approve")
    app_p.add_argument("--notes", type=str, default="Approved via CLI", help="Approval rationale")

    # reject
    rej_p = subparsers.add_parser("reject", help="Reject decision with mandatory rationale")
    rej_p.add_argument("id", type=int, help="Decision ID to reject")
    rej_p.add_argument("--reason", type=str, required=True, help="Mandatory rejection rationale")

    # escalate
    esc_p = subparsers.add_parser("escalate", help="Escalate decision with urgency flag")
    esc_p.add_argument("id", type=int, help="Decision ID to escalate")
    esc_p.add_argument("--reason", type=str, required=True, help="Reason for escalation")

    # audit
    audit_p = subparsers.add_parser("audit", help="Audit log inspection")
    audit_sub = audit_p.add_subparsers(dest="subcommand")
    tail_p = audit_sub.add_parser("tail", help="Tail recent audit records")
    tail_p.add_argument("-n", type=int, default=10, help="Number of records to display")

    # seed
    subparsers.add_parser("seed", help="Seed platform with demo users, decisions, and workflows")

    # run
    subparsers.add_parser("run", help="Launch backend and frontend dev servers")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    if args.command == "status":
        cmd_status(args)
    elif args.command == "decisions":
        if args.subcommand == "show":
            cmd_decisions_show(args)
        else:
            cmd_decisions_list(args)
    elif args.command == "approve":
        cmd_workflow_approve(args)
    elif args.command == "reject":
        cmd_workflow_reject(args)
    elif args.command == "escalate":
        cmd_workflow_escalate(args)
    elif args.command == "audit":
        cmd_audit_tail(args)
    elif args.command == "seed":
        cmd_seed(args)
    elif args.command == "run":
        cmd_run(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
