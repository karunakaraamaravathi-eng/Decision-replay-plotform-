# Database Design & ER Specification
## Expert Decision Replay Platform

### Entity Relationship Model

```mermaid
erDiagram
    USERS ||--o{ DECISIONS : "creates"
    USERS }o--o| TEAMS : "belongs to"
    USERS ||--o{ AUDIT_LOGS : "triggers"
    TEAMS ||--o{ DECISIONS : "owns"
    DECISIONS ||--|{ ALTERNATIVES : "contains"
    DECISIONS ||--|{ APPROVAL_WORKFLOWS : "requires"

    USERS {
        int id PK
        string email UK
        string hashed_password
        string full_name
        string role
        string department
        int team_id FK
        boolean is_active
        datetime created_at
    }

    TEAMS {
        int id PK
        string name UK
        string description
        int manager_id FK
        datetime created_at
    }

    DECISIONS {
        int id PK
        string title
        text problem_statement
        string category
        string status
        int creator_id FK
        int team_id FK
        int version
        datetime created_at
        datetime updated_at
    }

    ALTERNATIVES {
        int id PK
        int decision_id FK
        string title
        text description
        text pros
        text cons
        float estimated_cost
        string risk_level
        int feasibility_score
    }

    APPROVAL_WORKFLOWS {
        int id PK
        int decision_id FK
        int reviewer_id FK
        int level
        string status
        text comments
        datetime updated_at
    }

    AUDIT_LOGS {
        int id PK
        int user_id FK
        string action
        string entity_type
        int entity_id
        text details
        datetime timestamp
    }
```

### Table Definitions & Field Types
1. **`users`**: User identity, roles (`Employee`, `Reviewer`, `Manager`, `Administrator`), and team membership.
2. **`teams`**: Organizational teams managed by department managers.
3. **`decisions`**: Core decision records with status state machine (`Draft` -> `Under Review` -> `Approved` / `Rejected` -> `Archived`).
4. **`alternatives`**: Multi-option comparisons evaluated per decision.
5. **`approval_workflows`**: Multi-tier reviewer approvals.
6. **`audit_logs`**: Immutable audit logs capturing user actions, privilege escalation, and logins.
