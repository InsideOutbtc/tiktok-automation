#!/bin/bash

if [ -z "$1" ]; then
  echo "Usage: ./init-new-project.sh <project-name>"
  exit 1
fi

PROJECT_NAME=$1
PROJECT_PATH=~/$PROJECT_NAME

echo "🚀 Initializing new project: $PROJECT_NAME"

# Create project and copy systems
mkdir -p $PROJECT_PATH
cp -r ~/Patrick/project-systems $PROJECT_PATH/systems

echo "✅ Project initialized at: $PROJECT_PATH"
echo "📋 Next: Load AI_AGENT_PROTOCOL.md into Claude"