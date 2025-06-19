#!/bin/bash

# Create and activate Python virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r backend/requirements.txt

# Install development dependencies
echo "Installing development dependencies..."
pip install pytest pytest-cov black flake8 mypy

# Download spaCy model
echo "Downloading spaCy model..."
python -m spacy download en_core_web_sm

# Install Node.js dependencies
echo "Installing Node.js dependencies..."
npm install

# Create necessary directories
mkdir -p backend/uploads
mkdir -p backend/data
mkdir -p backend/logs

# Set up environment variables
echo "Creating .env file..."
cat > .env << EOL
FLASK_ENV=development
FLASK_APP=backend/app.py
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/lait_db
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=development_secret_key
JWT_SECRET_KEY=jwt_development_secret
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
S3_BUCKET=your_bucket_name
EOL

# Start development services
echo "Starting development services..."
docker-compose up -d redis postgres

# Initialize database
echo "Initializing database..."
cd backend
flask db upgrade
python init_db.py
cd ..

echo "Development environment setup complete!"
echo "Run 'docker-compose up' to start all services"
echo "Run 'npm run dev' to start the frontend development server"
