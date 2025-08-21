# Hook Writer Agent with OpenAI Integration
# Generates viral hooks and metadata using AI

import os
import asyncio
from typing import Dict, List, Any
import logging
import random
from dotenv import load_dotenv
import openai

load_dotenv()
logger = logging.getLogger(__name__)


class HookWriterAgent:
    """AI agent that writes engaging hooks and metadata for clips"""
    
    def __init__(self):
        self.name = "HookWriter"
        self.hook_templates = []
        self.hashtag_database = []
        self.emoji_bank = ["💪", "🔥", "⚡", "🎯", "💯", "🚀", "⭐", "✨"]
        
        # OpenAI integration
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
            logger.info("HookWriter: OpenAI integration enabled")
        else:
            logger.info("HookWriter: Using template-based generation (no OpenAI key)")
            
    async def initialize(self):
        """Initialize the hook writer agent"""
        logger.info("Initializing Hook Writer Agent")
        
        # Load hook templates for fallback
        self.hook_templates = [
            "This {adjective} transformation will {action} you {emoji}",
            "POV: You {action} in just {timeframe} {emoji}",
            "The {number} {noun} that changed everything {emoji}",
            "Why nobody talks about this {noun} hack {emoji}",
            "I tried {action} for {timeframe} and THIS happened {emoji}",
            "{emoji} Watch till the end for the {adjective} results",
            "Stop scrolling if you want to {goal} {emoji}"
        ]
        
        # Load trending hashtags
        self.hashtag_database = [
            "#fitness", "#workout", "#transformation", "#gym", "#fitnessmotivation",
            "#bodybuilding", "#health", "#fitfam", "#training", "#muscle",
            "#fitnessjourney", "#gymmotivation", "#fitnessgoals", "#weightloss",
            "#nutrition", "#exercise", "#healthylifestyle", "#fitnessaddict"
        ]
        
        return True
        
    async def generate_metadata(self, clip: Dict[str, Any]) -> Dict[str, Any]:
        """Generate complete metadata for a clip"""
        if self.openai_api_key:
            return await self._generate_with_ai(clip)
        else:
            return await self._generate_with_templates(clip)
            
    async def _generate_with_ai(self, clip: Dict[str, Any]) -> Dict[str, Any]:
        """Generate metadata using OpenAI"""
        try:
            # Build context
            context = f"""
            Platform: {clip.get('platform', 'TikTok')}
            Video Type: {clip.get('type', 'fitness transformation')}
            Duration: {clip.get('duration', 30)} seconds
            Original Title: {clip.get('original_title', '')[:100]}
            Viral Score: {clip.get('viral_score', 0.8):.1f}
            """
            
            prompt = f"""You are a viral content expert. Create engaging metadata for this fitness video:

{context}

Generate:
1. TITLE: A viral-worthy title (max 60 chars)
2. HOOK: Text overlay for first 3 seconds (max 20 chars, all caps)
3. DESCRIPTION: Engaging description (2-3 sentences)
4. HASHTAGS: 10 relevant hashtags (mix popular and niche)
5. CTA: Call-to-action (one sentence)

Format each section clearly."""

            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert at creating viral fitness content."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.8
            )
            
            # Parse AI response
            ai_output = response.choices[0].message.content
            
            metadata = {
                "title": self._extract_section(ai_output, "TITLE", self._generate_title_fallback(clip)),
                "hook_text": self._extract_section(ai_output, "HOOK", "WATCH THIS"),
                "description": self._extract_section(ai_output, "DESCRIPTION", self._generate_description_fallback(clip)),
                "hashtags": self._extract_hashtags(ai_output),
                "call_to_action": self._extract_section(ai_output, "CTA", "Follow for more! 💪"),
                "generated_by": "ai"
            }
            
            # Add emojis to title if missing
            if not any(emoji in metadata["title"] for emoji in self.emoji_bank):
                metadata["title"] += f" {random.choice(self.emoji_bank)}"
                
            return metadata
            
        except Exception as e:
            logger.error(f"OpenAI metadata generation error: {e}")
            return await self._generate_with_templates(clip)
            
    def _extract_section(self, text: str, section: str, default: str) -> str:
        """Extract a section from AI response"""
        try:
            if f"{section}:" in text:
                lines = text.split('\n')
                for i, line in enumerate(lines):
                    if f"{section}:" in line:
                        # Get the content after the section marker
                        content = line.split(f"{section}:")[1].strip()
                        if content:
                            return content
                        # Check next line if current is empty
                        elif i + 1 < len(lines):
                            return lines[i + 1].strip()
            return default
        except:
            return default
            
    def _extract_hashtags(self, text: str) -> List[str]:
        """Extract hashtags from AI response"""
        try:
            if "HASHTAGS:" in text:
                hashtag_line = text.split("HASHTAGS:")[1].split("\n")[0]
                # Extract all hashtags
                import re
                hashtags = re.findall(r'#\w+', hashtag_line)
                if len(hashtags) >= 5:
                    return hashtags[:15]  # Max 15 hashtags
                    
        except:
            pass
            
        # Fallback to database
        return random.sample(self.hashtag_database[:10], 5) + random.sample(self.hashtag_database[10:], 5)
        
    async def _generate_with_templates(self, clip: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback template-based generation"""
        return {
            "title": self._generate_title_fallback(clip),
            "description": self._generate_description_fallback(clip),
            "hashtags": await self._generate_hashtags_fallback(clip),
            "hook_text": await self._generate_hook_text_fallback(clip),
            "call_to_action": await self._generate_cta_fallback(clip),
            "generated_by": "templates"
        }
        
    def _generate_title_fallback(self, clip: Dict[str, Any]) -> str:
        """Generate title using templates"""
        templates = [
            f"Insane {random.choice(['30-Day', '60-Day', '90-Day'])} Transformation Results",
            f"This One Exercise Changed My {random.choice(['Life', 'Body', 'Fitness Game'])}",
            f"Why I {random.choice(['Started', 'Never Skip', 'Love'])} This Workout",
            f"{random.choice(['Secret', 'Hidden', 'Unknown'])} Technique Pros Use",
            f"From {random.choice(['Beginner', 'Zero', 'Couch'])} to {random.choice(['Hero', 'Pro', 'Beast'])}"
        ]
        
        title = random.choice(templates)
        emoji = random.choice(self.emoji_bank)
        
        return f"{title} {emoji}"
        
    def _generate_description_fallback(self, clip: Dict[str, Any]) -> str:
        """Generate description using templates"""
        intros = [
            "I can't believe the results from this workout routine!",
            "After trying everything, THIS finally worked.",
            "Game changer alert! This method is incredible.",
            "You won't believe what happened when I tried this.",
            "The transformation speaks for itself!"
        ]
        
        tips = [
            "Save this for your next workout",
            "Follow for more fitness tips",
            "Drop a 💪 if you're ready to transform",
            "Comment your goals below",
            "Share with someone who needs to see this"
        ]
        
        return f"{intros[random.randrange(len(intros))]}\n\n{tips[random.randrange(len(tips))]}"
        
    async def _generate_hashtags_fallback(self, clip: Dict[str, Any]) -> List[str]:
        """Generate hashtags using database"""
        # Mix of popular and niche hashtags
        popular = random.sample(self.hashtag_database[:10], 5)
        niche = random.sample(self.hashtag_database[10:], 5)
        
        # Add clip-specific hashtags
        if clip.get("type") == "energy_peak":
            niche.append("#intenseworkout")
        elif clip.get("type") == "transformation":
            niche.append("#beforeandafter")
            
        return popular + niche
        
    async def _generate_hook_text_fallback(self, clip: Dict[str, Any]) -> str:
        """Generate hook text using templates"""
        hooks = [
            "WAIT FOR IT...",
            "THIS CHANGED EVERYTHING",
            "YOU'RE NOT READY FOR THIS",
            "IMPOSSIBLE? WATCH THIS",
            "THE RESULTS? INSANE."
        ]
        
        return random.choice(hooks)
        
    async def _generate_cta_fallback(self, clip: Dict[str, Any]) -> str:
        """Generate call-to-action using templates"""
        ctas = [
            "Follow for daily fitness tips! 💪",
            "Save this workout for later! 📌",
            "Tag someone who needs this! 👇",
            "Drop a ❤️ if this motivated you!",
            "What's your fitness goal? Comment below! 💬"
        ]
        
        return random.choice(ctas)
        
    async def optimize_for_platform(self, metadata: Dict[str, Any], platform: str) -> Dict[str, Any]:
        """Optimize metadata for specific platform"""
        if platform == "tiktok":
            # TikTok specific optimizations
            metadata["title"] = metadata["title"][:100]  # TikTok limit
            metadata["hashtags"] = metadata["hashtags"][:30]  # Max hashtags
            
        elif platform == "youtube":
            # YouTube specific optimizations
            metadata["title"] = metadata["title"][:60]  # YouTube limit
            # Add YouTube-specific tags
            metadata["tags"] = [tag.replace("#", "") for tag in metadata["hashtags"]]
            
        return metadata