#!/bin/bash

echo "🐳 LAIT Docker Development Stack"
echo "================================"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker Desktop first:"
    echo "   macOS: https://docs.docker.com/docker-for-mac/install/"
    echo "   Linux: https://docs.docker.com/engine/install/"
    echo ""
    exit 1
fi

# Check if Docker Compose is available
if ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not available. Please update Docker Desktop."
    exit 1
fi

echo "✅ Docker is available"
echo "✅ Docker Compose is available"
echo ""

# Show the services that will be started
echo "� Starting LAIT development stack with:"
echo "   📊 PostgreSQL Database (port 5432)"
echo "   🔄 Redis Cache (port 6379)"  
echo "   🔧 API Backend (port 5003)"
echo "   🌐 Web Frontend (port 5173)"
echo ""

# Start the services
echo "⚡ Building and starting services..."
docker compose up -d --build

# Wait a moment for services to start
sleep 10

echo ""
echo "🎉 LAIT stack is starting up!"
echo ""
echo "� Service Status:"
docker compose ps

echo ""
echo "🧪 Testing API Health Check:"
curl -s http://localhost:5003/api/health | python3 -m json.tool || echo "API not ready yet, please wait..."

echo ""
echo "🔗 Access URLs:"
echo "   Frontend: http://localhost:5173"
echo "   API:      http://localhost:5003"
echo "   Database: postgres://postgres:postgres@localhost:5432/lait"
echo "   Redis:    redis://localhost:6379"
echo ""
echo "� Useful commands:"
echo "   View logs:    docker compose logs -f"
echo "   Stop stack:   docker compose down"
echo "   Restart:      docker compose restart"
echo ""
