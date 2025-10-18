#!/bin/bash

# Setup Cron Jobs for ServiceHub

set -e

echo "Setting up cron jobs for ServiceHub..."

# Make backup script executable
chmod +x /home/ubuntu/servicehub/scripts/backup.sh

# Create crontab entry
CRON_JOB="0 2 * * * /home/ubuntu/servicehub/scripts/backup.sh >> /var/log/servicehub-backup.log 2>&1"

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "servicehub/scripts/backup.sh"; then
    echo "✓ Cron job already exists"
else
    # Add cron job
    (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
    echo "✓ Cron job added: Daily backup at 2:00 AM"
fi

# Setup log rotation
cat > /etc/logrotate.d/servicehub << 'EOF'
/var/log/servicehub-backup.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 root root
    sharedscripts
}
EOF

echo "✓ Log rotation configured"

# Create backup directory
mkdir -p /backups/servicehub
chmod 755 /backups/servicehub

echo "✓ Backup directory created"

echo ""
echo "Cron setup completed!"
echo ""
echo "Scheduled tasks:"
echo "  - Daily backup at 2:00 AM"
echo ""
echo "View cron jobs:"
echo "  crontab -l"
echo ""
echo "View backup logs:"
echo "  tail -f /var/log/servicehub-backup.log"

