# Warehouse System Deployment Guide

This guide explains how to deploy the Warehouse System Django application on a production server.

## 🚀 Quick Start

### Prerequisites
- Ubuntu 20.04+ or Debian 11+ server
- User with sudo privileges
- SSH access to the server

### Automated Deployment

1. **Upload the startup script to your server:**
   ```bash
   scp startup_script_ubuntu.sh user@your-server:/home/user/
   ```

2. **Make the script executable and run it:**
   ```bash
   ssh user@your-server
   chmod +x startup_script_ubuntu.sh
   ./startup_script_ubuntu.sh
   ```

The script will automatically:
- Install all system dependencies
- Set up Python virtual environment
- Install Python packages
- Configure Nginx and systemd service
- Start the application

## 📋 Manual Deployment Steps

If you prefer to deploy manually, follow these steps:

### 1. System Dependencies
```bash
sudo apt update -y
sudo apt install -y python3 python3-pip python3-venv python3-dev build-essential nginx sqlite3 curl
```

### 2. Application Setup
```bash
# Create application directory
sudo mkdir -p /opt/warehousesystem
sudo chown $USER:$USER /opt/warehousesystem

# Copy project files
cp -r . /opt/warehousesystem/
cd /opt/warehousesystem

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn whitenoise
```

### 3. Django Configuration
```bash
# Create production settings
# (The startup script creates this automatically)

# Run migrations
python manage.py migrate --settings=ironwarehouse.settings_prod

# Collect static files
python manage.py collectstatic --noinput --settings=ironwarehouse.settings_prod
```

### 4. Service Configuration
```bash
# Create systemd service
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

# Enable site
sudo ln -sf /etc/nginx/sites-available/warehouse-system /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
```

### 5. Start Services
```bash
# Set permissions
sudo chown -R www-data:www-data /opt/warehousesystem
sudo chmod -R 755 /opt/warehousesystem

# Test Nginx
sudo nginx -t

# Start services
sudo systemctl daemon-reload
sudo systemctl enable warehouse-system
sudo systemctl start warehouse-system
sudo systemctl reload nginx
```

## 🔧 Service Management

### Check Service Status
```bash
sudo systemctl status warehouse-system
sudo systemctl status nginx
```

### Restart Service
```bash
sudo systemctl restart warehouse-system
sudo systemctl reload nginx
```

### View Logs
```bash
# Django application logs
sudo journalctl -u warehouse-system -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Stop Service
```bash
sudo systemctl stop warehouse-system
```

## 📁 File Structure After Deployment

```
/opt/warehousesystem/
├── venv/                    # Python virtual environment
├── ironwarehouse/          # Django project
├── inventory/              # Django app
├── manage.py              # Django management script
├── requirements.txt        # Python dependencies
├── gunicorn.conf.py       # Gunicorn configuration
├── staticfiles/           # Collected static files
├── media/                 # User uploaded files
├── logs/                  # Application logs
└── db.sqlite3            # Database file
```

## 🔒 Security Considerations

### 1. Update Secret Key
```bash
# Generate a new secret key
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Update in .env file
nano /opt/warehousesystem/.env
```

### 2. Configure Firewall
```bash
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS (if using SSL)
sudo ufw enable
```

### 3. SSL Certificate (Recommended)
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 🗄️ Database Configuration

### SQLite (Default)
The system uses SQLite by default, which is suitable for small to medium deployments.

### PostgreSQL (Recommended for Production)
```bash
# Install PostgreSQL
sudo apt install postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql
CREATE DATABASE warehouse_db;
CREATE USER warehouse_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE warehouse_db TO warehouse_user;
\q

# Update .env file
DB_ENGINE=django.db.backends.postgresql
DB_NAME=warehouse_db
DB_USER=warehouse_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

## 📊 Monitoring and Maintenance

### Health Check
```bash
# Check if application is responding
curl -I http://localhost

# Check service status
sudo systemctl is-active warehouse-system
sudo systemctl is-active nginx
```

### Backup
```bash
# Database backup
cd /opt/warehousesystem
source venv/bin/activate
python manage.py dumpdata --settings=ironwarehouse.settings_prod > backup_$(date +%Y%m%d_%H%M%S).json

# Files backup
sudo tar -czf backup_$(date +%Y%m%d_%H%M%S).tar.gz /opt/warehousesystem/media/ /opt/warehousesystem/staticfiles/
```

### Updates
```bash
cd /opt/warehousesystem
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate --settings=ironwarehouse.settings_prod
python manage.py collectstatic --noinput --settings=ironwarehouse.settings_prod
sudo systemctl restart warehouse-system
```

## 🚨 Troubleshooting

### Common Issues

1. **Permission Denied**
   ```bash
   sudo chown -R www-data:www-data /opt/warehousesystem
   sudo chmod -R 755 /opt/warehousesystem
   ```

2. **Port Already in Use**
   ```bash
   sudo netstat -tlnp | grep :8000
   sudo pkill -f gunicorn
   ```

3. **Nginx Configuration Error**
   ```bash
   sudo nginx -t
   sudo systemctl status nginx
   ```

4. **Django Migration Issues**
   ```bash
   cd /opt/warehousesystem
   source venv/bin/activate
   python manage.py showmigrations --settings=ironwarehouse.settings_prod
   python manage.py migrate --settings=ironwarehouse.settings_prod
   ```

### Log Analysis
```bash
# Check Django logs
tail -f /opt/warehousesystem/logs/django.log

# Check system logs
sudo journalctl -u warehouse-system -f

# Check Nginx logs
sudo tail -f /var/log/nginx/error.log
```

## 📞 Support

If you encounter issues during deployment:

1. Check the logs for error messages
2. Verify all services are running
3. Ensure proper file permissions
4. Check firewall and network configuration

## 🔄 Next Steps

After successful deployment:

1. **Create Superuser**: Access Django admin at `http://your-server/admin/`
2. **Configure Domain**: Update `ALLOWED_HOSTS` in production settings
3. **Set Up Monitoring**: Configure log rotation and monitoring tools
4. **Performance Tuning**: Adjust Gunicorn workers and Nginx settings based on server resources
5. **Regular Maintenance**: Set up automated backups and updates

---

**Note**: This deployment guide assumes a fresh Ubuntu/Debian server. Adjust commands for your specific server environment and requirements.
