# Backend (canonical)

This directory contains the canonical backend for the LAIT project. The repository historically contained multiple variations of the backend app; to reduce confusion the project uses `backend/app_real.py` as the canonical entrypoint for development and production.

Quick facts
- Canonical entrypoint: `backend/app_real.py`
- DB: controlled via `DATABASE_URL` environment variable (Postgres recommended; falls back to SQLite locally)
- Configuration: `backend/config.py` (used by some tooling), but `app_real.py` reads env vars directly. Prefer `DATABASE_URL`, `JWT_SECRET_KEY`, and `API_PORT`.

Run locally (dev)

1. Create a virtualenv and install requirements:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

2. Export simple env vars and run the server:

```bash
export DATABASE_URL="sqlite:///lait.db"  # or your Postgres URL
export JWT_SECRET_KEY="change-me-in-prod"
cd backend
python app_real.py
```

The server runs on port 5003 by default when invoked directly.

Archival / cleanup

To archive legacy/duplicate backend app files, run the top-level `cleanup.sh` script. It will move legacy app files into `backend/archive/` (safe — nothing is deleted permanently):

```bash
./cleanup.sh
```

Notes and next steps
- `app_real.py` is intentionally self-contained (models and endpoints). For a long-term refactor we recommend migrating functionality into the modular blueprint architecture under `backend/routes/` and using `backend/app.py` (factory) as the canonical app, but that is a larger change.
- When deploying with Docker or CI, ensure `FLASK_APP` or entrypoint references `backend/app_real.py` (many existing scripts already do).

If you want me to proceed with the full refactor into the blueprint/factory design, tell me and I will (1) migrate endpoints from `app_real.py` into blueprints, (2) update Docker/CI, and (3) run the tests/quality gates.
