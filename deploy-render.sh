#!/bin/bash

# LAIT Deployment Script for Render.com
echo "🚀 Deploying LAIT to Render.com..."

# Create render.yaml for Render deployment
cat > render.yaml << 'EOF'
services:
  - type: web
    name: lait-legal-intelligence
    env: python
    buildCommand: |
      pip install -r backend/requirements.txt
      npm install
      npm run build
    startCommand: |
      export PYTHONPATH=/opt/render/project/src
      python backend/app_real.py
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: FLASK_APP
        value: backend/app_real.py
      - key: FLASK_ENV
        value: production
      - key: SECRET_KEY
        generateValue: true
      - key: JWT_SECRET_KEY
        generateValue: true
      - key: DATABASE_URL
        fromDatabase:
          name: lait-database
          property: connectionString
      - key: REDIS_URL
        fromService:
          type: redis
          name: lait-redis
          property: connectionString

databases:
  - name: lait-database
    databaseName: legalspend
    user: lait_user

services:
  - type: redis
    name: lait-redis
    plan: free
EOF

echo "✅ Created render.yaml configuration"
echo "📋 Next steps:"
echo "1. Push this code to GitHub"
echo "2. Connect your GitHub repo to Render.com"
echo "3. Render will automatically deploy using this configuration"
echo "4. Your app will be available at: https://lait-legal-intelligence.onrender.com" 