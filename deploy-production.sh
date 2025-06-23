#!/bin/bash

# LAIT Production Deployment Script
# Deploys the LAIT application to production with live data integration

set -e

echo "🚀 LAIT Production Deployment Starting..."
echo "📅 $(date)"

# Configuration
APP_NAME="lait-legal-ai"
DOMAIN="lait-demo.com"
PORT=5003
FRONTEND_PORT=3000

# Check if required tools are installed
check_requirements() {
    echo "🔍 Checking deployment requirements..."
    
    commands=("python3" "npm" "git" "curl")
    for cmd in "${commands[@]}"; do
        if ! command -v $cmd &> /dev/null; then
            echo "❌ $cmd is not installed. Please install it first."
            exit 1
        fi
    done
    
    echo "✅ All requirements satisfied"
}

# Install Python dependencies
install_python_deps() {
    echo "🐍 Installing Python dependencies..."
    
    if [ ! -f "requirements.txt" ]; then
        echo "📝 Creating requirements.txt..."
        cat > requirements.txt << EOF
Flask==3.0.0
Flask-CORS==4.0.0
Flask-SocketIO==5.3.6
SQLAlchemy==2.0.23
pandas==2.1.4
numpy==1.25.2
scikit-learn==1.3.2
python-socketio==5.10.0
gunicorn==21.2.0
python-dotenv==1.0.0
aiohttp==3.9.1
lxml==4.9.3
requests==2.31.0
pytest==7.4.3
python-multipart==0.0.6
Werkzeug==3.0.1
eventlet==0.33.3
greenlet==3.0.2
EOF
    fi
    
    pip3 install -r requirements.txt
    echo "✅ Python dependencies installed"
}

# Install Node.js dependencies
install_node_deps() {
    echo "📦 Installing Node.js dependencies..."
    npm install
    echo "✅ Node.js dependencies installed"
}

# Build frontend
build_frontend() {
    echo "🔨 Building frontend for production..."
    
    # Set production environment variables
    export VITE_API_URL="https://$DOMAIN/api"
    export NODE_ENV="production"
    
    npm run build
    echo "✅ Frontend built successfully"
}

# Create production environment file
create_env() {
    echo "⚙️ Creating production environment configuration..."
    
    cat > .env.production << EOF
# LAIT Production Configuration
FLASK_ENV=production
DEBUG=False
API_HOST=0.0.0.0
API_PORT=$PORT
DATABASE_URL=sqlite:///./lait_production.db
CORS_ORIGINS=https://$DOMAIN
SECRET_KEY=$(openssl rand -base64 32)

# Live Data Configuration
LIVE_DATA_ENABLED=true
LIVE_DATA_SOURCES=22
LIVE_DATA_UPDATE_INTERVAL=300

# ML Configuration
ML_MODELS_ENABLED=true
ML_TRAINING_ENABLED=true

# Security
SECURE_COOKIES=true
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true
SESSION_COOKIE_SAMESITE=Lax

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/lait/app.log
EOF
    
    echo "✅ Production environment configured"
}

# Create systemd service file
create_systemd_service() {
    echo "🔧 Creating systemd service..."
    
    sudo tee /etc/systemd/system/lait-backend.service > /dev/null << EOF
[Unit]
Description=LAIT Legal AI Backend Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=$(pwd)/backend
Environment=PATH=$(pwd)/venv/bin
ExecStart=$(pwd)/venv/bin/python single_root_app.py
EnvironmentFile=$(pwd)/.env.production
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    
    sudo systemctl daemon-reload
    sudo systemctl enable lait-backend
    echo "✅ Systemd service created"
}

# Configure Nginx
configure_nginx() {
    echo "🌐 Configuring Nginx..."
    
    sudo tee /etc/nginx/sites-available/lait << EOF > /dev/null
server {
    listen 80;
    server_name $DOMAIN;
    
    # Redirect HTTP to HTTPS
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name $DOMAIN;
    
    # SSL Configuration (Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload";
    
    # Frontend static files
    location / {
        root $(pwd)/dist;
        try_files \$uri \$uri/ /index.html;
        
        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
    
    # API backend
    location /api {
        proxy_pass http://127.0.0.1:$PORT;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Socket.IO
    location /socket.io {
        proxy_pass http://127.0.0.1:$PORT;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        application/javascript
        application/json
        application/xml
        text/css
        text/javascript
        text/xml
        text/plain;
}
EOF
    
    # Enable the site
    sudo ln -sf /etc/nginx/sites-available/lait /etc/nginx/sites-enabled/
    sudo nginx -t && sudo systemctl reload nginx
    echo "✅ Nginx configured"
}

# Setup SSL with Let's Encrypt
setup_ssl() {
    echo "🔒 Setting up SSL certificate..."
    
    if ! command -v certbot &> /dev/null; then
        sudo apt-get update
        sudo apt-get install -y certbot python3-certbot-nginx
    fi
    
    sudo certbot --nginx -d $DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN
    echo "✅ SSL certificate installed"
}

# Create monitoring script
create_monitoring() {
    echo "📊 Setting up monitoring..."
    
    cat > monitor.sh << 'EOF'
#!/bin/bash
# LAIT System Monitoring Script

LOG_FILE="/var/log/lait/monitor.log"
API_URL="http://localhost:5003/api/health"

check_api() {
    response=$(curl -s -w "%{http_code}" -o /dev/null $API_URL)
    if [ "$response" = "200" ]; then
        echo "$(date): ✅ API is healthy" >> $LOG_FILE
        return 0
    else
        echo "$(date): ❌ API unhealthy (HTTP $response)" >> $LOG_FILE
        return 1
    fi
}

check_disk_space() {
    usage=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
    if [ $usage -gt 85 ]; then
        echo "$(date): ⚠️ Disk usage is at ${usage}%" >> $LOG_FILE
    fi
}

check_memory() {
    mem_usage=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100}')
    if [ $mem_usage -gt 85 ]; then
        echo "$(date): ⚠️ Memory usage is at ${mem_usage}%" >> $LOG_FILE
    fi
}

# Run checks
check_api
check_disk_space
check_memory

# Restart service if API is down
if ! check_api; then
    echo "$(date): 🔄 Restarting LAIT backend service" >> $LOG_FILE
    sudo systemctl restart lait-backend
    sleep 10
    check_api
fi
EOF

    chmod +x monitor.sh
    
    # Add to crontab
    (crontab -l 2>/dev/null; echo "*/5 * * * * $(pwd)/monitor.sh") | crontab -
    echo "✅ Monitoring setup complete"
}

# Create backup script
create_backup() {
    echo "💾 Setting up automated backups..."
    
    cat > backup.sh << 'EOF'
#!/bin/bash
# LAIT Database Backup Script

BACKUP_DIR="/var/backups/lait"
DB_FILE="./backend/lait_production.db"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup database
cp $DB_FILE $BACKUP_DIR/lait_db_$DATE.db

# Compress old backups
find $BACKUP_DIR -name "*.db" -mtime +7 -exec gzip {} \;

# Remove backups older than 30 days
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete

echo "$(date): Database backup completed: lait_db_$DATE.db"
EOF

    chmod +x backup.sh
    
    # Add to crontab (daily at 2 AM)
    (crontab -l 2>/dev/null; echo "0 2 * * * $(pwd)/backup.sh") | crontab -
    echo "✅ Backup system configured"
}

# Initialize database with production data
init_production_db() {
    echo "🗃️ Initializing production database..."
    
    cd backend
    python3 -c "
from db.database import init_database
from seed_data import seed_database
import logging

logging.basicConfig(level=logging.INFO)

print('Initializing production database...')
init_database()

print('Seeding with initial data...')
seed_database()

print('Database initialization complete!')
"
    cd ..
    echo "✅ Production database initialized"
}

# Deploy function
deploy() {
    echo "🚀 Starting LAIT deployment..."
    
    check_requirements
    install_python_deps
    install_node_deps
    build_frontend
    create_env
    init_production_db
    
    # Create log directory
    sudo mkdir -p /var/log/lait
    sudo chown www-data:www-data /var/log/lait
    
    create_systemd_service
    configure_nginx
    setup_ssl
    create_monitoring
    create_backup
    
    # Start services
    sudo systemctl start lait-backend
    sudo systemctl restart nginx
    
    # Verify deployment
    sleep 5
    if curl -f http://localhost:$PORT/api/health > /dev/null 2>&1; then
        echo "✅ Backend is running"
    else
        echo "❌ Backend failed to start"
        exit 1
    fi
    
    echo ""
    echo "🎉 LAIT Deployment Complete!"
    echo "🌐 Application URL: https://$DOMAIN"
    echo "📊 API Health: https://$DOMAIN/api/health"
    echo "🔧 Admin Panel: https://$DOMAIN/admin"
    echo ""
    echo "📋 Post-deployment checklist:"
    echo "  - Test all functionality in browser"
    echo "  - Verify SSL certificate"
    echo "  - Check monitoring dashboard"
    echo "  - Review logs: sudo journalctl -u lait-backend"
    echo "  - Update DNS records if needed"
    echo ""
    echo "🔐 Demo Login Credentials:"
    echo "  Email: admin@lait.com"
    echo "  Password: admin123"
    echo ""
}

# Main execution
case "${1:-deploy}" in
    "deploy")
        deploy
        ;;
    "check")
        check_requirements
        ;;
    "build")
        build_frontend
        ;;
    "monitor")
        ./monitor.sh
        ;;
    "backup")
        ./backup.sh
        ;;
    *)
        echo "Usage: $0 {deploy|check|build|monitor|backup}"
        exit 1
        ;;
esac
