#!/usr/bin/env python3
"""Test database path consistency"""
import os
import sys

# Set path
DB_PATH = os.path.abspath('database/tiktok.db')
os.environ['DATABASE_PATH'] = DB_PATH
os.environ['DATABASE_URL'] = f'sqlite:///{DB_PATH}'

print(f"Test: DATABASE_PATH = {os.getenv('DATABASE_PATH')}")
print(f"Test: DATABASE_URL = {os.getenv('DATABASE_URL')}")
print(f"Test: Absolute path = {DB_PATH}")

# Test import
try:
    from src.database.models import init_db
    engine = init_db()
    print("✅ Database initialized successfully")
except Exception as e:
    print(f"❌ Error: {e}")