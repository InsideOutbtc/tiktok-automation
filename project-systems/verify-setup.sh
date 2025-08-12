#!/bin/bash

echo "🔍 Verifying Project Systems Setup..."

# Check directories
for dir in constitutional-ai mcp-integration prp-framework workflows patterns; do
  [ -d "$dir" ] && echo "✅ $dir exists" || echo "❌ $dir missing"
done

# Check key files
files=(
  "constitutional-ai/AI_AGENT_PROTOCOL.md"
  "mcp-integration/MCP_INTEGRATION_GUIDE.md"
  "workflows/ENHANCED_WORKFLOW_PROTOCOLS.md"
  "README.md"
)

for file in "${files[@]}"; do
  [ -f "$file" ] && echo "✅ $file exists" || echo "❌ $file missing"
done

echo "✨ Setup verification complete!"