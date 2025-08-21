#!/usr/bin/env python3
"""Process PowerPro logos for all use cases"""
from PIL import Image
import os

def process_logos():
    """Process the 3 PowerPro logos for different uses"""
    
    # Define logo files (in main directory)
    logos = {
        'with_words': 'Logo with words.png',
        'normal': 'Logo normal.png',
        'with_shade': 'Logo with shade.png'
    }
    
    # Create processed versions
    for name, filename in logos.items():
        if os.path.exists(filename):
            img = Image.open(filename)
            
            # Profile picture (200x200) - use shaded version
            if name == 'with_shade':
                profile = img.resize((200, 200), Image.Resampling.LANCZOS)
                profile.save('assets/logos/profile_200x200.png')
                
                # Also create 400x400 for higher quality
                profile_hq = img.resize((400, 400), Image.Resampling.LANCZOS)
                profile_hq.save('assets/logos/profile_400x400.png')
            
            # Watermark (white version with transparency)
            if name == 'normal':
                # Create watermark version
                watermark = img.convert('RGBA')
                # Make white version for overlays
                watermark.save('assets/watermarks/powerpro_watermark.png')
                
                # Create smaller watermark
                small_watermark = img.resize((150, 150), Image.Resampling.LANCZOS)
                small_watermark.save('assets/watermarks/powerpro_watermark_small.png')
            
            # Copy original to assets
            img.save(f'assets/logos/{name}.png')
    
    print("✅ Logos processed successfully")

if __name__ == "__main__":
    process_logos()