"""
Database Models - SQLite with <5ms query optimization
Constitutional AI compliant data structures
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, JSON, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

# Database setup with flexible path
def get_database_url():
    """Get database URL with fallback options"""
    # Check for explicit DATABASE_URL
    if os.getenv("DATABASE_URL"):
        return os.getenv("DATABASE_URL")
    
    # Check for DATABASE_PATH
    db_path = os.getenv("DATABASE_PATH")
    if db_path:
        return f"sqlite:///{db_path}"
    
    # Try to find a writable location
    possible_paths = [
        "/tmp/tiktok.db",  # Always writable in containers
        "database/tiktok.db",  # Local development
        "/app/database/tiktok.db"  # Container path
    ]
    
    for path in possible_paths:
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            return f"sqlite:///{path}"
        except:
            continue
    
    # Default fallback
    return "sqlite:///tiktok_ai.db"

DATABASE_URL = get_database_url()
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Video(Base):
    """Video content from platforms"""
    __tablename__ = "videos"
    
    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String, index=True)
    platform_id = Column(String, unique=True)
    url = Column(String)
    title = Column(String)
    author = Column(String)
    engagement_score = Column(Float, index=True)
    viral_score = Column(Float, index=True)
    video_metadata = Column(JSON)
    processed = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    
    # Relationships
    clips = relationship("Clip", back_populates="video")
    
    # Indexes for <5ms queries
    __table_args__ = (
        Index('idx_videos_processed_score', 'processed', 'viral_score'),
        Index('idx_videos_platform_processed', 'platform', 'processed'),
    )


class Clip(Base):
    """Extracted video clips"""
    __tablename__ = "clips"
    
    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey("videos.id"))
    path = Column(String)
    start_time = Column(Float)
    end_time = Column(Float)
    duration = Column(Float)
    score = Column(Float, index=True)
    clip_metadata = Column(JSON)
    effects_applied = Column(JSON)
    hook_data = Column(JSON)
    prediction = Column(JSON)
    posted = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    posted_at = Column(DateTime, nullable=True)
    
    # Relationships
    video = relationship("Video", back_populates="clips")
    publications = relationship("Publication", back_populates="clip")
    
    # Indexes for <5ms queries
    __table_args__ = (
        Index('idx_clips_score_posted', 'score', 'posted'),
        Index('idx_clips_video_score', 'video_id', 'score'),
    )


class Publication(Base):
    """Published content tracking"""
    __tablename__ = "publications"
    
    id = Column(Integer, primary_key=True, index=True)
    clip_id = Column(Integer, ForeignKey("clips.id"))
    platform = Column(String)
    platform_post_id = Column(String)
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    engagement_rate = Column(Float, index=True)
    published_at = Column(DateTime, default=datetime.utcnow)
    last_update = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    clip = relationship("Clip", back_populates="publications")
    
    # Indexes
    __table_args__ = (
        Index('idx_publications_engagement', 'engagement_rate'),
        Index('idx_publications_platform_date', 'platform', 'published_at'),
    )


class Pattern(Base):
    """Learned patterns for AI agents"""
    __tablename__ = "patterns"
    
    id = Column(Integer, primary_key=True, index=True)
    pattern_type = Column(String, index=True)
    pattern_data = Column(JSON)
    confidence = Column(Float)
    usage_count = Column(Integer, default=0)
    success_rate = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used = Column(DateTime, nullable=True)
    
    __table_args__ = (
        Index('idx_patterns_type_confidence', 'pattern_type', 'confidence'),
    )


class Task(Base):
    """Background task tracking"""
    __tablename__ = "tasks"
    
    id = Column(String, primary_key=True)  # UUID
    task_type = Column(String)
    status = Column(String, index=True)
    input_data = Column(JSON)
    result_data = Column(JSON)
    error_message = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    __table_args__ = (
        Index('idx_tasks_status_created', 'status', 'created_at'),
    )


# Database initialization function
def init_db(db_path=None):
    """Initialize database with consistent path"""
    global engine, SessionLocal
    
    if not db_path:
        # First check environment variables
        db_path = os.getenv('DATABASE_PATH')
        
        if not db_path:
            # Use DATABASE_URL if set
            db_url = os.getenv('DATABASE_URL')
            if db_url and db_url.startswith('sqlite:///'):
                db_path = db_url.replace('sqlite:///', '')
        
        if not db_path:
            # Default to absolute path
            db_path = os.path.abspath('database/tiktok.db')
    
    # Ensure it's absolute
    db_path = os.path.abspath(db_path)
    
    # Log the path being used
    print(f"Database: Using path {db_path}")
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # Create engine with absolute path
    engine = create_engine(f'sqlite:///{db_path}', connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    return engine


# Create tables with default setup
Base.metadata.create_all(bind=engine)


# Database session helper
def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()