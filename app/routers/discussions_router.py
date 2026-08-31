from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Decision, Comment, User, AuditLog
from app.schemas import CommentCreate, CommentResponse
from app.auth import get_current_user

router = APIRouter(tags=["Discussion & Collaboration"])

@router.post("/decisions/{decision_id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def post_comment(
    decision_id: int,
    comment_in: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Post a comment or discussion note on a decision."""
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")

    if comment_in.parent_id:
        parent = db.query(Comment).filter(Comment.id == comment_in.parent_id).first()
        if not parent:
            raise HTTPException(status_code=404, detail="Parent comment not found")

    comment = Comment(
        decision_id=decision_id,
        user_id=current_user.id,
        parent_id=comment_in.parent_id,
        content=comment_in.content
    )
    db.add(comment)

    audit = AuditLog(
        user_id=current_user.id,
        action="COMMENT_POST",
        entity_type="Decision",
        entity_id=decision_id,
        details=f"User {current_user.full_name} commented on decision #{decision_id}: '{comment_in.content[:50]}...'"
    )
    db.add(audit)
    db.commit()
    db.refresh(comment)

    res = CommentResponse.model_validate(comment)
    res.author_name = current_user.full_name
    res.author_role = current_user.role
    return res

@router.get("/decisions/{decision_id}/comments", response_model=List[CommentResponse])
def get_comments(
    decision_id: int,
    db: Session = Depends(get_db)
):
    """Get all discussion comments for a decision."""
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")

    comments = db.query(Comment).filter(Comment.decision_id == decision_id).order_by(Comment.created_at.asc()).all()
    result = []
    for c in comments:
        res = CommentResponse.model_validate(c)
        res.author_name = c.user.full_name if c.user else "Unknown"
        res.author_role = c.user.role if c.user else "User"
        result.append(res)
    return result

@router.delete("/comments/{comment_id}", status_code=status.HTTP_200_OK)
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a comment."""
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    if comment.user_id != current_user.id and current_user.role != "Administrator":
        raise HTTPException(status_code=403, detail="Not authorized to delete this comment")

    decision_id = comment.decision_id
    db.delete(comment)

    audit = AuditLog(
        user_id=current_user.id,
        action="COMMENT_DELETE",
        entity_type="Decision",
        entity_id=decision_id,
        details=f"Deleted comment #{comment_id} from decision #{decision_id}"
    )
    db.add(audit)
    db.commit()
    return {"message": "Comment deleted successfully", "comment_id": comment_id}
