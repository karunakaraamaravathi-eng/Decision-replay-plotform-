from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(String, default="Employee", nullable=False) # Employee, Reviewer, Manager, Administrator
    department = Column(String, default="Engineering")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
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
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    members = relationship("User", back_populates="team", foreign_keys=[User.team_id])

class Decision(Base):
    __tablename__ = "decisions"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    problem_statement = Column(Text, nullable=False)
    category = Column(String, nullable=False) # Architecture, Infrastructure, Security, Process
    status = Column(String, default="Draft") # Draft, Under Review, Approved, Rejected, Archived
    creator_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="SET NULL"), nullable=True)
    version = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    creator = relationship("User", back_populates="decisions")
    alternatives = relationship("Alternative", back_populates="decision", cascade="all, delete-orphan")
    approvals = relationship("ApprovalWorkflow", back_populates="decision", cascade="all, delete-orphan")

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

class ApprovalWorkflow(Base):
    __tablename__ = "approval_workflows"

    id = Column(Integer, primary_key=True, index=True)
    decision_id = Column(Integer, ForeignKey("decisions.id", ondelete="CASCADE"), nullable=False)
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    level = Column(Integer, default=1)
    status = Column(String, default="Pending") # Pending, Approved, Rejected
    comments = Column(Text)
    updated_at = Column(DateTime, default=datetime.utcnow)

    decision = relationship("Decision", back_populates="approvals")

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String, nullable=False)
    entity_type = Column(String, nullable=False) # User, Decision, Team, Approval
    entity_id = Column(Integer, nullable=True)
    details = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="audit_logs")
