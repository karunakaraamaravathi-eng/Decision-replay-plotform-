from fastapi import APIRouter

router = APIRouter(prefix="/wireframes", tags=["Milestone 1 Specification"])

@router.get("/requirements")
def get_requirements():
    """Return structured project requirement analysis."""
    return {
        "title": "Expert Decision Replay Platform",
        "objective": "Develop a centralized platform that records important organizational decisions, including problem statement, alternatives, evaluation criteria, risks, discussions, approvals, and outcomes.",
        "outcomes": [
            "Centralized decision management platform",
            "Secure authentication and role-based access control (RBAC)",
            "Structured decision creation workflows",
            "Multi-level approval process",
            "Discussion and collaboration modules",
            "Complete decision history and audit logs",
            "Organizational decision analytics",
            "Docker and cloud deployment"
        ],
        "milestones": [
            {
                "name": "Milestone 1 (Week 1-2)",
                "status": "COMPLETED",
                "tasks": [
                    "Requirement analysis",
                    "Database design (SQLAlchemy ORM)",
                    "UI wireframes specification",
                    "FastAPI backend setup",
                    "Web UI Frontend SPA",
                    "JWT Authentication",
                    "User Management & Role-Based Access"
                ]
            },
            {
                "name": "Milestone 2 (Week 3-4)",
                "status": "UPCOMING",
                "tasks": [
                    "Decision management module",
                    "Alternative comparison matrix",
                    "File attachments",
                    "Discussion threads",
                    "Version tracking"
                ]
            },
            {
                "name": "Milestone 3 (Week 5-6)",
                "status": "UPCOMING",
                "tasks": [
                    "Approval workflows",
                    "Notifications system",
                    "Audit logging & security reports",
                    "Analytics & Dashboards"
                ]
            },
            {
                "name": "Milestone 4 (Week 7-8)",
                "status": "UPCOMING",
                "tasks": [
                    "Testing & Bug fixing",
                    "Docker containerization",
                    "Final documentation & GitHub submission"
                ]
            }
        ]
    }

@router.get("/db-schema")
def get_db_schema():
    """Return database ER schema structure."""
    return {
        "tables": [
            {
                "name": "users",
                "columns": ["id (PK)", "email (Unique)", "hashed_password", "full_name", "role", "department", "team_id (FK)", "is_active", "created_at"],
                "roles": ["Administrator", "Manager", "Reviewer", "Employee"]
            },
            {
                "name": "teams",
                "columns": ["id (PK)", "name (Unique)", "description", "manager_id (FK)", "created_at"]
            },
            {
                "name": "decisions",
                "columns": ["id (PK)", "title", "problem_statement", "category", "status", "creator_id (FK)", "team_id (FK)", "version", "created_at", "updated_at"]
            },
            {
                "name": "alternatives",
                "columns": ["id (PK)", "decision_id (FK)", "title", "description", "pros", "cons", "estimated_cost", "risk_level", "feasibility_score"]
            },
            {
                "name": "approval_workflows",
                "columns": ["id (PK)", "decision_id (FK)", "reviewer_id (FK)", "level", "status", "comments", "updated_at"]
            },
            {
                "name": "audit_logs",
                "columns": ["id (PK)", "user_id (FK)", "action", "entity_type", "entity_id", "details", "timestamp"]
            }
        ]
    }

@router.get("/ui-specs")
def get_ui_specs():
    """Return UI Wireframe layout specifications."""
    return {
        "screens": [
            {
                "id": "auth-screen",
                "name": "Authentication (Login/Register)",
                "description": "JWT-backed login/registration form with rapid role switcher for quick testing."
            },
            {
                "id": "admin-dashboard",
                "name": "Administrator Dashboard",
                "description": "User management grid, role updates, system stats overview, and real-time audit logs."
            },
            {
                "id": "manager-dashboard",
                "name": "Manager Dashboard",
                "description": "Team management overview, pending team decisions, and department metrics."
            },
            {
                "id": "reviewer-dashboard",
                "name": "Reviewer Dashboard",
                "description": "Queue of pending decision reviews, evaluation checklists, and decision approval actions."
            },
            {
                "id": "employee-dashboard",
                "name": "Employee Dashboard",
                "description": "Personal decision submissions, draft decisions, and team decision activity stream."
            },
            {
                "id": "wireframe-explorer",
                "name": "Wireframe & DB Schema Visualizer",
                "description": "Interactive visual view of Milestone 1 requirements, database tables, and architecture data flow."
            }
        ]
    }
