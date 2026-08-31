# GitHub Repository Setup Guide
## Expert Decision Replay Platform — Milestone 1 & 2

Follow these simple steps to push your completed **Milestone 1 & 2** project to your GitHub account:

### Step 1: Open Terminal in Project Directory
Open your terminal (PowerShell, Command Prompt, or Git Bash) in your project folder:
```bash
cd c:\Users\admin\OneDrive\Pictures\Desktop\python_proj
```

---

### Step 2: Initialize Git & Commit Milestone 1 & 2 Files
Run the following commands:
```bash
git init
git add .
git commit -m "Milestone 1 & 2 Completed: Decision Management, Alternative Matrix, Discussions, File Uploads, Version Tracking, Auth & RBAC"
```

---

### Step 3: Link Local Project to GitHub and Push
Replace `YOUR_USERNAME` with your actual GitHub username:

```bash
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/expert-decision-replay-platform.git
git push -u origin main
```

---

### Step 4: Verify Deliverables on GitHub
Your repository now contains:
- `app/`: FastAPI Backend, Database Models, JWT Auth, Decisions, Alternatives Matrix, Discussion Comments, File Uploads, Version Tracking, and User Management APIs.
- `static/`: Single Page Application (SPA) Web Interface with Decision Workspace tab, Alternative Matrix side-by-side cards, Discussion Threads, Attachment uploader, and Version History timeline.
- `docs/`: PDF Completion Reports for Milestone 1 & 2 (`Expert_Decision_Replay_Platform_Milestone_1_Report.pdf`, `Expert_Decision_Replay_Platform_Milestone_2_Report.pdf`), Requirement Analysis, and Database Export.
- `tests/`: Automated Pytest test suite with 20/20 tests passing (100% pass rate).
- `requirements.txt` & `run.py`: One-command execution (`python run.py`).
