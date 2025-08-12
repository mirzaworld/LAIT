#!/bin/sh
# Frontend entrypoint script for LAIT
# Configures nginx with backend URL from environment variable

set -e

echo "🚀 Starting LAIT Frontend with Nginx"
echo "=================================="

# Default backend URL if not provided
BACKEND_URL=${BACKEND_URL:-"localhost:5003"}

echo "🔧 Configuration:"
echo "   Backend URL: ${BACKEND_URL}"
echo "   Frontend Port: 80"

# Replace placeholder in nginx config with actual backend URL
sed -i "s/backend_placeholder/${BACKEND_URL}/g" /etc/nginx/nginx.conf

echo "📋 Nginx configuration updated"

# Validate nginx configuration
nginx -t

echo "✅ Nginx configuration is valid"
echo "🎯 Starting nginx server..."

# Start nginx in foreground
exec nginx -g 'daemon off;'
