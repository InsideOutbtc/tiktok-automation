"""Health check endpoint for monitoring"""
import os
import sqlite3
from datetime import datetime

def health_check():
    """Perform health check"""
    checks = {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'checks': {}
    }
    
    # Check database
    try:
        conn = sqlite3.connect('database/tiktok.db')
        conn.execute('SELECT 1')
        conn.close()
        checks['checks']['database'] = 'ok'
    except:
        checks['checks']['database'] = 'error'
        checks['status'] = 'unhealthy'
    
    # Check directories
    for dir_name in ['input', 'output', 'logs']:
        if os.path.exists(dir_name):
            checks['checks'][dir_name] = 'ok'
        else:
            checks['checks'][dir_name] = 'missing'
            checks['status'] = 'degraded'
    
    # Check API keys
    if os.getenv('YOUTUBE_API_KEY') and os.getenv('OPENAI_API_KEY'):
        checks['checks']['api_keys'] = 'configured'
    else:
        checks['checks']['api_keys'] = 'missing'
        checks['status'] = 'unhealthy'
    
    return checks