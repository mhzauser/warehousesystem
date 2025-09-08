# Warehouse System Infrastructure

This directory contains the infrastructure configuration files for the warehouse management system.

## Directory Structure

```
infra/
├── nginx/
│   ├── sites-available/
│   │   └── warehouse.anbaarahan.com    # Nginx configuration
│   └── sites-enabled/
│       └── warehouse.anbaarahan.com    # Symlink to enable the site
├── docker-compose.yml                  # Docker Compose configuration
├── Dockerfile                          # Docker image configuration
├── deploy.sh                           # Deployment script
└── README.md                           # This file
```

## Nginx Configuration

The nginx configuration file `warehouse.anbaarahan.com` includes:

- **SSL/HTTPS Support**: Automatic HTTP to HTTPS redirect
- **Security Headers**: X-Frame-Options, X-Content-Type-Options, etc.
- **Static Files**: Optimized serving of CSS, JS, and images
- **Media Files**: Proper handling of uploaded files
- **Proxy Configuration**: Forwarding requests to Django application
- **Gzip Compression**: Reduced bandwidth usage
- **Logging**: Access and error logs

## Deployment Options

### Option 1: Manual Deployment

1. **Install Dependencies**:
   ```bash
   sudo apt update
   sudo apt install nginx python3-pip python3-venv postgresql-client
   ```

2. **Set up SSL Certificates**:
   ```bash
   # Using Let's Encrypt (recommended)
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d warehouse.anbaarahan.com
   ```

3. **Run Deployment Script**:
   ```bash
   ./infra/deploy.sh
   ```

### Option 2: Docker Deployment

1. **Build and Run with Docker Compose**:
   ```bash
   cd infra
   docker-compose up -d
   ```

2. **Set up SSL Certificates** (if not using Docker for nginx):
   ```bash
   sudo certbot --nginx -d warehouse.anbaarahan.com
   ```

## Configuration Details

### Nginx Configuration Features

- **Domain**: warehouse.anbaarahan.com
- **Ports**: 80 (HTTP), 443 (HTTPS)
- **SSL**: TLS 1.2/1.3 with secure ciphers
- **Static Files**: Served directly by nginx
- **Media Files**: Served directly by nginx
- **Django App**: Proxied to localhost:8000

### Security Features

- HTTP to HTTPS redirect
- Security headers (HSTS, X-Frame-Options, etc.)
- SSL/TLS encryption
- Non-root user in Docker container
- Input validation and sanitization

### Performance Optimizations

- Gzip compression
- Static file caching
- Connection keep-alive
- Optimized nginx worker processes

## SSL Certificate Setup

### Using Let's Encrypt (Recommended)

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d warehouse.anbaarahan.com

# Auto-renewal (already configured by certbot)
sudo certbot renew --dry-run
```

### Using Custom Certificates

1. Place your certificate files:
   - Certificate: `/etc/ssl/certs/warehouse.anbaarahan.com.crt`
   - Private Key: `/etc/ssl/private/warehouse.anbaarahan.com.key`

2. Update file permissions:
   ```bash
   sudo chmod 644 /etc/ssl/certs/warehouse.anbaarahan.com.crt
   sudo chmod 600 /etc/ssl/private/warehouse.anbaarahan.com.key
   ```

## Monitoring and Logs

### Nginx Logs
- Access Log: `/var/log/nginx/warehouse.anbaarahan.com.access.log`
- Error Log: `/var/log/nginx/warehouse.anbaarahan.com.error.log`

### Django Logs
- Application logs: Check Django settings for logging configuration
- System logs: `journalctl -u warehouse-system` (if using systemd)

## Troubleshooting

### Common Issues

1. **SSL Certificate Errors**:
   - Verify certificate files exist and have correct permissions
   - Check certificate validity: `openssl x509 -in /etc/ssl/certs/warehouse.anbaarahan.com.crt -text -noout`

2. **Nginx Configuration Errors**:
   - Test configuration: `sudo nginx -t`
   - Check syntax: `sudo nginx -T`

3. **Django Application Not Starting**:
   - Check Django logs
   - Verify database connection
   - Ensure all dependencies are installed

4. **Static Files Not Loading**:
   - Run `python manage.py collectstatic`
   - Check nginx static file configuration
   - Verify file permissions

### Useful Commands

```bash
# Test nginx configuration
sudo nginx -t

# Reload nginx
sudo systemctl reload nginx

# Check nginx status
sudo systemctl status nginx

# View nginx logs
sudo tail -f /var/log/nginx/warehouse.anbaarahan.com.error.log

# Check Django application
python manage.py check

# Run Django migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput
```

## Maintenance

### Regular Tasks

1. **Update SSL Certificates**: Let's Encrypt certificates auto-renew
2. **Update Dependencies**: Regularly update Python packages and system packages
3. **Monitor Logs**: Check for errors and performance issues
4. **Backup Database**: Regular database backups
5. **Security Updates**: Keep system and packages updated

### Backup Strategy

```bash
# Database backup
pg_dump -h localhost -U warehouse_user warehouse_db > backup_$(date +%Y%m%d).sql

# Media files backup
tar -czf media_backup_$(date +%Y%m%d).tar.gz media/

# Configuration backup
tar -czf config_backup_$(date +%Y%m%d).tar.gz infra/
```
