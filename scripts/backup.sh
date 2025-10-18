#!/bin/bash

# ServiceHub Backup Script
# Faz backup do banco de dados e arquivos

set -e

# Configuration
BACKUP_DIR="/backups/servicehub"
RETENTION_DAYS=30
DATE=$(date +%Y%m%d_%H%M%S)
LOG_FILE="/var/log/servicehub-backup.log"

# Create backup directory
mkdir -p $BACKUP_DIR

# Logging function
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a $LOG_FILE
}

log "Starting ServiceHub backup..."

# Backup PostgreSQL Database
log "Backing up PostgreSQL database..."
docker-compose -f /home/ubuntu/servicehub/docker-compose.prod.yml exec -T db pg_dump -U servicehub servicehub | gzip > $BACKUP_DIR/database_$DATE.sql.gz

if [ $? -eq 0 ]; then
    log "✓ Database backup completed: database_$DATE.sql.gz"
else
    log "✗ Database backup failed!"
    exit 1
fi

# Backup Redis
log "Backing up Redis..."
docker-compose -f /home/ubuntu/servicehub/docker-compose.prod.yml exec -T redis redis-cli BGSAVE
sleep 5
docker cp servicehub-redis:/data/dump.rdb $BACKUP_DIR/redis_$DATE.rdb

if [ $? -eq 0 ]; then
    log "✓ Redis backup completed: redis_$DATE.rdb"
else
    log "✗ Redis backup failed!"
fi

# Backup Media Files
log "Backing up media files..."
tar -czf $BACKUP_DIR/media_$DATE.tar.gz -C /home/ubuntu/servicehub/backend media/ 2>/dev/null || true

if [ $? -eq 0 ]; then
    log "✓ Media backup completed: media_$DATE.tar.gz"
else
    log "✗ Media backup failed!"
fi

# Backup Static Files
log "Backing up static files..."
tar -czf $BACKUP_DIR/static_$DATE.tar.gz -C /home/ubuntu/servicehub/backend staticfiles/ 2>/dev/null || true

if [ $? -eq 0 ]; then
    log "✓ Static files backup completed: static_$DATE.tar.gz"
else
    log "✗ Static files backup failed!"
fi

# Cleanup old backups
log "Cleaning up old backups (older than $RETENTION_DAYS days)..."
find $BACKUP_DIR -type f -mtime +$RETENTION_DAYS -delete

if [ $? -eq 0 ]; then
    log "✓ Old backups cleaned up"
else
    log "✗ Cleanup failed!"
fi

# Calculate backup size
BACKUP_SIZE=$(du -sh $BACKUP_DIR | cut -f1)
log "Total backup size: $BACKUP_SIZE"

# Upload to S3 (optional)
if [ ! -z "$AWS_S3_BUCKET" ]; then
    log "Uploading backups to S3..."
    aws s3 sync $BACKUP_DIR s3://$AWS_S3_BUCKET/backups/servicehub/ --delete
    
    if [ $? -eq 0 ]; then
        log "✓ Backups uploaded to S3"
    else
        log "✗ S3 upload failed!"
    fi
fi

log "Backup completed successfully!"

