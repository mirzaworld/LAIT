#!/bin/bash
# LAIT Docker Development Stack - Test Script

echo "🐳 LAIT Docker Development Stack"
echo "================================="
echo ""

echo "📋 ACCEPTANCE TEST COMMANDS:"
echo ""
echo "1. Start the Docker stack:"
echo "   cd infra && docker compose up -d --build"
echo ""
echo "2. Test API health endpoint:"
echo "   curl http://localhost:5003/api/health"
echo ""

echo "🔍 STACK OVERVIEW:"
echo "- db:    PostgreSQL 15 on port 5432"
echo "- redis: Redis 7 on port 6379" 
echo "- api:   Backend Flask API on port 5003"
echo "- web:   Frontend Vite dev server on port 5173"
echo ""

echo "🌍 ACCESS URLS:"
echo "- Frontend: http://localhost:5173"
echo "- Backend:  http://localhost:5003"
echo "- API Docs: http://localhost:5003/api/health"
echo ""

echo "📂 SERVICES CONFIGURATION:"
echo "✅ PostgreSQL: legalspend database with postgres/postgres credentials"
echo "✅ Redis: Available for caching and sessions" 
echo "✅ Backend: Builds from backend/Dockerfile, runs app_real.py"
echo "✅ Frontend: Builds from frontend/Dockerfile, runs dev server with HMR"
echo ""

echo "🔧 ENVIRONMENT VARIABLES:"
echo "✅ DATABASE_URL: postgresql+psycopg2://postgres:postgres@db:5432/legalspend"
echo "✅ REDIS_URL: redis://redis:6379/0"
echo "✅ VITE_API_BASE: http://localhost:5003"
echo ""

echo "🚀 Ready for development!"
echo "To start: cd infra && docker compose up -d --build"
