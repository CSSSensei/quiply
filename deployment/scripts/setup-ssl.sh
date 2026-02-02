#!/bin/bash

# SSL Certificate Setup Script for Quiply API
# This script obtains and configures Let's Encrypt SSL certificates
#
# Steps performed:
# 1. Validate environment variables (DOMAIN, EMAIL)
# 2. Create certbot directories
# 3. Switch nginx to HTTP-only mode (for ACME challenge)
# 4. Request SSL certificate from Let's Encrypt
# 5. Fix permissions on certificate directories
# 6. Switch nginx to HTTPS mode
# 7. Restart nginx with SSL configuration

set -e

echo "🔐 Setting up SSL certificates with Let's Encrypt..."

# Step 1: Validate environment
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "Please copy env.template to .env and configure it:"
    echo "  cp env.template .env"
    echo "  nano .env"
    exit 1
fi

source .env

if [ -z "$DOMAIN" ] || [ -z "$EMAIL" ]; then
    echo "❌ Error: DOMAIN and EMAIL must be set in .env file"
    exit 1
fi

echo "Email: $EMAIL"
echo "Domain: $DOMAIN"

# Step 2: Create certbot directories
echo "Creating certbot directories..."
mkdir -p certbot/conf
mkdir -p certbot/www

# Step 3: Switch to HTTP-only nginx configuration
echo "Switching to HTTP-only nginx configuration..."
if [ -f nginx/conf.d/api.conf ]; then
    mv nginx/conf.d/api.conf nginx/conf.d/api.conf.ssl
    echo "  Moved api.conf -> api.conf.ssl"
fi

# Restore HTTP-only config if it was backed up
if [ -f nginx/conf.d/api-http-only.conf.bak ]; then
    mv nginx/conf.d/api-http-only.conf.bak nginx/conf.d/api-http-only.conf
    echo "  Restored api-http-only.conf from backup"
fi

if [ ! -f nginx/conf.d/api-http-only.conf ]; then
    echo "❌ Error: api-http-only.conf not found!"
    echo "Please ensure nginx/conf.d/api-http-only.conf exists"
    exit 1
fi

echo "Starting nginx in HTTP-only mode..."
docker compose -f docker-compose.prod.yml up -d nginx

echo "Waiting for nginx to start..."
sleep 5

# Step 4: Request SSL certificate
echo "Requesting SSL certificate from Let's Encrypt..."
docker compose -f docker-compose.prod.yml run --rm --entrypoint certbot certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    --email $EMAIL \
    --agree-tos \
    --no-eff-email \
    -d $DOMAIN

# Step 5: Fix permissions on certificate directories
# Certbot creates directories with 700 permissions, but nginx needs to read them
echo "Fixing certificate directory permissions..."
if [ -d "certbot/conf/live" ]; then
    sudo chmod 755 certbot/conf/live
    echo "  Fixed permissions on certbot/conf/live"
fi
if [ -d "certbot/conf/archive" ]; then
    sudo chmod 755 certbot/conf/archive
    echo "  Fixed permissions on certbot/conf/archive"
fi

# Verify certificate was obtained (use sudo to check due to permissions)
if ! sudo test -d "certbot/conf/live/$DOMAIN"; then
    echo "❌ Error: Certificate was not obtained!"
    echo "Please check:"
    echo "  1. Domain $DOMAIN points to this server's IP"
    echo "  2. Ports 80 and 443 are open"
    echo "  3. Check certbot logs above for errors"
    exit 1
fi

echo "✅ Certificate obtained successfully!"

# Step 6: Switch to HTTPS nginx configuration
echo "Switching to HTTPS nginx configuration..."

# Backup HTTP-only config (don't delete it)
if [ -f nginx/conf.d/api-http-only.conf ]; then
    mv nginx/conf.d/api-http-only.conf nginx/conf.d/api-http-only.conf.bak
    echo "  Backed up api-http-only.conf -> api-http-only.conf.bak"
fi

# Restore SSL config
if [ -f nginx/conf.d/api.conf.ssl ]; then
    mv nginx/conf.d/api.conf.ssl nginx/conf.d/api.conf
    echo "  Restored api.conf from api.conf.ssl"
fi

# Step 7: Restart nginx with SSL
echo "Restarting nginx with SSL..."
docker compose -f docker-compose.prod.yml restart nginx

# Wait for nginx to start and verify it's running
sleep 3
if ! docker compose -f docker-compose.prod.yml ps nginx | grep -q "Up"; then
    echo "⚠️  Warning: nginx may not have started correctly"
    echo "Check logs with: docker compose -f docker-compose.prod.yml logs nginx"
fi

echo ""
echo "✅ SSL certificate setup completed!"
echo ""
echo "Certificate details:"
docker compose -f docker-compose.prod.yml run --rm --entrypoint certbot certbot certificates

echo ""
echo "📋 Summary:"
echo "  - Certificate location: certbot/conf/live/$DOMAIN/"
echo "  - Certificate will auto-renew via certbot container"
echo "  - Your API is now available at: https://$DOMAIN"
echo ""
echo "To verify HTTPS is working:"
echo "  curl https://$DOMAIN/api/v1/health"
