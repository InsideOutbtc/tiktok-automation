#!/usr/bin/env python3
"""
Visual Assets Specification Generator
"""
import json
from datetime import datetime

def generate_visual_specs(brand_name, primary_color, secondary_color):
    """Generate specifications for all visual assets"""
    
    specs = {
        "logo": {
            "primary": {
                "dimensions": "1080x1080px",
                "format": "PNG with transparency",
                "style": "Bold, modern, readable at 50px",
                "colors": [primary_color, "white"],
                "variations": ["full", "icon", "wordmark"],
                "usage": "Profile picture, watermark base"
            }
        },
        "profile_picture": {
            "tiktok": {
                "dimensions": "200x200px",
                "format": "JPG",
                "design": f"{brand_name} logo on {primary_color} background",
                "border": "None"
            }
        },
        "watermark": {
            "video": {
                "dimensions": "150x50px",
                "format": "PNG with transparency",
                "opacity": "70%",
                "position": "bottom-right, 10px margin",
                "text": f"@{brand_name.lower()}"
            }
        },
        "video_templates": {
            "intro": {
                "duration": "2 seconds",
                "animation": "Fade in with pulse",
                "colors": [primary_color, secondary_color],
                "text": brand_name
            },
            "outro": {
                "duration": "3 seconds",
                "cta": "Follow for more!",
                "animation": "Slide up",
                "include": ["handle", "logo"]
            }
        },
        "thumbnail_templates": {
            "style_1": {
                "background": primary_color,
                "text_color": "white",
                "font": "Bold sans-serif",
                "elements": ["exercise name", "duration", "difficulty"]
            },
            "style_2": {
                "background": "gradient",
                "overlay": "black 50%",
                "text_color": secondary_color,
                "elements": ["before/after", "results", "testimonial"]
            }
        }
    }
    
    # Save specifications
    with open("visual_assets_specifications.json", "w") as f:
        json.dump(specs, f, indent=2)
    
    # Create Canva/Designer instructions
    instructions = f"""
# Visual Assets Creation Guide

## 1. Logo Design Instructions
- Open Canva or Adobe Express
- Create new design: 1080x1080px
- Search for "fitness logo templates"
- Customize with:
  - Brand name: {brand_name}
  - Primary color: {primary_color}
  - Style: Bold, modern, minimal
- Export as PNG with transparency

## 2. Quick Logo Options (if no designer):
1. Text-only logo:
   - Font: Montserrat Bold or Bebas Neue
   - Color: {primary_color}
   - Add small icon (dumbbell, flame, or lightning)

2. Initials logo:
   - Use first letters of {brand_name}
   - Geometric shape background
   - High contrast colors

## 3. Watermark Creation:
- Take logo
- Resize to 150x50px
- Set opacity to 70%
- Save as PNG

## 4. Free Tools to Use:
- Canva.com (free templates)
- Adobe Express (free version)
- Figma (free for personal)
- GIMP (open source)
- Photopea.com (browser-based)
"""
    
    with open("VISUAL_ASSETS_GUIDE.md", "w") as f:
        f.write(instructions)
    
    return specs

if __name__ == "__main__":
    # Default values for testing
    generate_visual_specs("FitMax", "#FF6B35", "#004E89")
    print("✅ Visual assets specifications generated!")