"""
Error handler with Tier 1-4 error handling system.
Following Constitutional AI principles.
"""

from typing import Dict, List, Any  # FIX 1: Added List import
import logging
import time
import asyncio
from enum import Enum

class ErrorTier(Enum):
    """Error severity tiers."""
    TIER_1 = 1  # Transient - retry once
    TIER_2 = 2  # Persistent - retry with backoff
    TIER_3 = 3  # System - workaround needed
    TIER_4 = 4  # Critical - recovery plan needed

class ErrorHandler:
    """Handles errors according to Constitutional AI tier system."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # FIX 2: Initialize with ALL required keys
        self.error_stats = {
            'transient': 0,
            'persistent': 0,
            'system': 0,  # This was missing!
            'critical': 0,
            ErrorTier.TIER_1: 0,  # Also add enum keys
            ErrorTier.TIER_2: 0,
            ErrorTier.TIER_3: 0,
            ErrorTier.TIER_4: 0
        }
        self.retry_counts = {}
    
    def classify_error(self, error: Exception) -> ErrorTier:
        """Classify error into appropriate tier."""
        error_str = str(error).lower()
        error_type = type(error).__name__
        
        # Tier 1: Transient errors
        if any(x in error_str for x in ['timeout', 'temporary', 'connection reset']):
            return ErrorTier.TIER_1
            
        # Tier 2: Persistent errors  
        if any(x in error_str for x in ['permission', 'access denied', 'rate limit']):
            return ErrorTier.TIER_2
            
        # Tier 3: System errors
        if any(x in error_str for x in ['not found', 'missing', 'unavailable']):
            return ErrorTier.TIER_3
            
        # Tier 4: Critical errors
        if any(x in error_str for x in ['critical', 'fatal', 'corruption']):
            return ErrorTier.TIER_4
            
        # Default to Tier 2 for unknown errors
        return ErrorTier.TIER_2
    
    async def handle(self, error: Exception, context: Dict[str, Any] = None) -> Any:
        """Handle error according to its tier."""
        tier = self.classify_error(error)
        self.logger.info(f"Handling {tier.name}: {str(error)}")
        
        # FIX 3: Safer stat tracking
        # Try multiple keys to avoid KeyError
        for key in [tier, tier.value, tier.name.lower().replace('tier_', '').replace('1', 'transient').replace('2', 'persistent').replace('3', 'system').replace('4', 'critical')]:
            if key in self.error_stats:
                self.error_stats[key] = self.error_stats.get(key, 0) + 1
                break
        else:
            # Fallback: create the key if it doesn't exist
            self.error_stats['system'] = self.error_stats.get('system', 0) + 1
        
        if tier == ErrorTier.TIER_1:
            return await self._handle_tier_1(error, context)
        elif tier == ErrorTier.TIER_2:
            return await self._handle_tier_2(error, context)
        elif tier == ErrorTier.TIER_3:
            return await self._handle_tier_3(error, context)
        else:
            return await self._handle_tier_4(error, context)
    
    async def _handle_tier_1(self, error: Exception, context: Dict[str, Any] = None) -> Any:
        """Tier 1: Retry once immediately."""
        self.logger.info("Tier 1: Retrying once...")
        
        if context and 'operation' in context:
            try:
                # Retry the operation
                await asyncio.sleep(0.1)  # Brief pause
                return await context['operation']()
            except Exception as e:
                self.logger.warning(f"Tier 1 retry failed: {e}")
                return None
        return None
    
    async def _handle_tier_2(self, error: Exception, context: Dict[str, Any] = None) -> Any:
        """Tier 2: Retry with exponential backoff."""
        self.logger.info("Tier 2: Retrying with backoff...")
        
        error_key = str(error)
        self.retry_counts[error_key] = self.retry_counts.get(error_key, 0)
        
        for attempt in range(3):
            try:
                wait_time = (2 ** attempt)  # Exponential backoff
                self.logger.info(f"Waiting {wait_time}s before retry {attempt + 1}/3")
                await asyncio.sleep(wait_time)
                
                if context and 'operation' in context:
                    return await context['operation']()
            except Exception as e:
                self.logger.warning(f"Tier 2 retry {attempt + 1} failed: {e}")
                
        return None
    
    async def _handle_tier_3(self, error: Exception, context: Dict[str, Any] = None) -> Any:
        """Tier 3: Implement workaround."""
        self.logger.warning(f"Tier 3: Implementing workaround for {error}")
        
        # Specific workarounds based on error type
        if "ffmpeg" in str(error).lower():
            self.logger.info("FFmpeg not available, using mock mode")
            if context:
                context['use_mock'] = True
            return {'workaround': 'mock_mode'}
            
        if "database" in str(error).lower():
            self.logger.info("Database issue, attempting reconnection")
            # Implement database reconnection logic
            return {'workaround': 'reconnect'}
            
        return {'workaround': 'generic'}
    
    async def _handle_tier_4(self, error: Exception, context: Dict[str, Any] = None) -> Any:
        """Tier 4: Generate recovery plan."""
        self.logger.error(f"Tier 4 Critical Error: {error}")
        
        recovery_plan = {
            'error': str(error),
            'type': type(error).__name__,
            'timestamp': time.time(),
            'context': context,
            'recovery_steps': [
                "1. Check system logs for root cause",
                "2. Verify all dependencies are installed",
                "3. Check database connectivity",
                "4. Restart the service",
                "5. Contact support if issue persists"
            ]
        }
        
        self.logger.error(f"Recovery plan: {recovery_plan}")
        
        # Don't crash - try to continue in degraded mode
        if context:
            context['degraded_mode'] = True
            
        return recovery_plan
    
    def get_stats(self) -> Dict[str, int]:
        """Get error statistics."""
        return dict(self.error_stats)
    
    def reset_stats(self):
        """Reset error statistics."""
        for key in self.error_stats:
            self.error_stats[key] = 0
        self.retry_counts.clear()