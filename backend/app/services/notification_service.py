from typing import List, Optional
from sqlalchemy.orm import Session
from app.models import Notification, User, RoleEnum, NotificationType


def create_notification(
    db: Session,
    user_id: int,
    title: str,
    message: str,
    type: str = NotificationType.APPROVAL_REQUEST.value,
    link: Optional[str] = None
) -> Notification:
    """Create a single notification for a specific user."""
    notif = Notification(
        user_id=user_id,
        title=title,
        message=message,
        type=type if isinstance(type, str) else type.value,
        is_read=False,
        link=link
    )
    db.add(notif)
    db.commit()
    db.refresh(notif)
    return notif


def notify_users(
    db: Session,
    user_ids: List[int],
    title: str,
    message: str,
    type: str = NotificationType.APPROVAL_REQUEST.value,
    link: Optional[str] = None
):
    """Batch notification creation for a list of user IDs."""
    unique_ids = set(user_ids)
    for uid in unique_ids:
        notif = Notification(
            user_id=uid,
            title=title,
            message=message,
            type=type if isinstance(type, str) else type.value,
            is_read=False,
            link=link
        )
        db.add(notif)
    db.commit()


def notify_team(
    db: Session,
    team_id: int,
    title: str,
    message: str,
    type: str = NotificationType.APPROVAL_REQUEST.value,
    link: Optional[str] = None,
    exclude_user_id: Optional[int] = None
):
    """Notify all active members of a specific team."""
    query = db.query(User.id).filter(User.team_id == team_id, User.is_active == True)
    if exclude_user_id:
        query = query.filter(User.id != exclude_user_id)
    user_ids = [u[0] for u in query.all()]
    notify_users(db, user_ids, title, message, type, link)


def notify_role(
    db: Session,
    role: RoleEnum,
    title: str,
    message: str,
    type: str = NotificationType.APPROVAL_REQUEST.value,
    link: Optional[str] = None,
    exclude_user_id: Optional[int] = None
):
    """Notify all active users with a specified organizational role."""
    query = db.query(User.id).filter(User.role == role, User.is_active == True)
    if exclude_user_id:
        query = query.filter(User.id != exclude_user_id)
    user_ids = [u[0] for u in query.all()]
    notify_users(db, user_ids, title, message, type, link)


def get_user_notifications(
    db: Session,
    user_id: int,
    unread_only: bool = False,
    skip: int = 0,
    limit: int = 50
) -> List[Notification]:
    """Retrieve notifications for a user ordered by newest first."""
    query = db.query(Notification).filter(Notification.user_id == user_id)
    if unread_only:
        query = query.filter(Notification.is_read == False)
    return query.order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()


def get_unread_count(db: Session, user_id: int) -> int:
    """Count unread notifications for a user."""
    return db.query(Notification).filter(
        Notification.user_id == user_id,
        Notification.is_read == False
    ).count()


def mark_as_read(db: Session, notification_id: int, user_id: int) -> Optional[Notification]:
    """Mark a specific user notification as read."""
    notif = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == user_id
    ).first()
    if notif:
        notif.is_read = True
        db.commit()
        db.refresh(notif)
    return notif


def mark_all_as_read(db: Session, user_id: int) -> int:
    """Mark all notifications of a user as read."""
    count = db.query(Notification).filter(
        Notification.user_id == user_id,
        Notification.is_read == False
    ).update({"is_read": True})
    db.commit()
    return count
