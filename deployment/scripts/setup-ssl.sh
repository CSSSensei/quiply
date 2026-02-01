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

echo "Starting nginx in HTTP-only mode..."
docker-compose -f docker-compose.prod.yml up -d nginx

sleep 5

echo "Requesting SSL certificate..."
docker-compose -f docker-compose.prod.yml run --rm certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    --email $EMAIL \
    --agree-tos \
    --no-eff-email \
    -d $DOMAIN

echo "Restarting nginx with SSL..."
docker-compose -f docker-compose.prod.yml restart nginx

echo "SSL certificate setup completed!"
echo ""
echo "Certificate details:"
docker-compose -f docker-compose.prod.yml run --rm certbot certificates

echo ""
echo "Certificate will auto-renew via certbot container"
