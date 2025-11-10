"""Import job models"""

from datetime import datetime
import enum

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship

from app.core.database import Base


class ImportJobStatus(str, enum.Enum):
    """Status values for bulk import jobs"""

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class AudioImportJob(Base):
    """Represents a bulk audio import operation"""

    __tablename__ = "audio_import_jobs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    status = Column(SQLEnum(ImportJobStatus), default=ImportJobStatus.PENDING, nullable=False, index=True)
    source = Column(String, nullable=True)
    manifest_path = Column(String, nullable=True)

    total_files = Column(Integer, nullable=False, default=0)
    processed_files = Column(Integer, nullable=False, default=0)
    duplicate_files = Column(Integer, nullable=False, default=0)
    failed_files = Column(Integer, nullable=False, default=0)

    error_log = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="import_jobs")
    audio_files = relationship("Audio", back_populates="import_job")

    def __repr__(self) -> str:
        return f"<AudioImportJob(id={self.id}, status='{self.status}', total_files={self.total_files})>"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "status": self.status.value if isinstance(self.status, ImportJobStatus) else self.status,
            "source": self.source,
            "manifest_path": self.manifest_path,
            "total_files": self.total_files,
            "processed_files": self.processed_files,
            "duplicate_files": self.duplicate_files,
            "failed_files": self.failed_files,
            "error_log": self.error_log,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
