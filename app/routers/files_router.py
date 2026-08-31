import os
import shutil
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Decision, Attachment, User, AuditLog
from app.schemas import AttachmentResponse
from app.auth import get_current_user

router = APIRouter(tags=["Document Management"])

UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "static", "uploads"))
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/decisions/{decision_id}/upload", response_model=AttachmentResponse, status_code=status.HTTP_201_CREATED)
async def upload_attachment(
    decision_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload a document or file attachment for a decision."""
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")

    safe_filename = f"decision_{decision_id}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, safe_filename)

    # Save file contents
    content = await file.read()
    file_size = len(content)
    with open(file_path, "wb") as f:
        f.write(content)

    attachment = Attachment(
        decision_id=decision_id,
        uploaded_by_id=current_user.id,
        filename=file.filename,
        file_path=file_path,
        file_size=file_size,
        content_type=file.content_type
    )
    db.add(attachment)

    audit = AuditLog(
        user_id=current_user.id,
        action="ATTACHMENT_UPLOAD",
        entity_type="Decision",
        entity_id=decision_id,
        details=f"Uploaded file '{file.filename}' ({file_size} bytes) to decision #{decision_id}"
    )
    db.add(audit)
    db.commit()
    db.refresh(attachment)

    res = AttachmentResponse.model_validate(attachment)
    res.uploader_name = current_user.full_name
    return res

@router.get("/decisions/{decision_id}/attachments", response_model=List[AttachmentResponse])
def list_attachments(
    decision_id: int,
    db: Session = Depends(get_db)
):
    """List all supporting attachments for a decision."""
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")

    attachments = db.query(Attachment).filter(Attachment.decision_id == decision_id).all()
    result = []
    for att in attachments:
        res = AttachmentResponse.model_validate(att)
        res.uploader_name = att.uploaded_by.full_name if att.uploaded_by else "Unknown"
        result.append(res)
    return result

@router.get("/attachments/{attachment_id}/download")
def download_attachment(
    attachment_id: int,
    db: Session = Depends(get_db)
):
    """Download an attached file."""
    att = db.query(Attachment).filter(Attachment.id == attachment_id).first()
    if not att:
        raise HTTPException(status_code=404, detail="Attachment not found")

    if not os.path.exists(att.file_path):
        raise HTTPException(status_code=404, detail="File on disk not found")

    return FileResponse(
        path=att.file_path,
        filename=att.filename,
        media_type=att.content_type or "application/octet-stream"
    )
