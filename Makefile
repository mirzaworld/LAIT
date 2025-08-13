# LAIT Project Makefile
# ====================

# Default Python interpreter
PYTHON := python3

# Backend virtual environment
BACKEND_VENV := backend/venv_real/bin/python

# Check if backend venv exists, otherwise use system python
PYTHON_CMD := $(shell [ -f $(BACKEND_VENV) ] && echo $(BACKEND_VENV) || echo $(PYTHON))

.PHONY: help seed health metrics clean

# Default target
help:
	@echo "🌱 LAIT Project Commands"
	@echo "========================"
	@echo ""
	@echo "Available targets:"
	@echo "  make seed     - Seed demo data (creates demo user + sample invoices)"
	@echo "  make health   - Check backend health"
	@echo "  make metrics  - Show dashboard metrics (requires demo user)"
	@echo "  make clean    - Clean up demo data"
	@echo ""
	@echo "Requirements:"
	@echo "  - Backend running on localhost:5003"
	@echo "  - Start with: cd backend && python app_real.py"

# Seed demo data
seed:
	@echo "🌱 Seeding LAIT demo data..."
	@echo "Requirement: Backend must be running on localhost:5003"
	@echo ""
	python3 scripts/seed_demo.py

# Check backend health
health:
	@echo "🏥 Checking backend health..."
	@curl -s http://localhost:5003/api/health | jq '.' || echo "❌ Backend not accessible"

# Show dashboard metrics (requires demo user to be seeded first)
metrics:
	@echo "📊 Fetching dashboard metrics..."
	@echo "Note: Run 'make seed' first to create demo user"
	@curl -s -X POST -H "Content-Type: application/json" \
		-d '{"email":"demo@lait.com","password":"demo123!"}' \
		http://localhost:5003/api/auth/login | \
		jq -r '.token' | \
		xargs -I {} curl -s -H "Authorization: Bearer {}" \
		http://localhost:5003/api/dashboard/metrics | \
		jq '.'

# Clean up demo data (removes demo user and their invoices)
clean:
	@echo "🧹 Cleaning up demo data..."
	@echo "Note: This would require admin endpoints to fully clean."
	@echo "For now, restart the backend or delete the SQLite database."
	@echo "Backend database: backend/lait.db"

# Development shortcuts
start-backend:
	@echo "🚀 Starting LAIT backend..."
	cd backend && $(PYTHON_CMD) app_real.py

install-deps:
	@echo "📦 Installing backend dependencies..."
	cd backend && pip install -r requirements.txt
