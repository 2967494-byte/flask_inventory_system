import uuid
from datetime import datetime
from sqlalchemy import Column, String, Enum, DateTime, Boolean, Integer, ForeignKey, Numeric, Text, JSON, Table, BigInteger
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

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    username = Column(String, nullable=True)
    full_name = Column(String, nullable=True)
    profile_photo = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    projects = relationship("Project", back_populates="user")
    tasks = relationship("Task", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")
    notes = relationship("Note", back_populates="user")
    login_tokens = relationship("LoginToken", back_populates="user")

class LoginToken(Base):
    __tablename__ = "login_tokens"
    
    token = Column(String, primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_used = Column(Boolean, default=False)
    
    user = relationship("User", back_populates="login_tokens")

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    type = Column(Enum(ProjectType), default=ProjectType.IT)
    status = Column(Enum(ProjectStatus), default=ProjectStatus.ACTIVE)
    meta_data = Column(JSONB, default={})
    
    # Passport fields
    description = Column(String, nullable=True)
    goals = Column(String, nullable=True)
    deadline = Column(DateTime, nullable=True)
    budget = Column(Numeric(10, 2), nullable=True)
    progress = Column(Integer, default=0)  # 0-100%
    notes = Column(String, nullable=True)
    tags = Column(JSONB, default=[])
    files = Column(JSONB, default=[])  # [{name: str, data: base64, uploaded_at: str}]
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="projects")
    tasks = relationship("Task", back_populates="project")
    transactions = relationship("Transaction", back_populates="project")
    notes = relationship("Note", back_populates="project")

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=True)
    title = Column(String, nullable=False)
    due_date = Column(DateTime, nullable=True)
    is_completed = Column(Boolean, default=False)
    priority = Column(Integer, default=3)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="tasks")
    project = relationship("Project", back_populates="tasks")

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=True)
    amount = Column(Numeric(precision=15, scale=2), nullable=False)
    type = Column(Enum(TransactionType), nullable=False)
    category = Column(String, nullable=True)
    date = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="transactions")
    project = relationship("Project", back_populates="transactions")

class Note(Base):
    __tablename__ = "notes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=True)
    content = Column(Text, nullable=False)
    tags = Column(JSON, default=[]) # Array of strings
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="notes")
    project = relationship("Project", back_populates="notes")
