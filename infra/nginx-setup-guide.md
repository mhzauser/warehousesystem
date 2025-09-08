# Nginx Setup Guide for Warehouse System

This guide helps you set up nginx as a reverse proxy for your existing Django warehouse system.

## Prerequisites

- Django application running on localhost:8000
- Ubuntu/Debian server with sudo access
- Domain name: warehouse.anbaarahan.com

## Quick Setup

### 1. Install Nginx

```bash
sudo apt update
sudo apt install nginx
```

### 2. Run the Setup Script

```bash
./infra/setup-nginx.sh
```

### 3. Set up SSL Certificates (Recommended)

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d warehouse.anbaarahan.com
```

## Manual Setup (Alternative)

If you prefer to set up manually:

### 1. Copy Nginx Configuration

```bash
sudo cp infra/nginx-only.conf /etc/nginx/sites-available/warehouse.anbaarahan.com
```

### 2. Enable the Site

```bash
sudo ln -s /etc/nginx/sites-available/warehouse.anbaarahan.com /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default  # Remove default site
```

### 3. Test and Reload

```bash
sudo nginx -t
sudo systemctl reload nginx
```

## Configuration Details

### Nginx Configuration Features

- **Domain**: warehouse.anbaarahan.com
- **HTTP to HTTPS Redirect**: Automatic redirect from port 80 to 443
- **SSL/TLS**: Secure HTTPS with modern protocols
- **Static Files**: Direct serving of CSS, JS, images
- **Media Files**: Direct serving of uploaded files
- **Django Proxy**: Forwards requests to localhost:8000
- **Security Headers**: HSTS, X-Frame-Options, etc.
- **Gzip Compression**: Reduced bandwidth usage

### File Paths

Make sure these paths match your Django project:

```nginx
# Static files
location /static/ {
    alias /var/www/warehousesystem/static/;
}

# Media files  
location /media/ {
    alias /var/www/warehousesystem/media/;
}
```

If your Django project is in a different location, update these paths in the nginx configuration.

## Django Application Setup

### Start Django with Gunicorn

```bash
cd /path/to/your/warehousesystem
gunicorn ironwarehouse.wsgi:application --bind 127.0.0.1:8000 --workers 3
```

### Create Systemd Service (Optional)

Create `/etc/systemd/system/warehouse-system.service`:

```ini
[Unit]
Description=Warehouse System Django Application
After=network.target

[Service]
Type=exec
User=your_username
Group=your_username
WorkingDirectory=/path/to/your/warehousesystem
ExecStart=/path/to/your/venv/bin/gunicorn ironwarehouse.wsgi:application --bind 127.0.0.1:8000 --workers 3
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable warehouse-system
sudo systemctl start warehouse-system
```

## SSL Certificate Setup

### Using Let's Encrypt (Free)

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d warehouse.anbaarahan.com

# Test auto-renewal
sudo certbot renew --dry-run
```

### Using Custom Certificates

1. Place your certificate files:
   ```bash
   sudo cp your-certificate.crt /etc/ssl/certs/warehouse.anbaarahan.com.crt
   sudo cp your-private-key.key /etc/ssl/private/warehouse.anbaarahan.com.key
   ```

2. Set proper permissions:
   ```bash
   sudo chmod 644 /etc/ssl/certs/warehouse.anbaarahan.com.crt
   sudo chmod 600 /etc/ssl/private/warehouse.anbaarahan.com.key
   ```

## DNS Configuration

Configure your DNS to point warehouse.anbaarahan.com to your server's IP address:

```
A Record: warehouse.anbaarahan.com → YOUR_SERVER_IP
```

## Firewall Configuration

Allow HTTP and HTTPS traffic:

```bash
# UFW (Ubuntu)
sudo ufw allow 'Nginx Full'

# Or manually
sudo ufw allow 80
sudo ufw allow 443
```

## Testing

### Test Nginx Configuration

```bash
sudo nginx -t
```

### Test Django Application

```bash
curl http://localhost:8000
```

### Test Public Access

```bash
curl -I http://warehouse.anbaarahan.com
curl -I https://warehouse.anbaarahan.com
```

## Monitoring and Logs

### Nginx Logs

```bash
# Access logs
sudo tail -f /var/log/nginx/warehouse.anbaarahan.com.access.log

# Error logs
sudo tail -f /var/log/nginx/warehouse.anbaarahan.com.error.log

# General nginx logs
sudo tail -f /var/log/nginx/error.log
```

### Django Logs

```bash
# If using systemd service
sudo journalctl -u warehouse-system -f

# If running manually, check your Django logs
```

## Troubleshooting

### Common Issues

1. **502 Bad Gateway**
   - Check if Django is running: `curl http://localhost:8000`
   - Check Django logs for errors
   - Verify nginx proxy configuration

2. **SSL Certificate Errors**
   - Verify certificate files exist and have correct permissions
   - Check certificate validity: `openssl x509 -in /etc/ssl/certs/warehouse.anbaarahan.com.crt -text -noout`

3. **Static Files Not Loading**
   - Run Django collectstatic: `python manage.py collectstatic`
   - Check nginx static file configuration
   - Verify file permissions

4. **Nginx Configuration Errors**
   - Test configuration: `sudo nginx -t`
   - Check syntax: `sudo nginx -T`

### Useful Commands

```bash
# Nginx management
sudo systemctl status nginx
sudo systemctl restart nginx
sudo systemctl reload nginx

# Check nginx configuration
sudo nginx -t
sudo nginx -T

# Check listening ports
sudo netstat -tlnp | grep :80
sudo netstat -tlnp | grep :443

# Check Django process
ps aux | grep gunicorn
```

## Security Considerations

1. **Keep nginx updated**: `sudo apt update && sudo apt upgrade nginx`
2. **Use strong SSL configuration**: Already configured in the provided config
3. **Regular security updates**: `sudo apt update && sudo apt upgrade`
4. **Monitor logs**: Set up log monitoring for security events
5. **Firewall**: Only allow necessary ports (22, 80, 443)

## Performance Optimization

The nginx configuration includes several optimizations:

- **Gzip compression**: Reduces bandwidth usage
- **Static file caching**: Improves load times
- **Connection keep-alive**: Reduces connection overhead
- **Security headers**: Protects against common attacks

For high-traffic sites, consider additional optimizations:

- Enable nginx caching
- Use CDN for static files
- Implement database connection pooling
- Add load balancing for multiple Django instances
