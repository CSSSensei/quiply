#!/bin/bash

set -e

echo "Creating database backup..."

if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    exit 1
fi

source .env

BACKUP_DIR="backups"
mkdir -p $BACKUP_DIR

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/quiply_db_${TIMESTAMP}.sql"

echo "Backing up database to: $BACKUP_FILE"

docker-compose -f docker-compose.prod.yml exec -T db pg_dump \
    -U $POSTGRES_USER \
    -d $POSTGRES_DB \
    > $BACKUP_FILE

gzip $BACKUP_FILE

echo "Backup completed: ${BACKUP_FILE}.gz"

echo "Cleaning old backups (keeping last 7)..."
ls -t ${BACKUP_DIR}/quiply_db_*.sql.gz | tail -n +8 | xargs -r rm

echo "Available backups:"
ls -lh ${BACKUP_DIR}/
