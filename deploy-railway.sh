#!/bin/bash

# LAIT Deployment Script for Railway.app
echo "🚀 Deploying LAIT to Railway.app..."

# Create railway.json for Railway deployment
cat > railway.json << 'EOF'
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "export PYTHONPATH=/app && python backend/enhanced_app.py",
    "healthcheckPath": "/api/health",
    "healthcheckTimeout": 300,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
EOF

# Create nixpacks.toml for better build configuration
cat > nixpacks.toml << 'EOF'
[phases.setup]
nixPkgs = ["python311", "nodejs_18", "postgresql_15"]

[phases.install]
cmds = [
  "pip install -r backend/requirements.txt",
  "npm install",
  "npm run build"
]

[phases.build]
cmds = ["echo 'Build completed'"]

[start]
cmd = "export PYTHONPATH=/app && python backend/enhanced_app.py"
EOF

echo "✅ Created Railway deployment configuration"
echo "📋 Next steps:"
echo "1. Install Railway CLI: npm install -g @railway/cli"
echo "2. Login to Railway: railway login"
echo "3. Initialize project: railway init"
echo "4. Deploy: railway up"
echo "5. Your app will be available at the provided Railway URL" 