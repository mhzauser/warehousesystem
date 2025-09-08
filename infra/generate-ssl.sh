#!/bin/bash

# SSL Certificate Generator for *.anbaarahan.com
# This script generates a self-signed SSL certificate for wildcard domain

set -e

echo "🔐 Generating SSL Certificate for *.anbaarahan.com..."

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

print_status "Project directory: $PROJECT_DIR"
print_status "SSL directory: $SSL_DIR"

# Create SSL directory if it doesn't exist
mkdir -p "$SSL_DIR"

# Certificate details
DOMAIN="*.anbaarahan.com"
CERT_FILE="$SSL_DIR/anbaarahan.com.crt"
KEY_FILE="$SSL_DIR/anbaarahan.com.key"
CSR_FILE="$SSL_DIR/anbaarahan.com.csr"
CONFIG_FILE="$SSL_DIR/ssl.conf"

print_step "Creating SSL configuration file..."

# Create OpenSSL configuration file
cat > "$CONFIG_FILE" << EOF
[req]
default_bits = 2048
prompt = no
default_md = sha256
distinguished_name = dn
req_extensions = v3_req

[dn]
C=IR
ST=Tehran
L=Tehran
O=Anbaarahan
OU=IT Department
CN=*.anbaarahan.com
emailAddress=admin@anbaarahan.com

[v3_req]
basicConstraints = CA:FALSE
keyUsage = nonRepudiation, digitalSignature, keyEncipherment
subjectAltName = @alt_names

[alt_names]
DNS.1 = *.anbaarahan.com
DNS.2 = anbaarahan.com
DNS.3 = warehouse.anbaarahan.com
DNS.4 = admin.anbaarahan.com
DNS.5 = api.anbaarahan.com
DNS.6 = www.anbaarahan.com
EOF

print_status "SSL configuration file created ✓"

print_step "Generating private key..."
openssl genrsa -out "$KEY_FILE" 2048
print_status "Private key generated ✓"

print_step "Generating certificate signing request..."
openssl req -new -key "$KEY_FILE" -out "$CSR_FILE" -config "$CONFIG_FILE"
print_status "Certificate signing request generated ✓"

print_step "Generating self-signed certificate..."
openssl x509 -req -in "$CSR_FILE" -signkey "$KEY_FILE" -out "$CERT_FILE" -days 365 -extensions v3_req -extfile "$CONFIG_FILE"
print_status "Self-signed certificate generated ✓"

print_step "Setting proper permissions..."
chmod 600 "$KEY_FILE"
chmod 644 "$CERT_FILE"
chmod 644 "$CSR_FILE"
chmod 644 "$CONFIG_FILE"
print_status "Permissions set ✓"

print_step "Certificate information:"
echo ""
openssl x509 -in "$CERT_FILE" -text -noout | grep -A 2 "Subject:"
openssl x509 -in "$CERT_FILE" -text -noout | grep -A 5 "Subject Alternative Name"
openssl x509 -in "$CERT_FILE" -text -noout | grep -A 2 "Validity"

print_status "✅ SSL Certificate generation completed successfully!"
echo ""
echo "📁 Generated files:"
echo "  Certificate: $CERT_FILE"
echo "  Private Key: $KEY_FILE"
echo "  CSR: $CSR_FILE"
echo "  Config: $CONFIG_FILE"
echo ""
echo "🔧 To install on your server:"
echo "  sudo cp $CERT_FILE /etc/ssl/certs/anbaarahan.com.crt"
echo "  sudo cp $KEY_FILE /etc/ssl/private/anbaarahan.com.key"
echo "  sudo chmod 644 /etc/ssl/certs/anbaarahan.com.crt"
echo "  sudo chmod 600 /etc/ssl/private/anbaarahan.com.key"
echo ""
echo "⚠️  Important Notes:"
echo "  - This is a self-signed certificate for development/testing"
echo "  - Browsers will show security warnings"
echo "  - For production, use Let's Encrypt or a trusted CA"
echo "  - Certificate is valid for 365 days"
echo "  - Works for all *.anbaarahan.com subdomains"
echo ""
echo "🌐 Supported domains:"
echo "  - *.anbaarahan.com (wildcard)"
echo "  - anbaarahan.com"
echo "  - warehouse.anbaarahan.com"
echo "  - admin.anbaarahan.com"
echo "  - api.anbaarahan.com"
echo "  - www.anbaarahan.com"
