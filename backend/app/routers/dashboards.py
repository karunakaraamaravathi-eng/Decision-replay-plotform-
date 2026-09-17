from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, RoleEnum
from app.auth import get_current_active_user, require_role
from app.schemas import (
    EmployeeDashboardResponse,
    ManagerDashboardResponse,
    AdminDashboardResponse
)
from app.services import dashboard_service

router = APIRouter(prefix="/dashboards", tags=["Role-Based Dashboards"])


@router.get("/employee", response_model=EmployeeDashboardResponse)
def get_employee_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get customized workspace metrics and activities for the authenticated user/employee.
    """
    return dashboard_service.get_employee_dashboard(db, current_user)


@router.get(
    "/manager",
    response_model=ManagerDashboardResponse,
    dependencies=[Depends(require_role([RoleEnum.MANAGER, RoleEnum.ADMINISTRATOR]))]
)
def get_manager_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get team operational metrics, pending approvals queue, and decision statistics for Managers.
    """
    return dashboard_service.get_manager_dashboard(db, current_user)


@router.get(
    "/admin",
    response_model=AdminDashboardResponse,
    dependencies=[Depends(require_role([RoleEnum.ADMINISTRATOR]))]
)
def get_admin_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get organizational system analytics, user roles, turnaround metrics, and audit summaries for Administrators.
    """
    return dashboard_service.get_admin_dashboard(db)
