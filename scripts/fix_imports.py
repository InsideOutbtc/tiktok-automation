#!/usr/bin/env python3
"""
Fix any import issues in the codebase
"""

import os
import re
from pathlib import Path

def fix_imports():
    """Fix common import issues"""
    
    fixes_applied = []
    
    # Fix patterns
    patterns = [
        # Fix relative imports
        (r'from agents\.', 'from src.agents.'),
        (r'from core\.', 'from src.core.'),
        (r'from database\.', 'from src.database.'),
        (r'from mcp\.', 'from src.mcp.'),
        (r'from utils\.', 'from src.utils.'),
        
        # Fix optional imports
        (r'^import whisper$', 'try:\n    import whisper\nexcept ImportError:\n    whisper = None'),
        (r'^import torch$', 'try:\n    import torch\nexcept ImportError:\n    torch = None'),
    ]
    
    # Process all Python files
    for py_file in Path('src').rglob('*.py'):
        try:
            content = py_file.read_text()
            original = content
            
            for pattern, replacement in patterns:
                content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
            
            if content != original:
                py_file.write_text(content)
                fixes_applied.append(str(py_file))
        except Exception as e:
            print(f"  ⚠️  Error processing {py_file}: {e}")
    
    # Also process scripts
    for py_file in Path('scripts').rglob('*.py'):
        if py_file.name in ['fix_imports.py', '__pycache__']:
            continue
            
        try:
            content = py_file.read_text()
            original = content
            
            # Add src to path if not present
            if 'sys.path' not in content and 'from src.' in content:
                # Find where imports start
                lines = content.split('\n')
                import_index = 0
                for i, line in enumerate(lines):
                    if line.startswith('import ') or line.startswith('from '):
                        import_index = i
                        break
                
                # Insert path fix before imports
                import_block = '''import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

'''
                lines.insert(import_index, import_block)
                content = '\n'.join(lines)
                
                py_file.write_text(content)
                fixes_applied.append(str(py_file))
        except Exception as e:
            print(f"  ⚠️  Error processing {py_file}: {e}")
    
    return fixes_applied

if __name__ == "__main__":
    print("🔧 Fixing import issues...")
    fixes = fix_imports()
    
    if fixes:
        print(f"✅ Fixed {len(fixes)} files:")
        for file in fixes:
            print(f"   - {file}")
    else:
        print("✅ No import issues found")