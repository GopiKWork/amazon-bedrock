#!/usr/bin/env python3
"""
Setup script for multimodal patterns notebook
This ensures all imports work correctly in Jupyter
"""

import sys
import os

# Store original working directory
original_cwd = os.getcwd()

# Get the parent directory (project root)
parent_dir = os.path.dirname(os.getcwd())

# Add the parent directory to the path
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

print(f"✅ Added to Python path: {parent_dir}")

# Change working directory to parent so data files can be found
os.chdir(parent_dir)
print(f"✅ Changed working directory from {original_cwd} to: {os.getcwd()}")

# Test imports
try:
    from mm_index import MMIngestor, ImageResizer
    from config import REGION_NAME, MULTIMODAL_DAMAGE_DATA_FILE, DEALER_ESCALATION_FILE, IMAGES_DIR
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from utils import get_standard_names, load_json_data, load_text_data
    print("All imports successful!")
    print(f"Region: {REGION_NAME}")
    print(f"Images directory: {IMAGES_DIR}")
    
    # Test data file access
    if os.path.exists(MULTIMODAL_DAMAGE_DATA_FILE):
        print(f"Found data file: {MULTIMODAL_DAMAGE_DATA_FILE}")
    else:
        print(f"Data file not found: {MULTIMODAL_DAMAGE_DATA_FILE}")
        print(f"   Current directory: {os.getcwd()}")
        print(f"   Looking for: {os.path.abspath(MULTIMODAL_DAMAGE_DATA_FILE)}")
        
except Exception as e:
    print(f"Import error: {e}")
    raise
    if os.path.exists(DEALER_ESCALATION_FILE):
        print(f"✅ Found escalation file: {DEALER_ESCALATION_FILE}")
    else:
        print(f"❌ Escalation file not found: {DEALER_ESCALATION_FILE}")
        
    # Check images directory
    if os.path.exists(IMAGES_DIR):
        image_count = len([f for f in os.listdir(IMAGES_DIR) if f.endswith('.jpeg')])
        print(f"✅ Found images directory with {image_count} JPEG files")
    else:
        print(f"❌ Images directory not found: {IMAGES_DIR}")
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please ensure you're running from the multimodal_patterns directory")
    print("and that the parent directory contains mm_index, config.py, and utils.py")
except Exception as e:
    print(f"❌ Setup error: {e}")
    
print("\\n" + "="*50)
print("Setup complete! You can now run the notebook cells.")