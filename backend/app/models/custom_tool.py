"""ORM model for custom user-created tools."""

from sqlalchemy import Column, String, Text, Boolean, DateTime, Enum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
import enum
from app.database import Base


class ToolStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING_VERIFICATION = "pending_verification"
    VERIFIED = "verified"
    REJECTED = "rejected"
    ERROR = "error"


class ToolType(str, enum.Enum):
    HTTP = "http"
    DATABASE = "database"
    EMAIL = "email"
    WEBHOOK = "webhook"
    TRANSFORM = "transform"
    DELAY = "delay"
    MESSAGING = "messaging"
    STORAGE = "storage"
    CUSTOM = "custom"


class CustomTool(Base):
    __tablename__ = "custom_tools"

    id = Column(String, primary_key=True, default=lambda: __import__("uuid").uuid4().hex[:12])
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=False)
    tool_type = Column(Enum(ToolType), nullable=False, default=ToolType.CUSTOM)
    status = Column(Enum(ToolStatus), nullable=False, default=ToolStatus.DRAFT)

    # Config stored as JSON
    input_schema = Column(JSONB, nullable=False, default=dict)
    config = Column(JSONB, nullable=False, default=dict)
    output_schema = Column(JSONB, nullable=False, default=dict)

    # Verification fields
    last_test_result = Column(JSONB, nullable=True)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    verified_by = Column(String(100), nullable=True)

    # Integration config — real service credentials (JSONB on Postgres, JSON on SQLite)
    integration_config = Column(JSONB, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
