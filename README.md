# 🧠 Expert Decision Replay Platform

> A platform for capturing, managing, reviewing, and replaying expert decision-making processes.

![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi)
![React](https://img.shields.io/badge/React-18-61DAFB?logo=react)
![Vite](https://img.shields.io/badge/Vite-Build%20Tool-646CFF?logo=vite)
![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL%20%2F%20SQLite-336791?logo=postgresql)
![JWT](https://img.shields.io/badge/Auth-JWT%20Tokens-black?logo=jsonwebtokens)
![RBAC](https://img.shields.io/badge/Security-RBAC%20Enabled-green)

---

### Milestone 1 (Weeks 1-2): Authentication & Role-Based Access Control (RBAC)

## 🏛️ System Architecture & Roles

### User Roles (RBAC)
- **ADMINISTRATOR**: Full control over user accounts, role reassignments, and organizational governance.
- **MANAGER**: Team oversight, decision tracking, and multi-level approval workflows.
- **REVIEWER**: Alternative analysis, feasibility checks, and risk evaluation.
- **EMPLOYEE**: Standard member creating decisions, alternatives, and discussion threads.

---

## 📁 Directory Structure

```text
python_proj/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py             # App settings & JWT configuration
│   │   ├── database.py           # SQLAlchemy engine & session maker
│   │   ├── models.py             # User, Team, and RoleEnum models
│   │   ├── schemas.py            # Pydantic validation & response schemas
│   │   ├── auth.py               # Password hashing, JWT utils, RBAC guards
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py           # /auth/register, /auth/login, /auth/me
│   │   │   ├── users.py          # /users CRUD & role management
│   │   │   └── teams.py          # /teams CRUD
│   │   └── main.py               # FastAPI entry point & startup auto-seed
│   ├── .env.example
│   └── requirements.txt
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── api/
│   │   │   ├── axios.js          # Axios client with JWT interceptor
│   │   │   ├── auth.js           # Auth API service
│   │   │   ├── users.js          # User management API service
│   │   │   └── teams.js          # Teams API service
│   │   ├── components/
│   │   │   ├── Navbar.jsx        # Navigation bar with role badge & status
│   │   │   ├── ProtectedRoute.jsx# Role-based route guard
│   │   │   └── RoleBadge.jsx     # Visual badge for user roles
│   │   ├── context/
│   │   │   └── AuthContext.jsx   # Auth provider, user session & helpers
│   │   ├── pages/
│   │   │   ├── Login.jsx         # Login screen with 1-click test fill
│   │   │   ├── Register.jsx      # User registration with team picker
│   │   │   ├── Dashboard.jsx     # Role-customized dashboard & profile
│   │   │   ├── AdminUsers.jsx    # User table & role assignment panel
│   │   │   └── Unauthorized.jsx # 403 Forbidden screen
│   │   ├── App.jsx               # React Router configuration
│   │   ├── main.jsx              # Vite entry point
│   │   └── index.css             # Tailwind CSS directives
│   ├── index.html
│   ├── package.json
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   └── vite.config.js
└── README.md
```

---

## 🚀 Step-by-Step Setup Instructions

### 1. Backend Setup (FastAPI)

1. Open a terminal and navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a Python virtual environment:
   - **Windows (PowerShell)**:
     ```powershell
     python -m venv venv
     .\venv\Scripts\Activate.ps1
     ```
   - **Linux / macOS**:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```
3. Install backend dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the FastAPI development server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
5. Interactive API Documentation:
   - **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
   - **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

### 2. Frontend Setup (React + Vite + Tailwind)

1. Open another terminal and navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install npm dependencies:
   ```bash
   npm install
   ```
3. Start the Vite dev server:
   ```bash
   npm run dev
   ```
4. Access the application in your browser:
   - **Frontend URL**: [http://localhost:5173](http://localhost:5173)

---

## 🔑 Pre-Seeded Demo Accounts (Instant 1-Click Testing)

When the backend starts up for the first time, it automatically creates sample teams and four pre-configured test users:

| Role | Email | Password | Pre-assigned Team |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin@decisionreplay.com` | `Admin@123` | Executive Governance & Risk |
| **Manager** | `manager@decisionreplay.com` | `Manager@123` | Platform Architecture & Engineering |
| **Reviewer** | `reviewer@decisionreplay.com` | `Reviewer@123` | Product Strategy & UX |
| **Employee** | `employee@decisionreplay.com` | `Employee@123` | Platform Architecture & Engineering |

*(The login screen also includes quick 1-click buttons to auto-populate these test credentials!)*

---

## 🛡️ Milestone 1 Backend API Endpoints

### Authentication (`/api/v1/auth`)
- `POST /api/v1/auth/register` - Register a new user
- `POST /api/v1/auth/login` - Authenticate with email/password and receive JWT
- `GET /api/v1/auth/me` - Get profile of the currently logged-in user

### User & Role Management (`/api/v1/users`)
- `GET /api/v1/users` - List all users (filter by `role`, `team_id`, or `search`)
- `GET /api/v1/users/{id}` - Get user details
- `PUT /api/v1/users/{id}` - Update user profile
- `PUT /api/v1/users/{id}/role` - Assign role (*Admin only*)
- `PUT /api/v1/users/{id}/status` - Activate / Deactivate account (*Admin only*)

### Teams Management (`/api/v1/teams`)
- `GET /api/v1/teams` - List all organizational teams
- `POST /api/v1/teams` - Create a team (*Manager / Admin only*)
- `GET /api/v1/teams/{id}` - Get team details
