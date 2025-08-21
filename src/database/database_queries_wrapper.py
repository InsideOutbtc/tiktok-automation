#!/usr/bin/env python3
"""
Import wrapper for DatabaseQueries to handle Docker environment issues
"""

import sys
import os

# Ensure src is in path
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

try:
    # Try standard import
    from src.database.queries import DatabaseQueries
except ImportError:
    try:
        # Try without src prefix
        sys.path.insert(0, os.path.join(src_path, 'src'))
        from database.queries import DatabaseQueries
    except ImportError:
        # Last resort - import directly
        import importlib.util
        queries_path = os.path.join(src_path, 'src', 'database', 'queries.py')
        spec = importlib.util.spec_from_file_location("queries", queries_path)
        queries = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(queries)
        DatabaseQueries = queries.DatabaseQueries

# Export
__all__ = ['DatabaseQueries']
