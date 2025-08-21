#!/bin/bash
# Deploy with Docker import fixes

echo "🚀 PowerPro Docker Deployment with Import Fixes"
echo "=============================================="

# Step 1: Run the Python fix script
echo "1. Running import fix script..."
python3 fix_docker_imports.py

# Step 2: Ensure all __init__.py files exist
echo -e "\n2. Ensuring __init__.py files..."
touch src/__init__.py
touch src/database/__init__.py
touch src/core/__init__.py
touch src/agents/__init__.py
touch src/agents/content_agents/__init__.py
touch src/utils/__init__.py
touch src/api/__init__.py
touch src/mcp/__init__.py

# Make sure they're not empty (can cause issues)
echo "# Auto-generated" > src/__init__.py
echo "# Auto-generated" > src/database/__init__.py

# Step 3: Test imports locally first
echo -e "\n3. Testing imports locally..."
python3 docker_debug_imports.py

# Step 4: Build Docker image with fixes
echo -e "\n4. Building Docker image..."
docker build -f Dockerfile.fixed -t powerpro-fixed:latest .

# Step 5: Test in Docker container
echo -e "\n5. Testing imports in Docker container..."
docker run --rm powerpro-fixed:latest python docker_debug_imports.py

# Step 6: Run container with environment variables
echo -e "\n6. Starting container for testing..."
docker run -d \
  --name powerpro-test \
  -e YOUTUBE_API_KEY="${YOUTUBE_API_KEY}" \
  -e OPENAI_API_KEY="${OPENAI_API_KEY}" \
  -e ENVIRONMENT="development" \
  -e AUTO_PUBLISH="false" \
  -v $(pwd)/database:/app/database \
  powerpro-fixed:latest \
  python start_docker_safe.py

# Wait a moment
sleep 5

# Check logs
echo -e "\n7. Checking container logs..."
docker logs powerpro-test

# Check if container is still running
if docker ps | grep -q powerpro-test; then
    echo -e "\n✅ Container is running!"
    echo "   To view logs: docker logs -f powerpro-test"
    echo "   To stop: docker stop powerpro-test && docker rm powerpro-test"
else
    echo -e "\n❌ Container stopped! Checking why..."
    docker logs powerpro-test
    docker rm powerpro-test
fi

echo -e "\n=============================================="
echo "Deployment test complete!"
echo ""
echo "If successful, deploy to DigitalOcean with:"
echo "  1. Push image to registry: docker tag powerpro-fixed:latest registry.digitalocean.com/YOUR_REGISTRY/powerpro:latest"
echo "  2. Push: docker push registry.digitalocean.com/YOUR_REGISTRY/powerpro:latest"
echo "  3. Update DigitalOcean App Platform to use new image"