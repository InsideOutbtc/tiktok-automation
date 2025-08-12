# ERROR HANDLING TIER SYSTEM

## TIER 1: Transient Issues
- Retry once immediately
- Continue if retry fails
- Document in session log
- No workflow interruption

### Examples
- Network timeout
- Temporary file lock
- API rate limit (first occurrence)
- Memory allocation failure

### Implementation
```javascript
try {
  return await operation();
} catch (error) {
  console.log(`Tier 1 error: ${error.message}, retrying...`);
  try {
    return await operation();
  } catch (retryError) {
    console.log(`Retry failed, continuing with workflow...`);
    return fallbackValue;
  }
}
```

## TIER 2: Persistent Issues  
- 3 retries with exponential backoff
- Alternative approach implementation
- Workaround documentation
- Modified workflow continuation

### Examples
- Repeated API failures
- Permission errors
- Resource exhaustion
- Dependency conflicts

### Implementation
```javascript
async function tier2Handler(operation, alternatives) {
  for (let i = 0; i < 3; i++) {
    try {
      return await operation();
    } catch (error) {
      await sleep(Math.pow(2, i) * 1000);
    }
  }
  
  // Implement alternative approach
  for (const alternative of alternatives) {
    try {
      return await alternative();
    } catch (error) {
      continue;
    }
  }
  
  // Document workaround and continue
  documentWorkaround();
  return modifiedWorkflow();
}
```

## TIER 3: System Issues
- Identify affected functionality
- Implement workaround
- Document for resolution
- Continue with available capabilities

### Examples
- Service unavailable
- Critical dependency missing
- System resource limits
- Infrastructure failures

### Implementation Pattern
1. **Assess Impact**
   - Identify affected features
   - Determine available alternatives
   - Calculate workaround feasibility

2. **Implement Workaround**
   - Use alternative services
   - Degrade gracefully
   - Maintain core functionality

3. **Document Status**
   - Current limitations
   - Workaround details
   - Recovery procedures

## TIER 4: Complete Failure
- Document complete status
- Generate recovery plan
- Prepare handoff documentation
- Suggest alternative approaches

### Examples
- Total system failure
- Unrecoverable data corruption
- Complete service outage
- Critical security breach

### Recovery Documentation Template
```markdown
## System Failure Report
**Timestamp**: [ISO 8601]
**Failure Type**: [Category]
**Affected Systems**: [List]

### Current State
[Detailed status description]

### Attempted Resolutions
1. [Action taken] - [Result]
2. [Action taken] - [Result]

### Recovery Plan
1. [Step with estimated time]
2. [Step with estimated time]

### Alternative Approaches
- [Alternative 1 with pros/cons]
- [Alternative 2 with pros/cons]

### Handoff Requirements
- [Required access/permissions]
- [Technical prerequisites]
- [Knowledge requirements]
```

## Error Classification Matrix

| Error Type | Tier | Retry Strategy | Workflow Impact | Documentation |
|------------|------|----------------|-----------------|---------------|
| Transient | 1 | Once immediate | None | Session log |
| Persistent | 2 | 3x with backoff | Modified | Workaround doc |
| System | 3 | None | Degraded | Full impact doc |
| Critical | 4 | None | Halted | Recovery plan |

## Automatic Tier Selection

```javascript
function selectErrorTier(error) {
  // Tier 1: Transient
  if (error.code === 'ETIMEDOUT' || 
      error.code === 'ECONNRESET' ||
      error.message.includes('temporary')) {
    return 1;
  }
  
  // Tier 2: Persistent
  if (error.code === 'EACCES' ||
      error.code === 'ENOSPC' ||
      error.retryCount > 0) {
    return 2;
  }
  
  // Tier 3: System
  if (error.code === 'ENOTFOUND' ||
      error.message.includes('service unavailable') ||
      error.critical === false) {
    return 3;
  }
  
  // Tier 4: Critical
  return 4;
}
```

## Integration with Maximum Velocity Mode

- **No Stopping**: Errors handled automatically without user intervention
- **Smart Recovery**: System selects appropriate tier and executes recovery
- **Continuous Flow**: Workflow continues with modifications as needed
- **Context Preservation**: Error handling maintains session context

## Best Practices

1. **Classify Early**: Determine tier immediately upon error
2. **Execute Quickly**: Implement recovery without delay
3. **Document Smartly**: Only document what's necessary for continuity
4. **Preserve Momentum**: Keep workflow moving forward
5. **Learn Patterns**: Store successful recovery patterns for reuse

---

**ERROR HANDLING SYSTEM**: ACTIVE AND AUTONOMOUS