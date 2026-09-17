import pytest
from app.models import Decision, DecisionStatus, ApprovalStatus


def _create_sample_decision(client, headers, title="Test Architecture Decision"):
    payload = {
        "title": title,
        "problem_statement": "Testing multi-level approval pipeline and compliance audit trails.",
        "category": "Architecture",
        "status": "Draft"
    }
    res = client.post("/api/v1/decisions", json=payload, headers=headers)
    assert res.status_code == 201
    return res.json()


def test_multilevel_approval_lifecycle_and_history(client, auth_headers, test_users):
    """
    Verify complete multi-level approval workflow:
    1. Employee creates decision (Draft)
    2. Employee submits for review -> becomes 'Under Review' (Level 1 Reviewer assigned)
    3. Reviewer approves Level 1 -> advances to Level 2 (Manager assigned)
    4. Manager approves Level 2 -> becomes 'Approved'
    5. Check approval history trail contains all steps
    """
    emp_headers = auth_headers["employee"]
    rev_headers = auth_headers["reviewer"]
    mgr_headers = auth_headers["manager"]
    reviewer_user = test_users["reviewer"]

    # Step 1: Create Decision
    dec = _create_sample_decision(client, emp_headers, "Cloud Migration Strategy")
    dec_id = dec["id"]
    assert dec["status"] == "Draft"

    # Step 2: Submit for review with Level 1 reviewer
    submit_res = client.post(
        f"/api/v1/decisions/{dec_id}/submit-for-review",
        json={"reviewer_id": reviewer_user.id, "comments": "Please review cloud sizing"},
        headers=emp_headers
    )
    assert submit_res.status_code == 200
    assert submit_res.json()["status"] == "Under Review"

    # Verify details reflect Level 1 pending
    detail_res = client.get(f"/api/v1/decisions/{dec_id}", headers=emp_headers)
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert len(detail["approvals"]) == 1
    assert detail["approvals"][0]["level"] == 1
    assert detail["approvals"][0]["status"] == "PENDING"

    # Step 3: Reviewer approves Level 1
    app1_res = client.post(
        f"/api/v1/decisions/{dec_id}/approve",
        json={"comments": "Technical evaluation passed."},
        headers=rev_headers
    )
    assert app1_res.status_code == 200
    assert app1_res.json()["status"] == "Under Review"

    # Check that it advanced to Level 2
    detail2_res = client.get(f"/api/v1/decisions/{dec_id}", headers=emp_headers)
    detail2 = detail2_res.json()
    assert len(detail2["approvals"]) == 2
    assert detail2["approvals"][0]["status"] == "APPROVED"
    assert detail2["approvals"][1]["level"] == 2
    assert detail2["approvals"][1]["status"] == "PENDING"

    # Step 4: Manager approves Level 2
    app2_res = client.post(
        f"/api/v1/decisions/{dec_id}/approve",
        json={"comments": "Budget approved for Phase 1."},
        headers=mgr_headers
    )
    assert app2_res.status_code == 200
    assert app2_res.json()["status"] == "Approved"

    # Step 5: Verify historical trail
    hist_res = client.get(f"/api/v1/decisions/{dec_id}/approval-history", headers=emp_headers)
    assert hist_res.status_code == 200
    hist = hist_res.json()
    assert hist["status"] == "Approved"
    assert len(hist["history"]) >= 3
    actions = [h["action"] for h in hist["history"]]
    assert "SUBMITTED" in actions
    assert "APPROVED" in actions


def test_rejection_workflow(client, auth_headers, test_users):
    """
    Verify rejection at review level transitions status to 'Rejected' and enforces comments.
    """
    emp_headers = auth_headers["employee"]
    rev_headers = auth_headers["reviewer"]

    dec = _create_sample_decision(client, emp_headers, "Unencrypted S3 Storage")
    dec_id = dec["id"]

    # Submit
    client.post(f"/api/v1/decisions/{dec_id}/submit-for-review", json={}, headers=emp_headers)

    # Attempt reject with empty comment -> 422 Unprocessable Entity
    bad_reject = client.post(f"/api/v1/decisions/{dec_id}/reject", json={"comments": "no"}, headers=rev_headers)
    assert bad_reject.status_code == 422

    # Proper rejection
    reject_res = client.post(
        f"/api/v1/decisions/{dec_id}/reject",
        json={"comments": "Security audit failed. Does not meet zero-trust encryption requirements."},
        headers=rev_headers
    )
    assert reject_res.status_code == 200
    assert reject_res.json()["status"] == "Rejected"


def test_escalation_workflow(client, auth_headers, test_users):
    """
    Verify that reviewers or managers can escalate a pending decision.
    """
    emp_headers = auth_headers["employee"]
    rev_headers = auth_headers["reviewer"]
    mgr_headers = auth_headers["manager"]
    manager_user = test_users["manager"]

    dec = _create_sample_decision(client, emp_headers, "Urgent Hotfix Architecture")
    dec_id = dec["id"]

    client.post(f"/api/v1/decisions/{dec_id}/submit-for-review", json={}, headers=emp_headers)

    # Escalate to Manager
    esc_res = client.post(
        f"/api/v1/decisions/{dec_id}/escalate",
        json={"reason": "Turnaround SLA breached", "new_approver_id": manager_user.id},
        headers=rev_headers
    )
    assert esc_res.status_code == 200

    hist_res = client.get(f"/api/v1/decisions/{dec_id}/approval-history", headers=mgr_headers)
    assert hist_res.status_code == 200
    actions = [h["action"] for h in hist_res.json()["history"]]
    assert "ESCALATED" in actions


def test_system_notifications(client, auth_headers):
    """
    Verify notification creation, listing, unread count, and marking as read.
    """
    emp_headers = auth_headers["employee"]
    rev_headers = auth_headers["reviewer"]

    # Submitting a decision creates notification for reviewer
    dec = _create_sample_decision(client, emp_headers, "Notification Trigger Decision")
    client.post(f"/api/v1/decisions/{dec['id']}/submit-for-review", json={}, headers=emp_headers)

    # Reviewer checks notifications
    notifs_res = client.get("/api/v1/notifications", headers=rev_headers)
    assert notifs_res.status_code == 200
    notifs = notifs_res.json()
    assert len(notifs) >= 1

    unread_res = client.get("/api/v1/notifications/unread-count", headers=rev_headers)
    assert unread_res.status_code == 200
    assert unread_res.json()["unread_count"] >= 1

    # Mark first notification as read
    first_id = notifs[0]["id"]
    read_res = client.patch(f"/api/v1/notifications/{first_id}/read", headers=rev_headers)
    assert read_res.status_code == 200
    assert read_res.json()["is_read"] is True

    # Mark all read
    mark_all_res = client.post("/api/v1/notifications/mark-all-read", headers=rev_headers)
    assert mark_all_res.status_code == 200


def test_audit_logging_and_compliance(client, auth_headers):
    """
    Verify automatic audit logging on actions and admin-only log query endpoint.
    """
    admin_headers = auth_headers["admin"]
    emp_headers = auth_headers["employee"]

    # Employee performs an action
    _create_sample_decision(client, emp_headers, "Audited Action Decision")

    # Employee cannot view all audit logs (Admin/Manager restricted)
    emp_audit = client.get("/api/v1/audit/logs", headers=emp_headers)
    assert emp_audit.status_code == 403

    # Admin queries audit logs
    admin_audit = client.get("/api/v1/audit/logs", headers=admin_headers)
    assert admin_audit.status_code == 200
    data = admin_audit.json()
    assert "items" in data
    assert data["total"] >= 1


def test_role_based_dashboards(client, auth_headers):
    """
    Verify Employee, Manager, and Admin dashboards return appropriate metrics and RBAC.
    """
    emp_headers = auth_headers["employee"]
    mgr_headers = auth_headers["manager"]
    admin_headers = auth_headers["admin"]

    # 1. Employee Dashboard
    emp_dash = client.get("/api/v1/dashboards/employee", headers=emp_headers)
    assert emp_dash.status_code == 200
    emp_data = emp_dash.json()
    assert "my_decisions_count" in emp_data
    assert "my_decisions" in emp_data
    assert "pending_reviews_awaiting_input" in emp_data

    # 2. Manager Dashboard
    mgr_dash = client.get("/api/v1/dashboards/manager", headers=mgr_headers)
    assert mgr_dash.status_code == 200
    mgr_data = mgr_dash.json()
    assert "team_overview" in mgr_data
    assert "pending_approvals_queue" in mgr_data
    assert "decision_statistics" in mgr_data

    # Employee cannot access manager dashboard
    assert client.get("/api/v1/dashboards/manager", headers=emp_headers).status_code == 403

    # 3. Admin Dashboard
    admin_dash = client.get("/api/v1/dashboards/admin", headers=admin_headers)
    assert admin_dash.status_code == 200
    admin_data = admin_dash.json()
    assert "total_users_by_role" in admin_data
    assert "active_decisions_metrics" in admin_data
    assert "approval_completion_turnaround" in admin_data


def test_reporting_engine_pdf_and_excel(client, auth_headers):
    """
    Verify PDF and Excel report generation endpoints return valid byte payloads.
    """
    emp_headers = auth_headers["employee"]
    admin_headers = auth_headers["admin"]

    # Seed at least one decision
    dec = _create_sample_decision(client, emp_headers, "Export Test Decision")

    # 1. Decision Summary Reports (PDF & Excel)
    pdf_res = client.get("/api/v1/reports/decisions/export?format=pdf", headers=emp_headers)
    assert pdf_res.status_code == 200
    assert pdf_res.headers["content-type"] == "application/pdf"
    assert len(pdf_res.content) > 100

    excel_res = client.get("/api/v1/reports/decisions/export?format=excel", headers=emp_headers)
    assert excel_res.status_code == 200
    assert "spreadsheetml" in excel_res.headers["content-type"]
    assert len(excel_res.content) > 100

    # Single decision export
    single_pdf = client.get(f"/api/v1/reports/decisions/{dec['id']}/export?format=pdf", headers=emp_headers)
    assert single_pdf.status_code == 200
    assert single_pdf.headers["content-type"] == "application/pdf"

    # 2. Approvals Turnaround Report
    app_pdf = client.get("/api/v1/reports/approvals/export?format=pdf", headers=emp_headers)
    assert app_pdf.status_code == 200
    assert app_pdf.headers["content-type"] == "application/pdf"

    app_excel = client.get("/api/v1/reports/approvals/export?format=excel", headers=emp_headers)
    assert app_excel.status_code == 200
    assert "spreadsheetml" in app_excel.headers["content-type"]

    # 3. Audit Compliance Report (Admin only)
    audit_pdf = client.get("/api/v1/reports/audit/export?format=pdf", headers=admin_headers)
    assert audit_pdf.status_code == 200
    assert audit_pdf.headers["content-type"] == "application/pdf"

    audit_excel = client.get("/api/v1/reports/audit/export?format=excel", headers=admin_headers)
    assert audit_excel.status_code == 200
    assert "spreadsheetml" in audit_excel.headers["content-type"]
