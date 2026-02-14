"""
Database models and schema for GUIS
"""
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey, Text, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

Base = declarative_base()

class University(Base):
    """University model"""
    __tablename__ = "universities"
    
    id = Column(Integer, primary_key=True, index=True)
    original_name = Column(String, nullable=False, index=True)
    translated_name = Column(String, index=True)
    country = Column(String, nullable=False, index=True)
    exists_in_gotouniversity = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    programs = relationship("Program", back_populates="university", cascade="all, delete-orphan")


class Program(Base):
    """Program/Course model"""
    __tablename__ = "programs"
    
    id = Column(Integer, primary_key=True, index=True)
    university_id = Column(Integer, ForeignKey("universities.id"), nullable=False)
    course_name = Column(String, nullable=False, index=True)
    program_url = Column(String, nullable=False, unique=True, index=True)
    level = Column(String, nullable=False, index=True)  # UG or PG
    taught_in_english = Column(Boolean, default=False)
    delivery_mode = Column(String, default="offline")  # online, offline, hybrid, bilingual
    visited = Column(Boolean, default=False)
    content_hash = Column(String, index=True)  # SHA256 hash
    embedding_vector = Column(LargeBinary)  # Stored as bytes
    last_checked = Column(DateTime, default=datetime.utcnow)
    last_modified_header = Column(String)
    etag = Column(String)
    confidence_score = Column(String)  # ML classification confidence
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    university = relationship("University", back_populates="programs")


class Database:
    """Database manager"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            # Default to project root
            import os
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(project_root, "guis.db")
        self.db_path = db_path
        self.engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
        Base.metadata.create_all(bind=self.engine)
        
        # Add delivery_mode column if it doesn't exist (migration)
        self._migrate_database()
        
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def _migrate_database(self):
        """Add new columns to existing database if needed"""
        try:
            from sqlalchemy import inspect, text
            inspector = inspect(self.engine)
            columns = [col['name'] for col in inspector.get_columns('programs')]
            
            if 'delivery_mode' not in columns:
                with self.engine.connect() as conn:
                    conn.execute(text("ALTER TABLE programs ADD COLUMN delivery_mode VARCHAR DEFAULT 'offline'"))
                    conn.commit()
        except Exception as e:
            # Column might already exist or table doesn't exist yet
            pass
    
    def get_session(self):
        """Get database session"""
        return self.SessionLocal()
    
    def close(self):
        """Close database connection"""
        self.engine.dispose()

