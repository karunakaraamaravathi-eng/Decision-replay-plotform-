# Expert Decision Replay Platform

A centralized platform for capturing organizational decisions, evaluating alternatives, managing file attachments, collaborating in discussion threads, and tracking decision version history.

---

## Milestone 2

### Completion PDF Reports
* 📄 **[Milestone 2 Report PDF](docs/Expert_Decision_Replay_Platform_Milestone_2_Report.pdf)**
* 📄 **[Milestone 1 Report PDF](docs/Expert_Decision_Replay_Platform_Milestone_1_Report.pdf)**

---

## Features Implemented in Milestone 2
* **Decision Management**: Full CRUD operations with categories (Architecture, Infrastructure, Security, Process) and lifecycle statuses (Draft, Under Review, Approved, Rejected, Archived).
* **Alternative Comparison**: Matrix evaluation of pros, cons, costs, risk profiles, feasibility scores, and automated top recommendation.
* **Discussion Threads**: Collaborative comment notes on decisions with role attribution.
* **File Attachments**: Upload and download supporting PDF/image documents.
* **Version Tracking**: Automatic immutable snapshot history recorded on decision edits.

---

## Demo Login Credentials

| Role | Email | Password |
| :--- | :--- | :--- |
| Administrator | `admin@expert.org` | `admin123` |
| Manager | `manager@expert.org` | `manager123` |
| Reviewer | `reviewer@expert.org` | `reviewer123` |
| Employee | `employee@expert.org` | `emp123` |

---

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run Application Server
python run.py
```

* **Web UI**: http://127.0.0.1:8000
* **API Documentation**: http://127.0.0.1:8000/docs
* **Run Tests**: `pytest`
