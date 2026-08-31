# 🗄️ SQLite Database Snapshot (`decision_replay.db`)
**File Size:** 106496 bytes | **Tables:** 9

> This document is automatically generated to view SQLite database tables directly in your text editor.

## Table: `USERS` (5 records)
| id | email | hashed_password | full_name | role | department | is_active | created_at | team_id |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | admin@expert.org | 264d45508f712121fbedacaf6a37e9fb679a40fa2024e080896ba881e2a24b5a | Alice Vance (System Administrator) | Administrator | IT Operations | 1 | 2026-08-31 13:01:05.996533 | 3 |
| 2 | manager@expert.org | 91e19553358292f55fbb6cc36fe0a64b393a8a1eade4c661baf76438b0ea680c | Bob Miller (Engineering Manager) | Manager | Engineering | 1 | 2026-08-31 13:01:05.996540 | 1 |
| 3 | reviewer@expert.org | adec71175932afa67909047339f083f547bc5c6d6dd4b976f7058300cfe8e6f7 | Carol Smith (Senior Reviewer) | Reviewer | Architecture Review Board | 1 | 2026-08-31 13:01:05.996542 | 1 |
| 4 | employee@expert.org | b0da5dd3680031077f00dcbafe35e9c028305caed6831d7859d60afb55aa6860 | David Chen (Software Engineer) | Employee | Engineering | 1 | 2026-08-31 13:01:05.996544 | 1 |
| 5 | infra.lead@expert.org | 54727db1c247adf32340faea39471ba5e3785fa81f7ebaaf73314fb549368a93 | Eva Green (DevOps Lead) | Manager | Infrastructure | 1 | 2026-08-31 13:01:05.996546 | 2 |


## Table: `TEAMS` (3 records)
| id | name | description | manager_id | created_at |
| --- | --- | --- | --- | --- |
| 1 | Core Architecture Team | Handles core platform design and architecture standards. | `NULL` | 2026-08-31 13:01:05.986399 |
| 2 | DevOps & Infrastructure | Manages deployment, containers, and cloud infrastructure. | `NULL` | 2026-08-31 13:01:05.986403 |
| 3 | Security & Compliance | Oversees audit logs, RBAC, and system security. | `NULL` | 2026-08-31 13:01:05.986404 |


## Table: `DECISIONS` (3 records)
| id | title | problem_statement | category | status | rationale | creator_id | team_id | version | created_at | updated_at |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Database Engine Selection for Replay Engine | Choose between PostgreSQL and MongoDB for high-throughput decision audit logging and version timeline queries. | Architecture | Approved | PostgreSQL provides ACID compliance, strong JSONB querying capabilities, and relational integrity for multi-level approval workflows. | 2 | 1 | 2 | 2026-08-31 13:01:06.009746 | 2026-08-31 13:01:06.009752 |
| 2 | Cloud Infrastructure Deployment Model | Evaluate Docker containerization vs AWS ECS vs Serverless functions for deploying application components. | Infrastructure | Under Review | Docker containerization ensures portable local testing and simple cloud deployment via Docker Compose or Kubernetes. | 5 | 2 | 1 | 2026-08-31 13:01:06.009755 | 2026-08-31 13:01:06.009757 |
| 3 | Zero-Trust Authentication & RBAC Policy | Implement JWT with short token expiry and role-based permissions across Employee, Reviewer, Manager, and Admin roles. | Security | Approved | JWT tokens combined with FastAPI dependencies provide seamless stateless validation and granular route protection. | 1 | 3 | 1 | 2026-08-31 13:01:06.009759 | 2026-08-31 13:01:06.009760 |


## Table: `AUDIT_LOGS` (7 records)
| id | user_id | action | entity_type | entity_id | details |
| --- | --- | --- | --- | --- | --- |
| 1 | 1 | SYSTEM_INIT | System | 1 | Initial Milestone 1 & 2 platform setup completed. |
| 2 | 1 | USER_CREATE | User | 2 | Created Manager user account: manager@expert.org |
| 3 | 2 | TEAM_CREATE | Team | 1 | Initialized Core Architecture Team |
| 4 | 2 | DECISION_CREATE | Decision | 1 | Created decision 'Database Engine Selection for Replay Engine' |
| 5 | 3 | DECISION_UPDATE | Decision | 1 | Approved decision and bumped version to 2 |
| 6 | 2 | LOGIN | User | 2 | User successfully logged in |
| 7 | 2 | ATTACHMENT_UPLOAD | Decision | 1 | Uploaded file 'test_doc.txt' (61 bytes) to decision #1 |


## Table: `ALTERNATIVES` (4 records)
| id | decision_id | title | description | pros | cons | estimated_cost | risk_level | feasibility_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 1 | Option A: PostgreSQL with JSONB | Relational database with structured tables for users, teams, and JSONB fields for dynamic metadata. | ACID compliance, strict FK constraints, high performance JSON indexing, native SQL support. | Requires explicit migration scripts for schema alterations. | 150.0 | Low | 9 |
| 2 | 1 | Option B: MongoDB Enterprise | NoSQL document database holding decision objects as JSON documents. | Schemaless flexibility, rapid document prototyping. | Complex multi-table join support, weaker constraint enforcement. | 280.0 | Medium | 6 |
| 3 | 2 | Option A: Docker & FastAPI Service Containers | Package backend and web SPA into lightweight Docker containers using Uvicorn ASGI server. | Vendor-neutral, rapid local debugging, easy horizontal scaling. | Requires container orchestration setup for multi-node clusters. | 100.0 | Low | 9 |
| 4 | 2 | Option B: AWS Lambda Serverless Functions | Deconstruct API routes into AWS Lambda functions behind API Gateway. | Zero server management, automatic scaling. | Vendor lock-in, cold start latency, database connection pooling challenges. | 320.0 | High | 5 |


## Table: `DECISION_VERSIONS` (3 records)
| id | decision_id | version | title | problem_statement | category | status | rationale | change_summary | created_by_id | created_at |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 1 | 1 | Database Engine Selection for Replay Engine (Draft) | Initial draft comparing PostgreSQL and MongoDB. | Architecture | Draft | Initial evaluation phase. | Initial decision proposal created. | 2 | 2026-08-31 13:01:06.029464 |
| 2 | 1 | 2 | Database Engine Selection for Replay Engine | Choose between PostgreSQL and MongoDB for high-throughput decision audit logging and version timeline queries. | Architecture | Approved | PostgreSQL provides ACID compliance, strong JSONB querying capabilities, and relational integrity for multi-level approval workflows. | Finalized decision approval after ARB review board meeting. | 3 | 2026-08-31 13:01:06.029469 |
| 3 | 2 | 1 | Cloud Infrastructure Deployment Model | Evaluate Docker containerization vs AWS ECS vs Serverless functions for deploying application components. | Infrastructure | Under Review | Docker containerization ensures portable local testing and simple cloud deployment via Docker Compose or Kubernetes. | Initial container strategy submission. | 5 | 2026-08-31 13:01:06.029472 |


## Table: `COMMENTS` (3 records)
| id | decision_id | user_id | parent_id | content | created_at |
| --- | --- | --- | --- | --- | --- |
| 1 | 1 | 3 | `NULL` | The PostgreSQL benchmark tests showed sub-10ms response times for complex version queries. Highly recommend proceeding. | 2026-08-31 13:01:06.028653 |
| 2 | 1 | 4 | `NULL` | Agreed. SQLAlchemy ORM integrations were clean and simplified model definitions. | 2026-08-31 13:01:06.028657 |
| 3 | 2 | 2 | `NULL` | Please ensure the Dockerfile uses multi-stage builds to keep production images compact. | 2026-08-31 13:01:06.028658 |


## Table: `ATTACHMENTS` (3 records)
| id | decision_id | uploaded_by_id | filename | file_path | file_size | content_type | uploaded_at |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 1 | 2 | PostgreSQL_vs_MongoDB_Benchmark.pdf | static/uploads/decision_1_PostgreSQL_vs_MongoDB_Benchmark.pdf | 204850 | application/pdf | 2026-08-31 13:01:06.027154 |
| 2 | 2 | 5 | Architecture_Diagram_V2.png | static/uploads/decision_2_Architecture_Diagram_V2.png | 512400 | image/png | 2026-08-31 13:01:06.027158 |
| 3 | 1 | 2 | test_doc.txt | C:\Users\admin\OneDrive\Pictures\Desktop\python_proj\static\uploads\decision_1_test_doc.txt | 61 | text/plain | 2026-08-31 13:01:06.068411 |


## Table: `APPROVAL_WORKFLOWS` (0 records)
_No records in this table currently._
