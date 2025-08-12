# SUCCESSFUL PATTERNS

## Agent Development
- Use start-simple-agents.ts framework
- Port assignment: 8000 + agentId
- Always include health endpoints
- Constitutional AI compliance

## Performance Optimization
- Cache with Redis for <22ms
- Parallel processing where possible
- Batch operations
- Connection pooling

## Error Handling
- TIER 1-4 classification
- Exponential backoff for retries
- Graceful degradation
- Comprehensive logging