# UI Wireframes & Layout Specification
## Expert Decision Replay Platform — Milestone 1

### Screen Layouts & Component Architecture

#### 1. Navigation Header & Auth Bar
- **Brand Identity**: Logo & Title (`Expert Decision Replay Platform`)
- **Quick Demo Login Buttons**: Allows instant 1-click role testing (`Admin`, `Manager`, `Reviewer`, `Employee`).
- **User Profile Pill**: Displays user name, active role badge (`Administrator`, `Manager`, `Reviewer`, `Employee`), and Sign In / Sign Out modal triggers.

#### 2. Wireframe & Requirements Visualizer Tab
- **Project Scope Summary**: Interactive card presenting Milestone 1 outcomes and tech stack.
- **Database ER Visualizer**: Live table schema browser detailing fields, primary/foreign keys, and role access constraints.
- **UI Layout Wireframes**: Specification grid of all platform screens.

#### 3. Role Dashboards Tab
- **Metrics Cards**: Displays Total Users, Active Teams, Active Sessions, and Milestone 1 System Health.
- **Role Distribution Breakdown**: Badges highlighting current user count per role level.
- **Decision Lifecycle Roadmap**: Visual representation of decision status progression (`Draft` -> `Under Review` -> `Approved` / `Rejected` -> `Archived`).

#### 4. User Directory & Role Management Tab (Admin / Manager)
- **Data Table**: Displays User ID, Name, Email, Department, Role Badge, and Account Status.
- **Role Modifier Dropdown**: Interactive Admin privilege dropdown to promote/demote user roles dynamically via REST API.

#### 5. Audit & Activity Trail Tab (Admin)
- **Security Logs**: Real-time event log tracking user logins, role updates, and system initializations.
