#!/usr/bin/env python3
"""
Initialize database with tables and seed data
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.core.database import init_db, engine, SessionLocal
from app.core.security import get_password_hash
from app.models import User, Audio, AudioAnalysis
from sqlalchemy.orm import Session


def create_tables():
    """Create all database tables"""
    print("🗄️  Creating database tables...")
    init_db()
    print("✅ Tables created successfully!")


def create_test_user(db: Session):
    """Create a test user for development"""
    print("👤 Creating test user...")
    
    # Check if user exists
    existing = db.query(User).filter(User.email == "test@samplemind.ai").first()
    if existing:
        print("ℹ️  Test user already exists")
        return existing
    
    user = User(
        email="test@samplemind.ai",
        hashed_password=get_password_hash("test123456"),
        full_name="Test User",
        is_active=True,
        is_beta_user=True,
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    print(f"✅ Test user created: {user.email}")
    print(f"   Password: test123456")
    return user


def main():
    """Main initialization function"""
    print("🚀 SampleMind AI - Database Initialization")
    print("=" * 50)
    
    try:
        # Create tables
        create_tables()
        
        # Create test data
        db = SessionLocal()
        try:
            user = create_test_user(db)
            print(f"\n✅ Database initialized successfully!")
            print(f"\n📝 Test credentials:")
            print(f"   Email: test@samplemind.ai")
            print(f"   Password: test123456")
            print(f"\n🔗 API: http://localhost:8000")
            print(f"📚 Docs: http://localhost:8000/api/docs")
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
