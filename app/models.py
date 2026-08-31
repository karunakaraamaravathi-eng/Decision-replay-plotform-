import os
import sys

# Ensure workspace root is in sys.path when running file directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(String, default="Employee", nullable=False) # Employee, Reviewer, Manager, Administrator
    department = Column(String, default="Engineering")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utc_now)
    
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    team = relationship("Team", back_populates="members", foreign_keys=[team_id])
    decisions = relationship("Decision", back_populates="creator")
    audit_logs = relationship("AuditLog", back_populates="user")

class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String)
    manager_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=utc_now)

    # Relationships
    members = relationship("User", back_populates="team", foreign_keys=[User.team_id])

class Decision(Base):
    __tablename__ = "decisions"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    problem_statement = Column(Text, nullable=False)
    category = Column(String, nullable=False) # Architecture, Infrastructure, Security, Process
    status = Column(String, default="Draft") # Draft, Under Review, Approved, Rejected, Archived
    rationale = Column(Text, nullable=True)
    creator_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="SET NULL"), nullable=True)
    version = Column(Integer, default=1)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    # Relationships
    creator = relationship("User", back_populates="decisions")
    team = relationship("Team")
    alternatives = relationship("Alternative", back_populates="decision", cascade="all, delete-orphan")
    approvals = relationship("ApprovalWorkflow", back_populates="decision", cascade="all, delete-orphan")
    versions = relationship("DecisionVersion", back_populates="decision", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="decision", cascade="all, delete-orphan")
    attachments = relationship("Attachment", back_populates="decision", cascade="all, delete-orphan")

class Alternative(Base):
    __tablename__ = "alternatives"

    id = Column(Integer, primary_key=True, index=True)
    decision_id = Column(Integer, ForeignKey("decisions.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    pros = Column(Text)
    cons = Column(Text)
    estimated_cost = Column(Float, default=0.0)
    risk_level = Column(String, default="Low") # Low, Medium, High
    feasibility_score = Column(Integer, default=5) # 1-10

    decision = relationship("Decision", back_populates="alternatives")

class DecisionVersion(Base):
    __tablename__ = "decision_versions"

    id = Column(Integer, primary_key=True, index=True)
    decision_id = Column(Integer, ForeignKey("decisions.id", ondelete="CASCADE"), nullable=False)
    version = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    problem_statement = Column(Text, nullable=False)
    category = Column(String, nullable=False)
    status = Column(String, nullable=False)
    rationale = Column(Text, nullable=True)
    change_summary = Column(String, nullable=True)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=utc_now)

    decision = relationship("Decision", back_populates="versions")
    created_by = relationship("User")

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    decision_id = Column(Integer, ForeignKey("decisions.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    parent_id = Column(Integer, ForeignKey("comments.id", ondelete="CASCADE"), nullable=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=utc_now)

    decision = relationship("Decision", back_populates="comments")
    user = relationship("User")

class Attachment(Base):
    __tablename__ = "attachments"

    id = Column(Integer, primary_key=True, index=True)
    decision_id = Column(Integer, ForeignKey("decisions.id", ondelete="CASCADE"), nullable=False)
    uploaded_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer, default=0)
    content_type = Column(String, nullable=True)
    uploaded_at = Column(DateTime, default=utc_now)

    decision = relationship("Decision", back_populates="attachments")
    uploaded_by = relationship("User")

class ApprovalWorkflow(Base):
    __tablename__ = "approval_workflows"

    id = Column(Integer, primary_key=True, index=True)
    decision_id = Column(Integer, ForeignKey("decisions.id", ondelete="CASCADE"), nullable=False)
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    level = Column(Integer, default=1)
    status = Column(String, default="Pending") # Pending, Approved, Rejected
    comments = Column(Text)
    updated_at = Column(DateTime, default=utc_now)

    decision = relationship("Decision", back_populates="approvals")

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String, nullable=False)
    entity_type = Column(String, nullable=False) # User, Decision, Team, Approval, Comment, Attachment
    entity_id = Column(Integer, nullable=True)
    details = Column(Text)
    user = relationship("User", back_populates="audit_logs")

if __name__ == "__main__":
    import os
    import sys
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    
    print("\n" + "=" * 60)
    print("  SQLALCHEMY ORM MODELS OVERVIEW")
    print("=" * 60)
    models = [User, Team, Decision, Alternative, DecisionVersion, Comment, Attachment, ApprovalWorkflow, AuditLog]
    for m in models:
        cols = [c.name for c in m.__table__.columns]
        print(f"[*] Table: {m.__tablename__:<20} | Columns ({len(cols)}): {', '.join(cols)}")
    print("=" * 60 + "\n")
