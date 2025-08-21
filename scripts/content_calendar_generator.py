#!/usr/bin/env python3
"""
30-Day Content Calendar Generator
"""
import json
import random
from datetime import datetime, timedelta

def generate_content_calendar(brand_name):
    """Generate 30 days of content with specific videos"""
    
    calendar = []
    start_date = datetime.now()
    
    # Video templates
    video_templates = {
        "morning_routine": {
            "title": "5-Minute Morning Wake-Up",
            "duration": "0:30",
            "hook": "Start your day strong in just 5 minutes!",
            "exercises": ["jumping jacks", "squats", "push-ups"],
            "hashtags": ["#morningworkout", "#5minuteworkout", "#morningroutine"]
        },
        "form_check": {
            "title": "You're Doing Squats WRONG",
            "duration": "0:45",
            "hook": "90% of people make this mistake...",
            "exercises": ["squat form correction"],
            "hashtags": ["#formcheck", "#squats", "#fitnesstips"]
        },
        "challenge": {
            "title": "30-Day Plank Challenge Day {day}",
            "duration": "0:15",
            "hook": "Can you hold for {seconds} seconds?",
            "exercises": ["plank hold"],
            "hashtags": ["#plankchallenge", "#30daychallenge", "#core"]
        },
        "transformation": {
            "title": "What 30 Days of {exercise} Did",
            "duration": "0:20",
            "hook": "The results shocked me...",
            "exercises": ["before/after showcase"],
            "hashtags": ["#transformation", "#results", "#beforeandafter"]
        },
        "quick_burn": {
            "title": "{bodypart} Burn in 30 Seconds",
            "duration": "0:30",
            "hook": "Feel the burn in just 30 seconds!",
            "exercises": ["targeted exercise"],
            "hashtags": ["#quickworkout", "#30seconds", "#burn"]
        }
    }
    
    # Generate 30 days
    for day in range(30):
        date = start_date + timedelta(days=day)
        
        # Determine video type based on day
        if day % 7 == 0:  # Monday
            video_type = "morning_routine"
            theme = "Motivation Monday"
        elif day % 7 == 4:  # Friday
            video_type = "form_check"
            theme = "Form Friday"
        elif day % 3 == 0:  # Every 3 days
            video_type = "challenge"
            theme = "Challenge Day"
        elif day % 5 == 0:  # Every 5 days
            video_type = "transformation"
            theme = "Transformation"
        else:
            video_type = "quick_burn"
            theme = "Daily Burn"
        
        template = video_templates[video_type].copy()
        
        # Customize template
        if video_type == "challenge":
            template["title"] = template["title"].format(day=day+1)
            template["hook"] = template["hook"].format(seconds=30+day)
        elif video_type == "transformation":
            exercises = ["push-ups", "squats", "planks", "burpees"]
            template["title"] = template["title"].format(exercise=random.choice(exercises))
        elif video_type == "quick_burn":
            bodyparts = ["abs", "glutes", "arms", "legs"]
            template["title"] = template["title"].format(bodypart=random.choice(bodyparts))
        
        calendar.append({
            "day": day + 1,
            "date": date.strftime("%Y-%m-%d"),
            "weekday": date.strftime("%A"),
            "theme": theme,
            "posts": [
                {
                    "time": "09:00",
                    "type": video_type,
                    "title": template["title"],
                    "duration": template["duration"],
                    "hook": template["hook"],
                    "hashtags": template["hashtags"] + [f"#{brand_name.lower()}"],
                    "status": "pending"
                }
            ]
        })
        
        # Add second post on high-engagement days
        if date.weekday() in [1, 4, 6]:  # Tuesday, Friday, Sunday
            calendar[-1]["posts"].append({
                "time": "18:00",
                "type": "evening_burn",
                "title": "Evening Quick Burn",
                "duration": "0:20",
                "hook": "End your day strong!",
                "hashtags": ["#eveningworkout", "#nightroutine", f"#{brand_name.lower()}"],
                "status": "pending"
            })
    
    # Save calendar
    with open("30_day_content_calendar.json", "w") as f:
        json.dump(calendar, f, indent=2)
    
    # Generate readable calendar
    readable_calendar = f"""
# 30-DAY CONTENT CALENDAR
Brand: @{brand_name.lower()}
Start Date: {start_date.strftime('%Y-%m-%d')}

## WEEK 1
"""
    for day in calendar[:7]:
        readable_calendar += f"\n**{day['weekday']} (Day {day['day']})**\n"
        for post in day['posts']:
            readable_calendar += f"- {post['time']}: {post['title']}\n"
            readable_calendar += f"  Hook: \"{post['hook']}\"\n"
    
    readable_calendar += "\n## POSTING SCHEDULE\n"
    readable_calendar += "- Primary Post: 9:00 AM daily\n"
    readable_calendar += "- Secondary Post: 6:00 PM (Tue, Fri, Sun)\n"
    readable_calendar += "\n## TOTAL CONTENT\n"
    total_posts = sum(len(day['posts']) for day in calendar)
    readable_calendar += f"- Total Posts: {total_posts}\n"
    readable_calendar += f"- Daily Average: {total_posts/30:.1f}\n"
    
    with open("CONTENT_CALENDAR.md", "w") as f:
        f.write(readable_calendar)
    
    return calendar

if __name__ == "__main__":
    # Default value for testing
    generate_content_calendar("FitMax")
    print("✅ Content calendar generated!")