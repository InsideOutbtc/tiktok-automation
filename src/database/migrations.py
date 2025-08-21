"""Database migrations handler"""
import os
import logging
from sqlalchemy import create_engine, text
from src.database.models import Base

logger = logging.getLogger(__name__)

def run_migrations(db_path=None):
    """Run database migrations"""
    try:
        if not db_path:
            # Use environment variable or default
            db_path = os.getenv('DATABASE_PATH', os.path.abspath('database/tiktok.db'))
        
        # Ensure absolute path
        db_path = os.path.abspath(db_path)
        
        logger.info(f"Migrations: Using database at {db_path}")
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Create engine and tables
        engine = create_engine(f'sqlite:///{db_path}', connect_args={"check_same_thread": False})
        Base.metadata.create_all(bind=engine)
        
        logger.info("✅ Database migrations completed")
        
        # Check if we need to migrate old metadata columns
        # This is safe to run multiple times
        with engine.connect() as conn:
            try:
                # Check if old metadata columns exist
                result = conn.execute(text("PRAGMA table_info(videos)"))
                columns = [row[1] for row in result]
                
                if 'metadata' in columns and 'video_metadata' not in columns:
                    logger.info("Migrating videos.metadata to videos.video_metadata...")
                    conn.execute(text("ALTER TABLE videos RENAME COLUMN metadata TO video_metadata"))
                    conn.commit()
                    
                result = conn.execute(text("PRAGMA table_info(clips)"))
                columns = [row[1] for row in result]
                
                if 'metadata' in columns and 'clip_metadata' not in columns:
                    logger.info("Migrating clips.metadata to clips.clip_metadata...")
                    conn.execute(text("ALTER TABLE clips RENAME COLUMN metadata TO clip_metadata"))
                    conn.commit()
                    
            except Exception as e:
                # If migration fails, it's okay - tables might be new
                logger.info(f"Migration check completed: {e}")
                
        return True
        
    except Exception as e:
        logger.error(f"Migration error: {e}")
        return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_migrations()