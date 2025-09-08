#!/bin/bash

# Warehouse System Deployment Script
# This script deploys the warehouse system with nginx configuration

set -e

echo "🚀 Starting Warehouse System Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root"
   exit 1
fi

# Check if nginx is installed
if ! command -v nginx &> /dev/null; then
    print_error "Nginx is not installed. Please install nginx first."
    exit 1
fi

# Check if SSL certificates exist
SSL_CERT="/etc/ssl/certs/warehouse.anbaarahan.com.crt"
SSL_KEY="/etc/ssl/private/warehouse.anbaarahan.com.key"

if [ ! -f "$SSL_CERT" ] || [ ! -f "$SSL_KEY" ]; then
    print_warning "SSL certificates not found. Please ensure SSL certificates are installed:"
    print_warning "  Certificate: $SSL_CERT"
    print_warning "  Private Key: $SSL_KEY"
    print_warning "You can use Let's Encrypt or your own certificates."
fi

# Get the project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
print_status "Project directory: $PROJECT_DIR"

# Copy nginx configuration
print_status "Setting up nginx configuration..."
sudo cp "$PROJECT_DIR/infra/nginx/sites-available/warehouse.anbaarahan.com" /etc/nginx/sites-available/

# Create symlink to enable the site
if [ ! -L "/etc/nginx/sites-enabled/warehouse.anbaarahan.com" ]; then
    sudo ln -s /etc/nginx/sites-available/warehouse.anbaarahan.com /etc/nginx/sites-enabled/
    print_status "Nginx site enabled"
else
    print_status "Nginx site already enabled"
fi

# Test nginx configuration
print_status "Testing nginx configuration..."
if sudo nginx -t; then
    print_status "Nginx configuration is valid"
else
    print_error "Nginx configuration test failed"
    exit 1
fi

# Reload nginx
print_status "Reloading nginx..."
sudo systemctl reload nginx

# Set up Django application
print_status "Setting up Django application..."
cd "$PROJECT_DIR"

# Install Python dependencies
if [ -f "requirements.txt" ]; then
    print_status "Installing Python dependencies..."
    pip install -r requirements.txt
fi

# Run Django migrations
print_status "Running Django migrations..."
python manage.py migrate

# Collect static files
print_status "Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser (optional)
print_warning "Do you want to create a superuser? (y/n)"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    python manage.py createsuperuser
fi

# Set up systemd service (optional)
print_warning "Do you want to set up a systemd service for the Django app? (y/n)"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    cat > /tmp/warehouse-system.service << EOF
[Unit]
Description=Warehouse System Django Application
After=network.target

[Service]
Type=exec
User=$USER
Group=$USER
WorkingDirectory=$PROJECT_DIR
Environment=PATH=$PROJECT_DIR/venv/bin
ExecStart=$PROJECT_DIR/venv/bin/gunicorn ironwarehouse.wsgi:application --bind 127.0.0.1:8000 --workers 3
Restart=always

[Install]
WantedBy=multi-user.target
EOF
    
    sudo mv /tmp/warehouse-system.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable warehouse-system
    sudo systemctl start warehouse-system
    print_status "Systemd service created and started"
fi

print_status "✅ Deployment completed successfully!"
print_status "Your warehouse system should now be accessible at: https://warehouse.anbaarahan.com"
print_warning "Make sure to:"
print_warning "1. Configure your DNS to point warehouse.anbaarahan.com to this server"
print_warning "2. Install SSL certificates if not already done"
print_warning "3. Configure your firewall to allow HTTP (80) and HTTPS (443) traffic"
