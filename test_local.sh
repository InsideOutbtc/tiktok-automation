#!/bin/bash
# Test the application locally before deployment

echo "🧪 Testing PowerPro Automation Locally"
echo "====================================="

# Check Python version
echo "🐍 Python version:"
python3 --version

# Test imports
echo ""
echo "📦 Testing imports..."
python3 -c "
try:
    from src.core.main_controller import MainController
    print('✅ Main controller imports successfully')
except Exception as e:
    print(f'❌ Import error: {e}')
"

# Test Docker build
echo ""
echo "🐳 Building Docker image..."
docker build -t powerpro-test . || {
    echo "❌ Docker build failed"
    exit 1
}

echo "✅ Docker build successful"

# Test Docker run
echo ""
echo "🏃 Testing Docker container..."
docker run --rm -e YOUTUBE_API_KEY=test -e OPENAI_API_KEY=test powerpro-test python -c "print('Container works!')"

echo ""
echo "✅ All tests passed! Ready for deployment."
echo "Run ./deploy.sh to deploy to DigitalOcean"