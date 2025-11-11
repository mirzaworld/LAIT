#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

echo "== LAIT dev bootstrap: creating virtualenv and installing minimal dev deps =="

if [ -d ".venv" ]; then
  echo "Using existing .venv virtualenv"
else
  python3 -m venv .venv
  echo "Created virtualenv at .venv"
fi

# Activate venv for this script
# shellcheck disable=SC1091
source .venv/bin/activate

echo "Installing backend dev requirements (this may take a few minutes)" 
pip install --upgrade pip
pip install -r backend/dev-requirements.txt

echo "Setting DATABASE_URL to SQLite for lightweight local dev"
export DATABASE_URL="sqlite:///lait_local.db"

echo "Initializing DB (if missing)"
python - <<'PY'
import sys, os
sys.path.insert(0, os.path.join(os.getcwd(), 'backend'))
try:
  from db.database import init_db
  init_db()
  print('Database initialized (SQLite)')
except Exception as e:
  print('DB init warning:', e)
PY

echo "Seeding dev database with minimal records"
python scripts/seed_dev_db.py || echo "Seed script failed (continuing): $?"

echo "Training tiny ML models for dev"
python scripts/train_minimal_models.py || echo "Model training failed (continuing): $?"

echo "Starting backend (enhanced_app.py) on ${API_HOST:-127.0.0.1}:${API_PORT:-5003}"
python backend/enhanced_app.py
