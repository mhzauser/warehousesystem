#!/bin/bash

# Warehouse System Startup Script
# This script installs all requirements and sets up the service on the server

set -e  # Exit on any error

echo "🚀 Starting Warehouse System Setup..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root. Please run as a regular user with sudo privileges."
   exit 1
fi

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
    libssl-dev \
    libffi-dev \
    git \
    nginx \
    supervisor \
    sqlite3 \
    curl \
    wget \
    unzip

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
    psycopg2-binary \
    python-dotenv \
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

# Database configuration for production (using PostgreSQL)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'warehouse_db'),
        'USER': os.environ.get('DB_USER', 'warehouse_user'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'warehouse_password'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

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

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# Create logs directory
os.makedirs(BASE_DIR / 'logs', exist_ok=True)
EOF

# Create environment file
print_status "Creating environment file..."
cat > .env << 'EOF'
# Database Configuration
DB_NAME=warehouse_db
DB_USER=warehouse_user
DB_PASSWORD=warehouse_password
DB_HOST=localhost
DB_PORT=5432

# Django Configuration
SECRET_KEY=your-secret-key-here-change-this-in-production
DEBUG=False

# Server Configuration
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com
EOF

# Create logs directory
mkdir -p logs

# Run Django migrations
print_status "Running Django migrations..."
python manage.py migrate --settings=ironwarehouse.settings_prod

# Collect static files
print_status "Collecting static files..."
python manage.py collectstatic --noinput --settings=ironwarehouse.settings_prod

# Create superuser (optional)
print_warning "Do you want to create a superuser? (y/n)"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    print_status "Creating superuser..."
    python manage.py createsuperuser --settings=ironwarehouse.settings_prod
fi

# Create Gunicorn configuration
print_status "Creating Gunicorn configuration..."
cat > gunicorn.conf.py << 'EOF'
# Gunicorn configuration file
bind = "127.0.0.1:8000"
workers = 3
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 30
keepalive = 2
preload_app = True
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
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
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

    client_max_body_size 100M;

    location /static/ {
        alias /opt/warehousesystem/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /opt/warehousesystem/media/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
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

# Create health check script
print_status "Creating health check script..."
cat > health_check.sh << 'EOF'
#!/bin/bash
# Health check script for the warehouse system

SERVICE_NAME="warehouse-system"
NGINX_NAME="nginx"

echo "Checking $SERVICE_NAME service status..."
if systemctl is-active --quiet $SERVICE_NAME; then
    echo "✅ $SERVICE_NAME is running"
else
    echo "❌ $SERVICE_NAME is not running"
    echo "Status: $(systemctl status $SERVICE_NAME --no-pager -l)"
fi

echo ""
echo "Checking $NGINX_NAME service status..."
if systemctl is-active --quiet $NGINX_NAME; then
    echo "✅ $NGINX_NAME is running"
else
    echo "❌ $NGINX_NAME is not running"
    echo "Status: $(systemctl status $NGINX_NAME --no-pager -l)"
fi

echo ""
echo "Checking application response..."
if curl -s http://localhost > /dev/null; then
    echo "✅ Application is responding on port 80"
else
    echo "❌ Application is not responding on port 80"
fi

echo ""
echo "Checking Gunicorn process..."
if pgrep -f "gunicorn.*ironwarehouse.wsgi:application" > /dev/null; then
    echo "✅ Gunicorn process is running"
    echo "Processes:"
    pgrep -f "gunicorn.*ironwarehouse.wsgi:application" | xargs ps -o pid,ppid,cmd --no-headers
else
    echo "❌ Gunicorn process is not running"
fi
EOF

chmod +x health_check.sh

# Create maintenance script
print_status "Creating maintenance script..."
cat > maintenance.sh << 'EOF'
#!/bin/bash
# Maintenance script for the warehouse system

SERVICE_NAME="warehouse-system"

case "$1" in
    restart)
        echo "Restarting $SERVICE_NAME..."
        sudo systemctl restart $SERVICE_NAME
        sudo systemctl reload nginx
        echo "Service restarted"
        ;;
    stop)
        echo "Stopping $SERVICE_NAME..."
        sudo systemctl stop $SERVICE_NAME
        echo "Service stopped"
        ;;
    start)
        echo "Starting $SERVICE_NAME..."
        sudo systemctl start $SERVICE_NAME
        echo "Service started"
        ;;
    status)
        echo "Service status:"
        sudo systemctl status $SERVICE_NAME --no-pager -l
        ;;
    logs)
        echo "Recent logs:"
        sudo journalctl -u $SERVICE_NAME -n 50 --no-pager
        ;;
    update)
        echo "Updating application..."
        cd /opt/warehousesystem
        git pull origin main
        source venv/bin/activate
        pip install -r requirements.txt
        python manage.py migrate --settings=ironwarehouse.settings_prod
        python manage.py collectstatic --noinput --settings=ironwarehouse.settings_prod
        sudo systemctl restart $SERVICE_NAME
        echo "Application updated and restarted"
        ;;
    *)
        echo "Usage: $0 {restart|stop|start|status|logs|update}"
        exit 1
        ;;
esac
EOF

chmod +x maintenance.sh

# Create backup script
print_status "Creating backup script..."
cat > backup.sh << 'EOF'
#!/bin/bash
# Backup script for the warehouse system

BACKUP_DIR="/opt/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="warehouse_backup_$DATE"

echo "Creating backup: $BACKUP_NAME"

# Create backup directory
sudo mkdir -p $BACKUP_DIR

# Backup database
echo "Backing up database..."
cd /opt/warehousesystem
source venv/bin/activate
python manage.py dumpdata --settings=ironwarehouse.settings_prod > $BACKUP_DIR/${BACKUP_NAME}_db.json

# Backup media files
echo "Backing up media files..."
sudo tar -czf $BACKUP_DIR/${BACKUP_NAME}_media.tar.gz -C /opt/warehousesystem media/

# Backup application files
echo "Backing up application files..."
sudo tar -czf $BACKUP_DIR/${BACKUP_NAME}_app.tar.gz -C /opt/warehousesystem . --exclude=venv --exclude=*.pyc --exclude=__pycache__

echo "Backup completed: $BACKUP_NAME"
echo "Backup files:"
ls -la $BACKUP_DIR/${BACKUP_NAME}*
EOF

chmod +x backup.sh

# Final status check
print_status "Performing final status check..."
./health_check.sh

print_success "🎉 Warehouse System setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Update the .env file with your production settings"
echo "2. Change the SECRET_KEY in .env file"
echo "3. Update ALLOWED_HOSTS in settings_prod.py"
echo "4. Configure your database (PostgreSQL recommended for production)"
echo "5. Set up SSL certificate for HTTPS"
echo ""
echo "🔧 Useful commands:"
echo "  - Check status: ./health_check.sh"
echo "  - Maintenance: ./maintenance.sh [restart|stop|start|status|logs|update]"
echo "  - Create backup: ./backup.sh"
echo ""
echo "🌐 Your application should now be accessible at: http://localhost"
echo "📁 Application directory: $APP_DIR"
echo "📝 Logs directory: $APP_DIR/logs"
