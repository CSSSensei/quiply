#!/bin/bash

set -e

echo "🚀 Starting Quiply API deployment..."

if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "Please copy env.template to .env and configure it:"
    echo "  cp env.template .env"
    echo "  nano .env"
    exit 1
fi

source .env

echo "Pulling latest changes..."
git pull origin main

echo "Building Docker images..."
docker-compose -f docker-compose.prod.yml build --no-cache

echo "🛑 Stopping existing containers..."
docker-compose -f docker-compose.prod.yml down

echo "🚀 Starting services..."
docker-compose -f docker-compose.prod.yml up -d

echo "⏳ Waiting for database to be ready..."
sleep 10

echo "🗄️  Running database migrations..."
docker-compose -f docker-compose.prod.yml exec -T backend flask db upgrade || \
docker-compose -f docker-compose.prod.yml exec -T backend python init_db.py

echo "Deployment completed successfully!"
echo ""
echo "Service status:"
docker-compose -f docker-compose.prod.yml ps

echo ""
echo "To view logs:"
echo "  docker-compose -f docker-compose.prod.yml logs -f"
echo ""
echo "API should be available at: https://${DOMAIN}"
