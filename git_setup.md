# GitHub Repository Setup Guide
## Expert Decision Replay Platform — Milestone 1

Follow these simple steps to push your completed **Milestone 1** project to your GitHub account:

### Step 1: Open Terminal in Project Directory
Open your terminal (PowerShell, Command Prompt, or Git Bash) in your project folder:
```bash
cd c:\Users\admin\OneDrive\Pictures\Desktop\python_proj
```

---

### Step 2: Initialize Git & Commit Files
Run the following commands:
```bash
git init
git add .
git commit -m "Milestone 1 (Week 1-2): Complete FastAPI backend, JWT Auth, Database Design, User Management & UI Wireframes"
```

*Or simply run `init_git.bat` by double-clicking it in your project folder.*

---

### Step 3: Create GitHub Repository
1. Go to [GitHub.com](https://github.com) and sign in.
2. Click the **`+`** icon at the top right and select **New repository**.
3. Name your repository: `expert-decision-replay-platform`
4. Choose **Public** or **Private**.
5. Leave "Initialize this repository with a README" **unchecked** (we already have README and code).
6. Click **Create repository**.

---

### Step 4: Link Local Project to GitHub and Push
Copy the commands shown on your GitHub repository page (replace `YOUR_USERNAME` with your actual GitHub username):

```bash
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/expert-decision-replay-platform.git
git push -u origin main
```

---

### Step 5: Verify Deliverables on GitHub
Your repository now contains:
- `app/`: FastAPI Backend, Database Models, JWT Authentication, and User Management API.
- `static/`: Glassmorphism Web UI Single Page Application (SPA).
- `docs/`: Requirement Analysis, Database ER Specifications, and UI Wireframes.
- `tests/`: Automated Pytest test suite (100% passing).
- `requirements.txt` & `run.py`: Easy one-command execution (`python run.py`).
