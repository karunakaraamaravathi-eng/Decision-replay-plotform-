# 🗄️ SQLite Database Snapshot (`decision_replay.db`)
**File Size:** 65536 bytes | **Tables:** 6

> This document is automatically generated to view SQLite database tables directly in your text editor.

## Table: `USERS` (7 records)
| id | email | hashed_password | full_name | role | department | is_active | created_at | team_id |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | admin@expert.org | 264d45508f712121fbedacaf6a37e9fb679a40fa2024e080896ba881e2a24b5a | Alice Vance (System Administrator) | Administrator | IT Operations | 1 | 2026-08-26 16:40:12.293765 | 3 |
| 2 | manager@expert.org | 91e19553358292f55fbb6cc36fe0a64b393a8a1eade4c661baf76438b0ea680c | Bob Miller (Engineering Manager) | Manager | Engineering | 1 | 2026-08-26 16:40:12.293771 | 1 |
| 3 | reviewer@expert.org | adec71175932afa67909047339f083f547bc5c6d6dd4b976f7058300cfe8e6f7 | Carol Smith (Senior Reviewer) | Reviewer | Architecture Review Board | 1 | 2026-08-26 16:40:12.293772 | 1 |
| 4 | employee@expert.org | b0da5dd3680031077f00dcbafe35e9c028305caed6831d7859d60afb55aa6860 | David Chen (Software Engineer) | Reviewer | Engineering | 1 | 2026-08-26 16:40:12.293773 | 1 |
| 5 | infra.lead@expert.org | 54727db1c247adf32340faea39471ba5e3785fa81f7ebaaf73314fb549368a93 | Eva Green (DevOps Lead) | Manager | Infrastructure | 1 | 2026-08-26 16:40:12.293774 | 2 |
| 6 | newuser_4f03cb@expert.org | e224854ba1863857980fe914558d75d05ad651317e8fa14a48b3d271060f0b9e | New Test User | Employee | Engineering | 1 | 2026-08-26 16:40:14.696874 | `NULL` |
| 7 | pwd_test_624aa4@expert.org | 574e08fe3529c8da9089191cb88c3f8b93d8e826a09ae567c00ea880f0cb4d42 | Password Test User | Employee | Engineering | 1 | 2026-08-26 16:40:14.874129 | `NULL` |


## Table: `TEAMS` (3 records)
| id | name | description | manager_id | created_at |
| --- | --- | --- | --- | --- |
| 1 | Core Architecture Team | Handles core platform design and architecture standards. | `NULL` | 2026-08-26 16:40:12.276707 |
| 2 | DevOps & Infrastructure | Manages deployment, containers, and cloud infrastructure. | `NULL` | 2026-08-26 16:40:12.276713 |
| 3 | Security & Compliance | Oversees audit logs, RBAC, and system security. | `NULL` | 2026-08-26 16:40:12.276715 |


## Table: `DECISIONS` (0 records)
_No records in this table currently._

## Table: `AUDIT_LOGS` (14 records)
| id | user_id | action | entity_type | entity_id | details |
| --- | --- | --- | --- | --- | --- |
| 1 | 1 | SYSTEM_INIT | System | 1 | Initial Milestone 1 platform setup completed. |
| 2 | 1 | USER_CREATE | User | 2 | Created Manager user account: manager@expert.org |
| 3 | 2 | TEAM_CREATE | Team | 1 | Initialized Core Architecture Team |
| 4 | 1 | LOGIN | User | 1 | User successfully logged in |
| 5 | 6 | REGISTER | User | 6 | User registered with role: Employee |
| 6 | 2 | LOGIN | User | 2 | User successfully logged in |
| 7 | 1 | LOGIN | User | 1 | User successfully logged in |
| 8 | `NULL` | ROLE_UPDATE | User | 4 | Updated user 'employee@expert.org' role from Employee to Reviewer |
| 9 | 1 | SWAGGER_AUTH | User | 1 | Authenticated via OAuth2 Password Form |
| 10 | 3 | LOGIN | User | 3 | User successfully logged in |
| 11 | 7 | REGISTER | User | 7 | User registered with role: Employee |
| 12 | 7 | LOGIN | User | 7 | User successfully logged in |
| 13 | 7 | PASSWORD_CHANGE | User | 7 | User password changed successfully |
| 14 | 7 | LOGIN | User | 7 | User successfully logged in |


## Table: `ALTERNATIVES` (0 records)
_No records in this table currently._

## Table: `APPROVAL_WORKFLOWS` (0 records)
_No records in this table currently._
