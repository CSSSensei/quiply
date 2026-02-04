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

export DOCKER_BUILDKIT=1
export BUILDKIT_PROGRESS=plain

echo "Pulling latest changes..."
git pull origin main

echo "Pruning unused Docker resources..."
docker system prune -f
docker volume prune -f

echo "Building Docker images with optimizations..."

docker compose -f docker-compose.prod.yml build \
    --parallel \
    --progress=plain \
    --no-cache

echo "Stopping existing containers..."
docker compose -f docker-compose.prod.yml down

docker network prune -f

echo "Starting services..."
docker compose -f docker-compose.prod.yml up -d

echo "Waiting for database to be ready..."
sleep 10

echo "Running database migrations..."
docker compose -f docker-compose.prod.yml exec -T backend flask db upgrade || \
docker compose -f docker-compose.prod.yml exec -T backend python init_db.py

echo "Deployment completed successfully!"
echo ""
echo "Service status:"
docker compose -f docker-compose.prod.yml ps

echo ""
echo "Container health status:"
docker compose -f docker-compose.prod.yml ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "To view logs:"
echo "  docker compose -f docker-compose.prod.yml logs -f"
echo ""
echo "API should be available at: https://${DOMAIN}"

echo ""
echo "Resource usage:"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"
