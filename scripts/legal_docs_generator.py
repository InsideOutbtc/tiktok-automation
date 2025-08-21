#!/usr/bin/env python3
"""
Legal Documents Generator for TikTok Fitness Brand
"""
import os

def generate_legal_docs(brand_name):
    """Generate all required legal documents"""
    
    # Create legal directory if it doesn't exist
    os.makedirs("legal", exist_ok=True)
    
    medical_disclaimer = f"""
# MEDICAL DISCLAIMER

The fitness content provided by {brand_name} is for informational and educational purposes only. It is not a substitute for professional medical advice, diagnosis, or treatment.

Always consult your physician or qualified health provider before beginning any exercise program. Never disregard professional medical advice or delay seeking it because of something you have seen in our content.

If you experience pain, dizziness, or discomfort during exercise, stop immediately and consult a medical professional.

{brand_name} assumes no responsibility for any injury or damage sustained by anyone using our content.
"""
    
    bio_text = f"""
# TIKTOK BIO OPTIONS (80 characters max)

Option 1 (78 chars):
🔥 Quick workouts that work | 15-30 secs | Beginner friendly | New daily 💪

Option 2 (79 chars):
Transform in 30 seconds ⚡ Daily workouts | Form tips | Join the movement 👇

Option 3 (80 chars):
Your daily fitness boost 💪 Quick & effective | No equipment needed | Start now

Option 4 (77 chars):
Fitness made simple 🎯 30-sec burns | Real results | Follow for daily tips

Option 5 (80 chars):
Stop scrolling, start moving! 🏃 Quick workouts | Form fixes | Results daily 📈
"""
    
    ftc_disclosure = f"""
# FTC DISCLOSURE TEMPLATES

## For Affiliate Posts:
"*This post contains affiliate links. I may earn a small commission if you purchase through my link, at no extra cost to you. I only recommend products I personally use and love! #ad #affiliate"

## For Sponsored Content:
"*Sponsored by [Brand]. All opinions are my own. Thank you [Brand] for partnering with {brand_name}! #sponsored #ad"

## For Gifted Products:
"*[Brand] gifted me this product to try. Not paid to post, just sharing my honest experience! #gifted"
"""
    
    privacy_policy = f"""
# PRIVACY POLICY

{brand_name} respects your privacy. This policy explains how we handle any information:

## Information Collection
- We do not collect personal information through our TikTok content
- Any interactions are handled through TikTok's platform
- We may track anonymous analytics for content improvement

## Use of Information
- Analytics are used to improve content quality
- We never sell or share personal information
- All data handling follows TikTok's privacy policies

## Contact
Questions about privacy? Reach out via TikTok DM.

Last updated: {__import__('datetime').datetime.now().strftime('%Y-%m-%d')}
"""
    
    terms_of_service = f"""
# TERMS OF SERVICE

By following and using content from {brand_name}, you agree to these terms:

## Content Usage
- All fitness content is for educational purposes only
- You assume all risks associated with exercise
- Consult a physician before starting any fitness program

## Intellectual Property
- All content is owned by {brand_name}
- You may share our content with proper attribution
- Commercial use requires written permission

## Liability
- We are not liable for any injuries or damages
- Use our content at your own risk
- Always prioritize your safety and health

## Changes
We may update these terms at any time. Continued use constitutes acceptance.
"""
    
    # Save all documents
    with open("legal/medical_disclaimer.md", "w") as f:
        f.write(medical_disclaimer)
    
    with open("bio_options.md", "w") as f:
        f.write(bio_text)
    
    with open("legal/ftc_disclosures.md", "w") as f:
        f.write(ftc_disclosure)
        
    with open("legal/privacy_policy.md", "w") as f:
        f.write(privacy_policy)
        
    with open("legal/terms_of_service.md", "w") as f:
        f.write(terms_of_service)
    
    print("✅ Legal documents generated!")
    return True

if __name__ == "__main__":
    # Default value for testing
    generate_legal_docs("FitMax")