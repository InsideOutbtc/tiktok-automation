#!/bin/bash

echo "Testing DatabaseQueries import fix..."
echo "=================================================="

# Test 1: Direct import test
echo -e "\n1. Testing direct import:"
python3 -c "
try:
    from src.database.queries import DatabaseQueries
    print('✅ DatabaseQueries import successful')
    db = DatabaseQueries()
    print('✅ DatabaseQueries instantiation successful')
except Exception as e:
    print(f'❌ Error: {e}')
"

# Test 2: Check class methods
echo -e "\n2. Testing DatabaseQueries methods:"
python3 -c "
try:
    from src.database.queries import DatabaseQueries
    db = DatabaseQueries()
    methods = ['create_clip', 'get_unpublished_clips', 'update_clip', 'get_performance_data']
    for method in methods:
        if hasattr(db, method):
            print(f'✅ Method {method} exists')
        else:
            print(f'❌ Method {method} missing')
except Exception as e:
    print(f'❌ Error: {e}')
"

# Test 3: Check models
echo -e "\n3. Testing database models:"
python3 -c "
try:
    from src.database.models import Video, Clip, Publication, get_session
    print('✅ All models imported successfully')
    
    # Test to_dict methods
    clip = Clip()
    if hasattr(clip, 'to_dict'):
        print('✅ Clip.to_dict method exists')
    else:
        print('❌ Clip.to_dict method missing')
        
except Exception as e:
    print(f'❌ Error: {e}')
"

# Test 4: Main controller import
echo -e "\n4. Testing main_controller import:"
python3 -c "
import os
os.environ['DATABASE_PATH'] = os.path.abspath('database/tiktok.db')
try:
    from src.core.main_controller import MainController
    print('✅ MainController import successful')
    controller = MainController()
    print('✅ MainController instantiation successful')
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()
"

echo -e "\n=================================================="
echo "Verification complete!"