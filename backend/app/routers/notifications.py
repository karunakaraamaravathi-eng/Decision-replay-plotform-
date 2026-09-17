from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.auth import get_current_active_user
from app.schemas import NotificationResponse, NotificationUnreadCount
from app.services import notification_service

router = APIRouter(prefix="/notifications", tags=["Notifications & Alerts"])


@router.get("", response_model=List[NotificationResponse])
def list_notifications(
    unread_only: bool = Query(False, description="Filter for unread notifications only"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Retrieve in-app notifications for current authenticated user with unread filter and pagination.
    """
    return notification_service.get_user_notifications(
        db, user_id=current_user.id, unread_only=unread_only, skip=skip, limit=limit
    )


@router.get("/unread-count", response_model=NotificationUnreadCount)
def get_unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get the total count of unread notifications for badge rendering.
    """
    count = notification_service.get_unread_count(db, user_id=current_user.id)
    return NotificationUnreadCount(unread_count=count)


@router.patch("/{id}/read", response_model=NotificationResponse)
def mark_notification_read(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Mark a single notification as read.
    """
    notif = notification_service.mark_as_read(db, notification_id=id, user_id=current_user.id)
    if not notif:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found or access denied"
        )
    return notif


@router.post("/mark-all-read")
def mark_all_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Mark all notifications of the current user as read.
    """
    count = notification_service.mark_all_as_read(db, user_id=current_user.id)
    return {"status": "success", "marked_read_count": count}
