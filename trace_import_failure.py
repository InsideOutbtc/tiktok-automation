#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Trace the exact import failure"""
import os
import sys
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Set up the same environment as start.py
DB_PATH = os.path.abspath('database/tiktok.db')
os.environ['DATABASE_URL'] = 'sqlite:///' + DB_PATH
os.environ['DATABASE_PATH'] = DB_PATH

logger.info("Environment setup:")
logger.info("  DATABASE_PATH: %s", os.getenv('DATABASE_PATH'))
logger.info("  DATABASE_URL: %s", os.getenv('DATABASE_URL'))
logger.info("  DB file exists: %s", os.path.exists(DB_PATH))

# Trace each import step
try:
    logger.info("1. Importing migrations...")
    from src.database.migrations import run_migrations
    logger.info("SUCCESS: Migrations imported successfully")
    
    logger.info("2. Running migrations...")
    result = run_migrations(DB_PATH)
    logger.info("SUCCESS: Migrations result: %s", result)
    
    logger.info("3. Importing main_wrapper...")
    from src.core.main_wrapper import main as run_automation
    logger.info("SUCCESS: main_wrapper imported successfully")
    
    logger.info("4. Importing main_controller directly...")
    from src.core.main_controller import main as async_main
    logger.info("SUCCESS: main_controller imported successfully")
    
    logger.info("5. Importing DatabaseQueries directly...")
    from src.database.queries import DatabaseQueries
    logger.info("SUCCESS: DatabaseQueries imported successfully")
    
    logger.info("6. Creating DatabaseQueries instance...")
    db = DatabaseQueries()
    logger.info("SUCCESS: DatabaseQueries instance created")
    
except ImportError as e:
    logger.error("FAILED: Import error at step: %s", e)
    logger.error("   Full traceback:", exc_info=True)
    
except Exception as e:
    logger.error("FAILED: Other error: %s", e)
    logger.error("   Full traceback:", exc_info=True)

logger.info("Trace complete.")