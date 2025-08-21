#!/bin/bash
# TikTok AI Automation Monitoring Script
# Real-time system monitoring

set -e

echo "📊 TikTok AI Automation Monitoring"
echo "=================================="
echo ""

# Function to check service status
check_service() {
    local service=$1
    local url=$2
    
    if curl -s -f "$url" > /dev/null 2>&1; then
        echo "✅ $service: Running"
    else
        echo "❌ $service: Down"
    fi
}

# Function to get metrics
get_metrics() {
    echo ""
    echo "📈 System Metrics:"
    echo "-----------------"
    
    # Get API metrics
    metrics=$(curl -s http://localhost:8000/api/v1/metrics 2>/dev/null || echo "{}")
    
    if [ "$metrics" != "{}" ]; then
        echo "$metrics" | python -m json.tool
    else
        echo "Unable to fetch metrics"
    fi
}

# Function to check Constitutional compliance
check_compliance() {
    echo ""
    echo "🏛️ Constitutional AI Compliance:"
    echo "--------------------------------"
    
    compliance=$(curl -s http://localhost:8000/api/v1/metrics 2>/dev/null | python -c "
import json, sys
data = json.load(sys.stdin)
print(f'API Response: {data.get(\"api_response_avg\", \"N/A\")}ms (Target: <22ms)')
print(f'Token Reduction: {data.get(\"token_reduction\", 0)*100:.1f}% (Target: 85%)')
print(f'Error Recovery: {data.get(\"error_recovery_rate\", 0)*100:.1f}% (Target: 95%)')
" 2>/dev/null || echo "Unable to check compliance")
    
    echo "$compliance"
}

# Function to show logs
show_logs() {
    echo ""
    echo "📜 Recent Logs (last 20 lines):"
    echo "------------------------------"
    docker-compose logs --tail=20 tiktok-ai 2>/dev/null || echo "Unable to fetch logs"
}

# Main monitoring loop
while true; do
    clear
    echo "📊 TikTok AI Automation Monitoring"
    echo "=================================="
    echo "Time: $(date)"
    echo ""
    
    echo "🔌 Service Status:"
    echo "-----------------"
    check_service "API" "http://localhost:8000/api/v1/health"
    check_service "Prometheus" "http://localhost:9090/-/healthy"
    check_service "Redis" "redis://localhost:6379" 
    
    get_metrics
    check_compliance
    
    echo ""
    echo "🔄 Refreshing in 30 seconds... (Press Ctrl+C to exit)"
    
    # Option to show logs
    read -t 30 -n 1 -p "Press 'L' to show logs, any other key to skip: " key || true
    if [ "$key" = "L" ] || [ "$key" = "l" ]; then
        show_logs
        read -p "Press Enter to continue..."
    fi
done