#!/bin/bash

set -e

echo "🔐 Setting up SSL certificates with Let's Encrypt..."

if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    exit 1
fi

source .env

if [ -z "$DOMAIN" ] || [ -z "$EMAIL" ]; then
    echo "❌ Error: DOMAIN and EMAIL must be set in .env file"
    exit 1
fi

echo "Email: $EMAIL"
echo "Domain: $DOMAIN"

mkdir -p certbot/conf
mkdir -p certbot/www

echo "Switching to HTTP-only nginx configuration..."
if [ -f nginx/conf.d/api.conf ]; then
    mv nginx/conf.d/api.conf nginx/conf.d/api.conf.ssl
fi
if [ ! -f nginx/conf.d/api-http-only.conf ]; then
    echo "Error: api-http-only.conf not found!"
    exit 1
fi

echo "Starting nginx in HTTP-only mode..."
docker compose -f docker-compose.prod.yml up -d nginx

echo "Waiting for nginx to start..."
sleep 5

echo "Requesting SSL certificate from Let's Encrypt..."
docker compose -f docker-compose.prod.yml run --rm --entrypoint certbot certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    --email $EMAIL \
    --agree-tos \
    --no-eff-email \
    -d $DOMAIN

if [ ! -d "certbot/conf/live/$DOMAIN" ]; then
    echo "Error: Certificate was not obtained!"
    echo "Please check:"
    echo "  1. Domain $DOMAIN points to this server's IP"
    echo "  2. Ports 80 and 443 are open"
    echo "  3. Check certbot logs above for errors"
    exit 1
fi

echo "Switching to HTTPS nginx configuration..."
rm -f nginx/conf.d/api-http-only.conf
if [ -f nginx/conf.d/api.conf.ssl ]; then
    mv nginx/conf.d/api.conf.ssl nginx/conf.d/api.conf
fi

echo "Restarting nginx with SSL..."
docker compose -f docker-compose.prod.yml restart nginx

echo "SSL certificate setup completed!"
echo ""
echo "Certificate details:"
docker compose -f docker-compose.prod.yml run --rm --entrypoint certbot certbot certificates

echo ""
echo "Certificate will auto-renew via certbot container"
echo "Your API is now available at: https://$DOMAIN"
