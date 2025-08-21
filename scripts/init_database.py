#!/usr/bin/env python3
"""
Initialize the SQLite database
"""

import sqlite3
import os

def init_database():
    """Initialize the database with all required tables"""
    
    db_path = 'database/tiktok_automation.db'
    os.makedirs('database', exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create videos table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS videos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        platform TEXT NOT NULL,
        video_id TEXT UNIQUE NOT NULL,
        title TEXT,
        url TEXT,
        views INTEGER,
        likes INTEGER,
        engagement_score REAL,
        download_status TEXT DEFAULT 'pending',
        local_path TEXT,
        processed BOOLEAN DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create clips table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS clips (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        video_id INTEGER,
        clip_number INTEGER,
        start_time REAL,
        end_time REAL,
        duration REAL,
        score REAL,
        title TEXT,
        description TEXT,
        hashtags TEXT,
        posted BOOLEAN DEFAULT 0,
        post_time TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (video_id) REFERENCES videos(id)
    )
    ''')
    
    # Create posts table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        clip_id INTEGER,
        platform TEXT,
        post_id TEXT,
        status TEXT,
        views INTEGER DEFAULT 0,
        likes INTEGER DEFAULT 0,
        comments INTEGER DEFAULT 0,
        engagement_rate REAL,
        posted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (clip_id) REFERENCES clips(id)
    )
    ''')
    
    # Create system_metrics table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS system_metrics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        metric_type TEXT,
        value REAL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create indexes for performance
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_videos_processed ON videos(processed)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_videos_platform ON videos(platform)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_clips_score ON clips(score DESC)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_clips_posted ON clips(posted)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_posts_platform ON posts(platform)')
    
    conn.commit()
    conn.close()
    
    print('✅ Database initialized successfully')

if __name__ == "__main__":
    init_database()