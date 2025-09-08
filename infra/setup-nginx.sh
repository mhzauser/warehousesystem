#!/bin/bash

# Nginx Setup Script for Warehouse System
# This script sets up nginx as reverse proxy for existing Django application

set -e

echo "🔧 Setting up Nginx for Warehouse System..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root"
   exit 1
fi

# Get the project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
print_status "Project directory: $PROJECT_DIR"

# Step 1: Check if nginx is installed
print_step "Checking nginx installation..."
if ! command -v nginx &> /dev/null; then
    print_error "Nginx is not installed. Please install nginx first:"
    echo "  Ubuntu/Debian: sudo apt update && sudo apt install nginx"
    echo "  CentOS/RHEL: sudo yum install nginx"
    exit 1
fi
print_status "Nginx is installed ✓"

# Step 2: Check if Django is running
print_step "Checking Django application..."
if ! curl -s http://localhost:8000 > /dev/null 2>&1; then
    print_warning "Django application is not running on localhost:8000"
    print_warning "Please make sure your Django application is running before continuing"
    echo ""
    echo "To start Django with Gunicorn:"
    echo "  cd $PROJECT_DIR"
    echo "  gunicorn ironwarehouse.wsgi:application --bind 127.0.0.1:8000 --workers 3"
    echo ""
    read -p "Press Enter to continue anyway, or Ctrl+C to exit..."
else
    print_status "Django application is running on localhost:8000 ✓"
fi

# Step 3: Create nginx configuration
print_step "Creating nginx configuration..."
sudo cp "$PROJECT_DIR/infra/nginx-only.conf" /etc/nginx/sites-available/warehouse.anbaarahan.com
print_status "Nginx configuration copied to sites-available ✓"

# Step 4: Enable the site
print_step "Enabling nginx site..."
if [ ! -L "/etc/nginx/sites-enabled/warehouse.anbaarahan.com" ]; then
    sudo ln -s /etc/nginx/sites-available/warehouse.anbaarahan.com /etc/nginx/sites-enabled/
    print_status "Nginx site enabled ✓"
else
    print_status "Nginx site already enabled ✓"
fi

# Step 5: Remove default nginx site (optional)
print_step "Removing default nginx site..."
if [ -L "/etc/nginx/sites-enabled/default" ]; then
    sudo rm /etc/nginx/sites-enabled/default
    print_status "Default nginx site removed ✓"
else
    print_status "Default nginx site not found ✓"
fi

# Step 6: Test nginx configuration
print_step "Testing nginx configuration..."
if sudo nginx -t; then
    print_status "Nginx configuration is valid ✓"
else
    print_error "Nginx configuration test failed"
    exit 1
fi

# Step 7: Reload nginx
print_step "Reloading nginx..."
sudo systemctl reload nginx
print_status "Nginx reloaded successfully ✓"

# Step 8: Check nginx status
print_step "Checking nginx status..."
if sudo systemctl is-active --quiet nginx; then
    print_status "Nginx is running ✓"
else
    print_warning "Nginx is not running. Starting nginx..."
    sudo systemctl start nginx
fi

# Step 9: SSL Certificate Information
print_step "SSL Certificate Setup"
print_warning "SSL certificates are required for HTTPS to work properly."
echo ""
echo "Certificate files should be placed at:"
echo "  Certificate: /etc/ssl/certs/warehouse.anbaarahan.com.crt"
echo "  Private Key: /etc/ssl/private/warehouse.anbaarahan.com.key"
echo ""
echo "To obtain free SSL certificates with Let's Encrypt:"
echo "  sudo apt install certbot python3-certbot-nginx"
echo "  sudo certbot --nginx -d warehouse.anbaarahan.com"
echo ""

# Step 10: Final instructions
print_status "✅ Nginx setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Configure your DNS to point warehouse.anbaarahan.com to this server"
echo "2. Install SSL certificates (see instructions above)"
echo "3. Make sure your Django application is running on localhost:8000"
echo "4. Configure your firewall to allow HTTP (80) and HTTPS (443) traffic"
echo ""
echo "🔍 Useful commands:"
echo "  Test nginx config: sudo nginx -t"
echo "  Reload nginx: sudo systemctl reload nginx"
echo "  Check nginx status: sudo systemctl status nginx"
echo "  View nginx logs: sudo tail -f /var/log/nginx/warehouse.anbaarahan.com.error.log"
echo ""
echo "🌐 Your site should be accessible at:"
echo "  HTTP: http://warehouse.anbaarahan.com (redirects to HTTPS)"
echo "  HTTPS: https://warehouse.anbaarahan.com (after SSL setup)"
