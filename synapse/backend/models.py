import uuid
from datetime import datetime
from sqlalchemy import Column, String, Enum, DateTime, Boolean, Integer, ForeignKey, Numeric, Text, JSON, Table
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from database import Base
import enum

class ProjectType(str, enum.Enum):
    AUTO = "auto"
    IT = "it"
    REALTY = "realty"
    HEALTH = "health"
    INCUBATOR = "incubator"

class ProjectStatus(str, enum.Enum):
    ACTIVE = "active"
    ARCHIVE = "archive"
    IDEA = "idea"

class TransactionType(str, enum.Enum):
    INCOME = "income"
    EXPENSE = "expense"

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    type = Column(Enum(ProjectType), default=ProjectType.IT)
    status = Column(Enum(ProjectStatus), default=ProjectStatus.ACTIVE)
    meta_data = Column(JSONB, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    
    tasks = relationship("Task", back_populates="project")
    transactions = relationship("Transaction", back_populates="project")
    notes = relationship("Note", back_populates="project")

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=True)
    title = Column(String, nullable=False)
    due_date = Column(DateTime, nullable=True)
    is_completed = Column(Boolean, default=False)
    priority = Column(Integer, default=3)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    project = relationship("Project", back_populates="tasks")

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=True)
    amount = Column(Numeric(precision=15, scale=2), nullable=False)
    type = Column(Enum(TransactionType), nullable=False)
    category = Column(String, nullable=True)
    date = Column(DateTime, default=datetime.utcnow)
    
    project = relationship("Project", back_populates="transactions")

class Note(Base):
    __tablename__ = "notes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=True)
    content = Column(Text, nullable=False)
    tags = Column(JSON, default=[]) # Array of strings
    created_at = Column(DateTime, default=datetime.utcnow)
    
    project = relationship("Project", back_populates="notes")
