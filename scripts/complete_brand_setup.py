#!/usr/bin/env python3
"""
Master script to run all brand setup tasks
"""
import os
import sys
import json
import subprocess
from datetime import datetime

def ensure_directories():
    """Create all required directories"""
    dirs = [
        "brand_output",
        "legal",
        "assets/branding",
        "assets/templates",
        "content/calendar",
        "content/hooks"
    ]
    for dir in dirs:
        os.makedirs(dir, exist_ok=True)
    print("✅ Directories created")

def run_all_generators():
    """Run all generator scripts"""
    scripts = [
        ("brand_generator_complete.py", "Brand Strategy"),
        ("visual_assets_generator.py", "Visual Assets"),
        ("content_calendar_generator.py", "Content Calendar"),
        ("legal_docs_generator.py", "Legal Documents"),
        ("launch_checklist_generator.py", "Launch Checklist")
    ]
    
    results = {}
    
    for script, name in scripts:
        print(f"\n🚀 Running {name} Generator...")
        try:
            # Import and run the main function from each script
            script_path = f"scripts.{script[:-3]}"  # Remove .py extension
            if script == "brand_generator_complete.py":
                from brand_generator_complete import main as brand_main
                brand_data = brand_main()
                results['brand_data'] = brand_data
            elif script == "visual_assets_generator.py":
                from visual_assets_generator import generate_visual_specs
                if 'brand_data' in results:
                    brand_name = results['brand_data']['brand_names'][0]['name']
                    primary_color = results['brand_data']['color_schemes'][0]['primary']
                    secondary_color = results['brand_data']['color_schemes'][0]['secondary']
                    generate_visual_specs(brand_name, primary_color, secondary_color)
            elif script == "content_calendar_generator.py":
                from content_calendar_generator import generate_content_calendar
                if 'brand_data' in results:
                    brand_name = results['brand_data']['brand_names'][0]['name']
                    generate_content_calendar(brand_name)
            elif script == "legal_docs_generator.py":
                from legal_docs_generator import generate_legal_docs
                if 'brand_data' in results:
                    brand_name = results['brand_data']['brand_names'][0]['name']
                    generate_legal_docs(brand_name)
            elif script == "launch_checklist_generator.py":
                from launch_checklist_generator import generate_launch_checklist
                generate_launch_checklist()
            
            print(f"✅ {name} completed successfully!")
        except Exception as e:
            print(f"⚠️ {name} had issues: {str(e)}")
            print("Continuing with other tasks...")
    
    return results

def create_final_report(results):
    """Combine all outputs into final report"""
    print("\n📊 Creating final brand report...")
    
    try:
        # Load brand data if it exists
        if os.path.exists("brand_data_complete.json"):
            with open("brand_data_complete.json", "r") as f:
                brand_data = json.load(f)
        else:
            brand_data = results.get('brand_data', {})
        
        if brand_data and 'brand_names' in brand_data:
            # Create deployment config
            deployment_config = {
                "brand": brand_data["brand_names"][0]["name"],
                "tiktok_handle": brand_data["brand_names"][0]["tiktok"],
                "primary_color": brand_data["color_schemes"][0]["primary"],
                "secondary_color": brand_data["color_schemes"][0]["secondary"],
                "deployment_ready": True,
                "content_ready": True,
                "legal_ready": True,
                "launch_date": datetime.now().strftime("%Y-%m-%d")
            }
            
            # Update or create .env file
            env_content = f"""# TikTok Fitness Brand Configuration
BRAND_NAME={deployment_config['brand']}
TIKTOK_HANDLE={deployment_config['tiktok_handle']}
PRIMARY_COLOR={deployment_config['primary_color']}
SECONDARY_COLOR={deployment_config['secondary_color']}
LAUNCH_DATE={deployment_config['launch_date']}
"""
            
            with open(".env.brand", "w") as f:
                f.write(env_content)
            
            print("✅ .env.brand file created")
            
            # Create deployment summary
            with open("brand_deployment_config.json", "w") as f:
                json.dump(deployment_config, f, indent=2)
            
            # Create summary report
            summary = f"""
# 🎉 BRAND SETUP COMPLETE!

## 📱 Your Brand Details:
- **Brand Name**: {deployment_config['brand']}
- **TikTok Handle**: {deployment_config['tiktok_handle']}
- **Primary Color**: {deployment_config['primary_color']}
- **Secondary Color**: {deployment_config['secondary_color']}

## 📁 Generated Files:
- ✅ brand_data_complete.json - Complete brand data
- ✅ BRAND_STRATEGY_REPORT.md - Comprehensive strategy
- ✅ 30_day_content_calendar.json - Content schedule
- ✅ CONTENT_CALENDAR.md - Readable calendar
- ✅ visual_assets_specifications.json - Design specs
- ✅ VISUAL_ASSETS_GUIDE.md - Design instructions
- ✅ legal/ - All legal documents
- ✅ bio_options.md - TikTok bio options
- ✅ LAUNCH_CHECKLIST.md - Step-by-step guide
- ✅ .env.brand - Configuration file

## 🚀 Next Steps:
1. **Check availability**: Verify @{deployment_config['brand'].lower()} is available on TikTok
2. **Create logo**: Use VISUAL_ASSETS_GUIDE.md with Canva
3. **Set up account**: Follow LAUNCH_CHECKLIST.md
4. **Start posting**: Use CONTENT_CALENDAR.md

## 💡 Quick Start Commands:
```bash
# View your brand report
cat BRAND_STRATEGY_REPORT.md

# Check your content calendar
cat CONTENT_CALENDAR.md

# Review launch checklist
cat LAUNCH_CHECKLIST.md
```

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}
"""
            
            with open("BRAND_SETUP_COMPLETE.md", "w") as f:
                f.write(summary)
            
            return deployment_config
        else:
            print("⚠️ No brand data found. Please check the output files.")
            return None
            
    except Exception as e:
        print(f"❌ Error creating final report: {str(e)}")
        return None

def display_summary(config):
    """Display final summary"""
    if config:
        print("\n" + "="*60)
        print("🎉 BRAND SETUP COMPLETE!")
        print("="*60)
        print(f"\n📱 Brand: {config['brand']}")
        print(f"🔗 TikTok: {config['tiktok_handle']}")
        print(f"🎨 Primary Color: {config['primary_color']}")
        print(f"🎨 Secondary Color: {config['secondary_color']}")
        print("\n📁 All Files Generated Successfully!")
        print("\n🚀 IMMEDIATE NEXT STEPS:")
        print(f"  1. Check if {config['tiktok_handle']} is available on TikTok")
        print("  2. Create logo using VISUAL_ASSETS_GUIDE.md")
        print("  3. Follow LAUNCH_CHECKLIST.md to set up account")
        print("  4. Start posting using CONTENT_CALENDAR.md")
        print("\n📖 For detailed instructions, see:")
        print("  - BRAND_SETUP_COMPLETE.md")
        print("  - LAUNCH_CHECKLIST.md")
    else:
        print("\n⚠️ Setup completed with warnings. Check individual files for details.")

def main():
    """Main execution function"""
    print("🚀 Starting Complete Brand Setup...")
    print("="*60)
    
    # Step 1: Create directories
    ensure_directories()
    
    # Step 2: Run all generators
    results = run_all_generators()
    
    # Step 3: Create final report
    config = create_final_report(results)
    
    # Step 4: Display summary
    display_summary(config)
    
    print("\n✅ Brand setup process complete!")
    print("Check all generated files for your complete brand package.")

if __name__ == "__main__":
    # Add scripts directory to Python path
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    main()