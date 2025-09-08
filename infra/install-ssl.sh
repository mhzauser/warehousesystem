#!/bin/bash

# SSL Certificate Installer
# This script installs the generated SSL certificate to the system

set -e

echo "🔐 Installing SSL Certificate for *.anbaarahan.com..."

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

# Get the project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SSL_DIR="$PROJECT_DIR/infra/ssl"

CERT_FILE="$SSL_DIR/anbaarahan.com.crt"
KEY_FILE="$SSL_DIR/anbaarahan.com.key"

# Check if certificate files exist
if [ ! -f "$CERT_FILE" ] || [ ! -f "$KEY_FILE" ]; then
    print_error "SSL certificate files not found!"
    print_error "Please run ./infra/generate-ssl.sh first"
    exit 1
fi

print_status "Found certificate files ✓"

# Check if running as root
if [[ $EUID -ne 0 ]]; then
    print_error "This script must be run as root (use sudo)"
    exit 1
fi

print_step "Creating SSL directories..."
mkdir -p /etc/ssl/certs
mkdir -p /etc/ssl/private
print_status "SSL directories created ✓"

print_step "Installing certificate..."
cp "$CERT_FILE" /etc/ssl/certs/anbaarahan.com.crt
print_status "Certificate installed ✓"

print_step "Installing private key..."
cp "$KEY_FILE" /etc/ssl/private/anbaarahan.com.key
print_status "Private key installed ✓"

print_step "Setting proper permissions..."
chmod 644 /etc/ssl/certs/anbaarahan.com.crt
chmod 600 /etc/ssl/private/anbaarahan.com.key
print_status "Permissions set ✓"

print_step "Verifying installation..."
if [ -f "/etc/ssl/certs/anbaarahan.com.crt" ] && [ -f "/etc/ssl/private/anbaarahan.com.key" ]; then
    print_status "SSL certificate installation verified ✓"
else
    print_error "SSL certificate installation failed"
    exit 1
fi

print_step "Testing nginx configuration..."
if nginx -t; then
    print_status "Nginx configuration is valid ✓"
else
    print_warning "Nginx configuration test failed - you may need to update your nginx config"
fi

print_status "✅ SSL Certificate installation completed successfully!"
echo ""
echo "📁 Installed files:"
echo "  Certificate: /etc/ssl/certs/anbaarahan.com.crt"
echo "  Private Key: /etc/ssl/private/anbaarahan.com.key"
echo ""
echo "🔧 Next steps:"
echo "1. Reload nginx: systemctl reload nginx"
echo "2. Test your site: https://warehouse.anbaarahan.com"
echo "3. Accept the security warning in your browser (self-signed certificate)"
echo ""
echo "⚠️  Important Notes:"
echo "  - This is a self-signed certificate"
echo "  - Browsers will show security warnings"
echo "  - For production, use Let's Encrypt or a trusted CA"
echo "  - Certificate works for all *.anbaarahan.com subdomains"
