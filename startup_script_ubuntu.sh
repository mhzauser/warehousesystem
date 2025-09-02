#!/bin/bash

# Warehouse System Startup Script for Ubuntu/Debian
# This script installs all requirements and sets up the service on the server

set -e  # Exit on any error

echo "🚀 Starting Warehouse System Setup on Ubuntu..."

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Update system packages
print_status "Updating system packages..."
sudo apt update -y

# Install system dependencies
print_status "Installing system dependencies..."
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    build-essential \
    nginx \
    sqlite3 \
    curl

# Create application directory
APP_DIR="/opt/warehousesystem"
print_status "Creating application directory: $APP_DIR"
sudo mkdir -p $APP_DIR
sudo chown $USER:$USER $APP_DIR

# Copy project files to application directory
print_status "Copying project files..."
cp -r . $APP_DIR/
cd $APP_DIR

# Create virtual environment
print_status "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install Python requirements
print_status "Installing Python requirements..."
pip install -r requirements.txt

# Install additional production dependencies
print_status "Installing additional production dependencies..."
pip install \
    gunicorn \
    whitenoise

# Create production settings
print_status "Creating production settings..."
cat > ironwarehouse/settings_prod.py << 'EOF'
"""
Production settings for ironwarehouse project.
"""

from .settings import *
import os
from pathlib import Path

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-here-change-this-in-production')

# Update allowed hosts for production
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'your-domain.com']

# Static files configuration
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files configuration
MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = '/media/'

# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Create logs directory
os.makedirs(BASE_DIR / 'logs', exist_ok=True)
EOF

# Create logs directory
mkdir -p logs

# Run Django migrations
print_status "Running Django migrations..."
python manage.py migrate --settings=ironwarehouse.settings_prod

# Collect static files
print_status "Collecting static files..."
python manage.py collectstatic --noinput --settings=ironwarehouse.settings_prod

# Create Gunicorn configuration
print_status "Creating Gunicorn configuration..."
cat > gunicorn.conf.py << 'EOF'
# Gunicorn configuration file
bind = "127.0.0.1:8000"
workers = 3
worker_class = "sync"
timeout = 30
EOF

# Create systemd service file
print_status "Creating systemd service file..."
sudo tee /etc/systemd/system/warehouse-system.service > /dev/null << 'EOF'
[Unit]
Description=Warehouse System Django Application
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/opt/warehousesystem
Environment=PATH=/opt/warehousesystem/venv/bin
ExecStart=/opt/warehousesystem/venv/bin/gunicorn --config gunicorn.conf.py ironwarehouse.wsgi:application
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Create Nginx configuration
print_status "Creating Nginx configuration..."
sudo tee /etc/nginx/sites-available/warehouse-system > /dev/null << 'EOF'
server {
    listen 80;
    server_name localhost;

    location /static/ {
        alias /opt/warehousesystem/staticfiles/;
    }

    location /media/ {
        alias /opt/warehousesystem/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# Enable Nginx site
print_status "Enabling Nginx site..."
sudo ln -sf /etc/nginx/sites-available/warehouse-system /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Set proper permissions
print_status "Setting proper permissions..."
sudo chown -R www-data:www-data $APP_DIR
sudo chmod -R 755 $APP_DIR

# Test Nginx configuration
print_status "Testing Nginx configuration..."
sudo nginx -t

# Reload systemd and start services
print_status "Reloading systemd and starting services..."
sudo systemctl daemon-reload
sudo systemctl enable warehouse-system
sudo systemctl start warehouse-system
sudo systemctl reload nginx

print_success "🎉 Warehouse System setup completed successfully!"
echo ""
echo "🌐 Your application should now be accessible at: http://localhost"
echo "📁 Application directory: $APP_DIR"
echo ""
echo "🔧 Useful commands:"
echo "  - Check status: sudo systemctl status warehouse-system"
echo "  - Restart service: sudo systemctl restart warehouse-system"
echo "  - View logs: sudo journalctl -u warehouse-system -f"
