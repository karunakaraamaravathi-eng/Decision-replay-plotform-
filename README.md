# 🧠 Expert Decision Replay Platform

> **Enterprise Platform for Capturing, Governing, Replaying, and Auditing High-Impact Organizational Decisions.**

![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-009688?logo=fastapi&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12-3776AB?logo=python&logoColor=white)
![React](https://img.shields.io/badge/React-18.2-61DAFB?logo=react&logoColor=black)
![Vite](https://img.shields.io/badge/Vite-5.4-646CFF?logo=vite&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?logo=docker&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL%20%2F%20SQLite-336791?logo=postgresql&logoColor=white)
![Nginx](https://img.shields.io/badge/Reverse%20Proxy-Nginx-009639?logo=nginx&logoColor=white)
![Security](https://img.shields.io/badge/Security-RBAC%20%26%20Audit%20Trail-success)

---

## 🏛️ Platform Architecture & Milestones Overview

```text
===================================================================================================
                       EXPERT DECISION REPLAY PLATFORM ARCHITECTURE
===================================================================================================
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│ MILESTONE 1: AUTHENTICATION & RBAC GOVERNANCE                                                   │
├─────────────────────────────────────────────────────────────────────────────────────────────────┤
│  • JWT Bearer Authentication (Passlib & PyJWT)                                                  │
│  • Role-Based Access Control: ADMINISTRATOR, MANAGER, REVIEWER, EMPLOYEE                       │
│  • User Management, Account Activation, & Multi-Team Organizational Structuring                 │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                │
                                                ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│ MILESTONE 2: DECISION ENGINE, VERSIONING & TRADEOFF MATRIX                                      │
├─────────────────────────────────────────────────────────────────────────────────────────────────┤
│  • Decision Lifecycle (Draft, Under Review, Approved, Rejected, Archived)                       │
│  • Automated Version Snapshotting (v1 -> v2 -> v3 immutable change audit trail)                 │
│  • Side-by-Side Alternatives Comparison Matrix (Pros/Cons, Feasibility, Cost & Metrics)         │
│  • Threaded Discussion Engine (General Comments, Meeting Notes, Rationale Tags)                │
│  • File Attachment & Artifact Management (Upload, Validate, Download)                           │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                │
                                                ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│ MILESTONE 3: APPROVAL PIPELINE, NOTIFICATIONS, AUDIT LOGS & REPORTING                           │
├─────────────────────────────────────────────────────────────────────────────────────────────────┤
│  • Multi-Level Verification: Tier 1 (Technical Verification) -> Tier 2 (Managerial Approval)    │
│  • Interactive Terminal CLI (In-browser & native python cli.py management suite)                │
│  • Real-Time Notification Center with live unread badge counters                                │
│  • Comprehensive Audit Log Trail tracking mutations with IP, actors & diffs                    │
│  • Enterprise Report Generation (Downloadable PDF & Excel workbooks)                            │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                │
                                                ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│ MILESTONE 4: DOCKERIZATION & ENTERPRISE PRODUCTION CONTAINERIZATION                             │
├─────────────────────────────────────────────────────────────────────────────────────────────────┤
│  • Multi-Stage Production Dockerfiles for Frontend (Vite -> Nginx) & Backend (FastAPI Python)   │
│  • Docker Compose Orchestration: PostgreSQL 16 Alpine + FastAPI + Nginx Reverse Proxy           │
│  • Automated Volume Persistence (PostgreSQL DB, File Uploads) & Health Checks                   │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
===================================================================================================
```

---

## 🐳 Quick Docker Deployment (Production Ready)

Deploy the entire enterprise stack (PostgreSQL, FastAPI Backend, React Frontend & Nginx Proxy) in a single command:

### 1. Launch with Docker Compose
```bash
# Windows / Linux / macOS
cd backend/docker
docker compose up --build -d
```
*(On Windows, you can also run **`backend/docker/docker-run.bat`**).*

### 2. Access the Live Platform
- **Web Application**: [`http://localhost:5173`](http://localhost:5173) or [`http://localhost`](http://localhost)
- **FastAPI Backend API**: [`http://localhost:8000`](http://localhost:8000)
- **Interactive Swagger Docs**: [`http://localhost:8000/docs`](http://localhost:8000/docs)
- **PostgreSQL Database**: `localhost:5432`

### 3. Container Management
```bash
# View live container logs
docker compose logs -f

# Stop and remove containers
docker compose down

# Stop and purge all data volumes
docker compose down -v
```

---

## 💻 Local Development Setup (Without Docker)

If you prefer running without Docker on your local workstation:

### 1-Click Batch Launcher (Windows)
Run the launcher script:
👉 **`backend/scripts/run_all.bat`** (or `./run_all.bat` locally)

---

### Manual Multi-Terminal Launch

#### Step 1: Backend Setup (FastAPI)
```bash
cd backend
python -m venv venv

# Windows:
.\venv\Scripts\Activate.ps1
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

#### Step 2: Frontend Setup (React + Vite)
```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at [`http://localhost:5173`](http://localhost:5173).

---

## 🔑 Pre-Configured Demo Accounts

| Role | Email | Password | Primary Workflow |
| :--- | :--- | :--- | :--- |
| **Staff Engineer** | `employee@expert.com` | `EmployeePassword123!` | Create & submit decisions, compare alternatives, in-browser CLI |
| **Engineering Manager** | `manager@expert.com` | `ManagerPassword123!` | Level 2 executive approvals, pending queues, SLA reports |
| **Senior Reviewer** | `reviewer@expert.com` | `ReviewerPassword123!` | Level 1 technical verification, review discussions |
| **Administrator** | `admin@expert.com` | `AdminPassword123!` | User management, RBAC governance, security audit logs |

---

## 🖥️ Command-Line Management Suite (`cli.py`)

A native terminal CLI is provided in the `backend/` directory:

```bash
# Inspect platform and database status
python backend/cli.py status

# List architectural decisions
python backend/cli.py decisions list

# Inspect decision details
python backend/cli.py decisions show 1

# Approve a decision tier
python backend/cli.py approve 1 --notes "Architecture verified and stress-tested"

# Reject a decision with mandatory rationale
python backend/cli.py reject 1 --reason "Alternative benchmarks required"

# Escalate a blocked decision
python backend/cli.py escalate 1 --reason "Critical production blocker"

# Inspect immutable audit trails
python backend/cli.py audit tail -n 15

# Re-seed database with clean demo data
python backend/cli.py seed
```

---

## 🌐 Application Routing Guide

| Module / Screen | URL Path | Description | Access Control |
| :--- | :--- | :--- | :--- |
| 🔑 **Authentication** | `/login` | Public login portal with 1-click test fillers | Public |
| 📊 **Dashboard** | `/dashboard` | Role-tailored operational KPIs and active queues | Authenticated |
| 🧠 **Decisions Directory** | `/decisions` | Filterable decision tracker (Category, Status, Author) | Authenticated |
| 🔍 **Decision Detail View** | `/decisions/{id}` | Version snapshots, trade-off matrix, discussions, approvals | Authenticated |
| 💻 **Terminal CLI** | `/terminal` | Interactive in-browser Unix-style governance shell | Authenticated |
| 📑 **Reports Center** | `/reports` | Export decisions, approval SLAs, and audit logs to PDF/Excel | Authenticated |
| 🏢 **Teams Workspace** | `/teams` | Department directory and team allocations | Authenticated |
| 🛡️ **User Administration** | `/admin/users` | RBAC management panel & account activation | Admin Only |
| 📖 **Swagger API Docs** | `http://localhost:8000/docs` | Interactive OpenAPI documentation and test runner | Developers |

---

## 🛡️ Complete REST API Surface

### 🔐 Authentication (`/api/v1/auth`)
- `POST /api/v1/auth/register` - Account registration
- `POST /api/v1/auth/login` - Authenticate and receive JWT token
- `GET /api/v1/auth/me` - Profile of authenticated user

### 👥 User & Role Administration (`/api/v1/users`)
- `GET /api/v1/users` - Search and list users
- `GET /api/v1/users/{id}` - Get user details
- `PUT /api/v1/users/{id}` - Update user profile
- `PUT /api/v1/users/{id}/role` - Assign role (*Admin only*)
- `PUT /api/v1/users/{id}/status` - Activate / Deactivate user (*Admin only*)

### 🏢 Teams (`/api/v1/teams`)
- `GET /api/v1/teams` - List organizational teams
- `POST /api/v1/teams` - Create team (*Manager / Admin only*)

### 🧠 Decisions Engine & Versioning (`/api/v1/decisions`)
- `POST /api/v1/decisions` - Create decision & initialize Version 1
- `GET /api/v1/decisions` - Filterable decision listing
- `GET /api/v1/decisions/{id}` - Complete decision aggregate view
- `PUT /api/v1/decisions/{id}` - Update decision & create new version snapshot
- `GET /api/v1/decisions/{id}/versions` - Version snapshot history

### 📊 Alternatives & Comparison Matrix (`/api/v1/decisions/{id}/alternatives`)
- `POST /api/v1/decisions/{id}/alternatives` - Add alternative option
- `GET /api/v1/decisions/{id}/alternatives` - List alternatives
- `GET /api/v1/decisions/{id}/alternatives/compare` - Get comparison trade-off matrix
- `PUT /api/v1/decisions/{id}/alternatives/{alt_id}` - Update alternative
- `DELETE /api/v1/decisions/{id}/alternatives/{alt_id}` - Delete alternative

### 💬 Threaded Discussions (`/api/v1/decisions/{id}/comments`)
- `POST /api/v1/decisions/{id}/comments` - Add comment/reply (*general_comment*, *meeting_note*, *rationale*)
- `GET /api/v1/decisions/{id}/comments` - Hierarchical comment tree
- `DELETE /api/v1/decisions/{id}/comments/{comment_id}` - Remove comment

### 📎 Document Attachments (`/api/v1/decisions/{id}/attachments`)
- `POST /api/v1/decisions/{id}/attachments` - Multipart file upload
- `GET /api/v1/decisions/{id}/attachments` - List attached documents
- `GET /api/v1/decisions/{id}/attachments/{att_id}/download` - Download document

### ⚡ Approval Workflows (`/api/v1/approvals`)
- `POST /api/v1/approvals/decisions/{id}/submit` - Submit draft for review
- `POST /api/v1/approvals/decisions/{id}/approve` - Approve current level
- `POST /api/v1/approvals/decisions/{id}/reject` - Reject with mandatory notes
- `POST /api/v1/approvals/decisions/{id}/escalate` - Escalate to higher authority
- `GET /api/v1/approvals/decisions/{id}/history` - Step-by-step approval audit trail
- `GET /api/v1/approvals/pending` - Pending approval queue for current user

### 🔔 Notifications (`/api/v1/notifications`)
- `GET /api/v1/notifications` - Get user notifications (read/unread)
- `PUT /api/v1/notifications/{id}/read` - Mark single notification as read
- `PUT /api/v1/notifications/read-all` - Mark all notifications as read

### 📜 Audit Logs (`/api/v1/audit`)
- `GET /api/v1/audit/logs` - Query compliance audit events with pagination and filters
- `GET /api/v1/audit/resources/{type}/{id}` - Full lifecycle change history of an entity

### 📊 Dashboards (`/api/v1/dashboards`)
- `GET /api/v1/dashboards/stats` - Role-aware dashboard analytics and metrics

### 📑 Reports & Exports (`/api/v1/reports`)
- `GET /api/v1/reports/decisions/pdf` - Export decisions registry as PDF
- `GET /api/v1/reports/decisions/excel` - Export decisions registry as Excel (.xlsx)
- `GET /api/v1/reports/approvals/sla` - Export approval SLAs and turnaround times
- `GET /api/v1/reports/audit/pdf` - Export compliance audit history report

---

## 🧪 Testing & Verification

```bash
# Run unit and integration tests
$env:PYTHONPATH="backend"
python -m pytest backend/tests/

# Run end-to-end verification script
python test_output.py
```
