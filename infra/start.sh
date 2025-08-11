#!/bin/bash

# LAIT Infrastructure Startup Script
set -e

echo "🚀 Starting LAIT Infrastructure..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose not found. Please install docker-compose."
    exit 1
fi

# Navigate to infra directory
cd "$(dirname "$0")"

# Check if .env file exists
if [ ! -f "../backend/.env" ]; then
    echo "📝 Creating .env file from example..."
    cp .env.example ../backend/.env
    echo "⚠️  Please edit ../backend/.env with your configuration"
fi

# Start infrastructure services first
echo "🏗️  Starting infrastructure services..."
docker-compose up -d postgres redis minio

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check service health
echo "🔍 Checking service health..."
docker-compose ps

# Start application services
echo "🚀 Starting application services..."
docker-compose up -d api worker web

# Run database migration
echo "🗃️  Running database migration..."
docker-compose run --rm migrate

# Show service status
echo "✅ LAIT Infrastructure started successfully!"
echo ""
echo "🌐 Services available at:"
echo "  - Frontend:      http://localhost:3000"
echo "  - API:           http://localhost:5003"
echo "  - MinIO Console: http://localhost:9001"
echo ""
echo "📊 To view logs: docker-compose logs -f [service]"
echo "🛑 To stop:      docker-compose down"
echo ""

# Show final status
docker-compose ps
