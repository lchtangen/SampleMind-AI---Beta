"""
User database model
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class User(Base):
    """User model for authentication and profile"""
    
    __tablename__ = "users"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Authentication
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    
    # Profile
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    
    # Premium/Beta access
    is_premium = Column(Boolean, default=False, nullable=False)
    is_beta_user = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login_at = Column(DateTime, nullable=True)
    
    # Relationships
    audio_files = relationship("Audio", back_populates="user", cascade="all, delete-orphan")
    import_jobs = relationship("AudioImportJob", back_populates="user", cascade="all, delete-orphan")
    embeddings = relationship("AudioEmbedding", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}')>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "email": self.email,
            "full_name": self.full_name,
            "is_active": self.is_active,
            "is_premium": self.is_premium,
            "is_beta_user": self.is_beta_user,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login_at": self.last_login_at.isoformat() if self.last_login_at else None,
        }
