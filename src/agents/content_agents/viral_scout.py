# Viral Scout Agent with OpenAI Integration
# Identifies viral potential using AI analysis

import os
import asyncio
from typing import Dict, List, Any, Optional
import logging
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
logger = logging.getLogger(__name__)


class ViralScoutAgent:
    """AI agent that scouts for viral content potential"""

    def __init__(self):
        self.name = "ViralScout"
        self.viral_patterns = []
        self.min_viral_score = 0.7

        # OpenAI integration v1.0+
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if self.openai_api_key:
            try:
                self.client = OpenAI(api_key=self.openai_api_key)
                self.enabled = True
                logger.info("✅ ViralScout: OpenAI v1.0+ initialized")
            except Exception as e:
                logger.warning("OpenAI init failed: %s, using rule-based" % e)
                self.client = None
                self.enabled = False
        else:
            logger.info("ViralScout: Using rule-based analysis (no OpenAI key)")
            self.client = None
            self.enabled = False

    async def initialize(self):
        """Initialize the viral scout agent"""
        logger.info("Initializing Viral Scout Agent")
        # Load pre-trained patterns
        self.viral_patterns = [
            {"feature": "hook_quality", "weight": 0.3},
            {"feature": "trend_alignment", "weight": 0.25},
            {"feature": "emotional_impact", "weight": 0.2},
            {"feature": "visual_quality", "weight": 0.15},
            {"feature": "audio_sync", "weight": 0.1}
        ]
        return True

    async def analyze(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze content for viral potential using AI or rules"""
        if self.enabled and self.client:
            return await self.analyze_with_ai(content)
        else:
            return self._rule_based_analysis(content)

    async def analyze_batch(self, content_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze multiple content items for viral potential"""
        tasks = [self.analyze(item) for item in content_items]
        return await asyncio.gather(*tasks)

    async def analyze_with_ai(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Use GPT to analyze viral potential"""
        try:
            # Build context for AI analysis
            context = f"""
            Platform: {content.get('platform', 'unknown')}
            Title: {content.get('title', '')[:200]}
            Views: {content.get('views', 0):,}
            Likes: {content.get('likes', 0):,}
            Comments: {content.get('comments', 0):,}
            Duration: {content.get('duration', 0)} seconds
            Engagement Rate: {content.get('engagement_score', 0):.2%}
            """

            prompt = f"""As a viral content expert specializing in fitness content, analyze this video's viral potential.

{context}

Provide:
1. A viral potential score from 0-1
2. The TOP viral factor (one of: hook_quality, trend_alignment, emotional_impact, visual_appeal, audio_sync)
3. A brief explanation (max 50 words)

Format: SCORE: X.XX | FACTOR: factor_name | REASON: explanation"""

            # OpenAI v1.0+ API call
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert at predicting viral fitness content."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100,
                temperature=0.3
            )

            # Parse AI response
            ai_output = response.choices[0].message.content

            result = {
                "score": 0.5,  # Default
                "top_factor": "unknown",
                "reason": "AI analysis"
            }

            # Extract score
            if "SCORE:" in ai_output:
                try:
                    score_str = ai_output.split("SCORE:")[1].split("|")[0].strip()
                    result["score"] = float(score_str)
                except:
                    pass

            # Extract factor
            if "FACTOR:" in ai_output:
                try:
                    result["top_factor"] = ai_output.split("FACTOR:")[1].split("|")[0].strip()
                except:
                    pass

            # Extract reason
            if "REASON:" in ai_output:
                try:
                    result["reason"] = ai_output.split("REASON:")[1].strip()
                except:
                    pass

            # Add AI insights to content
            content["viral_score"] = result["score"]
            content["viral_analysis"] = {
                "method": "ai",
                "top_factor": result["top_factor"],
                "reason": result["reason"],
                "features": self._extract_features(content)
            }

            return result

        except Exception as e:
            logger.error(f"OpenAI analysis error: {e}")
            # Fallback to rule-based
            return self._rule_based_analysis(content)

    def _rule_based_analysis(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback rule-based analysis"""
        # Calculate viral score based on features
        score = 0.0
        factors = []

        # Platform-specific scoring
        if content.get("platform") == "tiktok":
            score += 0.1
            factors.append("platform_bonus")

        # Engagement metrics scoring
        views = content.get("views", 0)
        likes = content.get("likes", 0)

        if views > 100000:
            score += 0.2
            factors.append("high_views")

        if views > 0 and likes / views > 0.1:
            score += 0.15
            factors.append("high_engagement")

        # Duration scoring (optimal: 15-30 seconds)
        duration = content.get("duration", 0)
        if 15 <= duration <= 30:
            score += 0.2
            factors.append("optimal_duration")
        elif 30 < duration <= 60:
            score += 0.1

        # Recent and trending
        if content.get("published_at"):
            score += 0.1
            factors.append("recent_content")

        # Cap at 1.0
        final_score = min(score, 1.0)

        # Determine top factor
        factor_weights = {
            "high_engagement": 0.3,
            "high_views": 0.25,
            "optimal_duration": 0.2,
            "recent_content": 0.15,
            "platform_bonus": 0.1
        }

        top_factor = max(
            (f for f in factors if f in factor_weights),
            key=lambda x: factor_weights[x],
            default="trend_alignment"
        )

        return {
            "score": final_score,
            "top_factor": top_factor,
            "reason": f"Rule-based scoring: {', '.join(factors)}",
            "method": "rules"
        }

    def _extract_features(self, content: Dict[str, Any]) -> Dict[str, float]:
        """Extract viral features from content"""
        views = content.get("views", 1)
        likes = content.get("likes", 0)
        comments = content.get("comments", 0)
        shares = content.get("shares", 0)
        duration = content.get("duration", 0)

        return {
            "engagement_rate": likes / max(views, 1),
            "share_rate": shares / max(views, 1),
            "comment_rate": comments / max(views, 1),
            "optimal_duration": 1.0 if 15 <= duration <= 30 else 0.5,
            "viral_velocity": min(views / 1000000, 1.0)  # Normalized view count
        }

    async def predict_performance(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Predict future performance using AI"""
        if not self.enabled or not self.client:
            return {
                "predicted_views": content.get("views", 0) * 2,
                "confidence": 0.5,
                "method": "simple_projection"
            }

        try:
            prompt = f"""Based on these metrics, predict the video's performance in 7 days:

Current Views: {content.get('views', 0):,}
Current Likes: {content.get('likes', 0):,}
Engagement Rate: {content.get('engagement_score', 0):.2%}
Platform: {content.get('platform')}
Age: New

Provide predicted views and confidence (0-1).
Format: VIEWS: number | CONFIDENCE: X.XX"""

            # OpenAI v1.0+ API call
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=50,
                temperature=0.3
            )

            output = response.choices[0].message.content

            predicted_views = content.get("views", 0) * 2  # Default
            confidence = 0.7

            if "VIEWS:" in output:
                try:
                    views_str = output.split("VIEWS:")[1].split("|")[0].strip()
                    predicted_views = int(views_str.replace(",", ""))
                except:
                    pass

            if "CONFIDENCE:" in output:
                try:
                    confidence = float(output.split("CONFIDENCE:")[1].strip())
                except:
                    pass

            return {
                "predicted_views": predicted_views,
                "confidence": confidence,
                "method": "ai_prediction"
            }

        except Exception as e:
            logger.error(f"Performance prediction error: {e}")
            return {
                "predicted_views": content.get("views", 0) * 2,
                "confidence": 0.5,
                "method": "fallback"
            }

    async def update_patterns(self, new_patterns: List[Dict[str, Any]]):
        """Update viral detection patterns"""
        logger.info(f"Updating viral patterns with {len(new_patterns)} new patterns")
        self.viral_patterns.extend(new_patterns)
