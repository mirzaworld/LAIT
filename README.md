# LAIT - Enhanced Legal Intelligence System

This repository contains the LAIT (Legal AI Tracker) project. The canonical project documentation is maintained in `COMPREHENSIVE_PROJECT_DOCUMENTATION.md`.

Quick start (minimal local development):

1. Copy `.env.example` to `.env` and adjust if needed.
2. Create a Python virtualenv and install minimal dev dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/dev-requirements.txt
```

3. Start the backend in lightweight SQLite mode (dev):

```bash
export DATABASE_URL="sqlite:///lait_local.db"
python backend/enhanced_app.py
```

4. Start the frontend (from repo root):

```bash

npm install
npm run dev

# OR (use the frontend package.json)
cd frontend
npm install
npm run dev
```

For full architecture, deployment, and feature documentation see `COMPREHENSIVE_PROJECT_DOCUMENTATION.md`.

If you'd like, I can (1) run a dev bootstrap now and start the backend to capture runtime errors, and (2) consolidate/readme and minor dev scripts to make local startup smoother. Choose which you'd like me to run next.
#### Option 2: Manual Start
