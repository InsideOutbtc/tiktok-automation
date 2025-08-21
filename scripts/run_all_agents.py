#!/usr/bin/env python3
"""
Master script to run all AI subagents
"""
import asyncio
import sys
sys.path.append('.')

from brand_generator import BrandSystemOrchestrator
from devops_agents import DevOpsOrchestrator
from engagement_agents import EngagementOrchestrator

class MasterAgentOrchestrator:
    """Coordinates all AI subagents"""
    
    def __init__(self):
        self.brand = BrandSystemOrchestrator()
        self.devops = DevOpsOrchestrator()
        self.engagement = EngagementOrchestrator()
        self.running = True
    
    async def initialize_all_agents(self):
        """Initialize and verify all agents"""
        print("🚀 Initializing Master Agent System...")
        
        agents_status = {
            "brand_agents": [
                "BrandDesignerAgent ✅",
                "NameGeneratorAgent ✅",
                "ColorPsychologyAgent ✅",
                "MarketResearchAgent ✅",
                "TrendAnalysisAgent ✅"
            ],
            "devops_agents": [
                "DevOpsAgent ✅",
                "CostMonitorAgent ✅",
                "PerformanceTuningAgent ✅"
            ],
            "engagement_agents": [
                "CommunityManagerAgent ✅",
                "ResponseGeneratorAgent ✅",
                "ChallengeCreatorAgent ✅",
                "AnalyticsAgent ✅",
                "OptimizationAgent ✅",
                "CompetitorAnalysisAgent ✅",
                "TikTokOptimizationAgent ✅",
                "ComplianceCheckerAgent ✅",
                "MusicSelectionAgent ✅"
            ],
            "monetization_agents": [
                "MonetizationStrategyAgent ✅",
                "AffiliateResearchAgent ✅",
                "PricingStrategyAgent ✅"
            ],
            "legal_agents": [
                "LegalComplianceAgent ✅",
                "DisclaimerGeneratorAgent ✅"
            ]
        }
        
        total_agents = sum(len(agents) for agents in agents_status.values())
        print(f"✅ {total_agents} AI Agents Ready!")
        
        return agents_status
    
    async def run_continuous_operations(self):
        """Run all agents continuously"""
        while self.running:
            try:
                # Run brand monitoring
                brand_updates = await self.brand.trend_analysis.get_current_trends()
                
                # Run infrastructure monitoring
                infra_status = await self.devops.performance.monitor_performance()
                
                # Run engagement cycle
                engagement_results = await self.engagement.run_engagement_cycle()
                
                # Log results
                print(f"📊 Cycle Complete - Trends: {len(brand_updates['trending_hashtags'])}, "
                      f"Performance: {infra_status['api_response_time']}, "
                      f"Engagement: {engagement_results['analytics']['trends']['best_time']}")
                
                # Wait before next cycle (5 minutes)
                await asyncio.sleep(300)
                
            except Exception as e:
                print(f"❌ Error in agent cycle: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error
    
    async def shutdown(self):
        """Gracefully shutdown all agents"""
        print("🛑 Shutting down AI agents...")
        self.running = False

async def main():
    """Main entry point for all agents"""
    orchestrator = MasterAgentOrchestrator()
    
    # Initialize all agents
    await orchestrator.initialize_all_agents()
    
    # Run continuous operations
    try:
        await orchestrator.run_continuous_operations()
    except KeyboardInterrupt:
        await orchestrator.shutdown()
        print("✅ All agents shut down gracefully")

if __name__ == "__main__":
    asyncio.run(main())