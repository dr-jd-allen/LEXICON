#!/bin/sh
# LEXICON Backup Script
# Runs automated backups of all critical data

BACKUP_DIR="/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_PREFIX="lexicon_backup_${TIMESTAMP}"

echo "[$(date)] Starting LEXICON backup..."

# Create backup directory
mkdir -p "${BACKUP_DIR}/${BACKUP_PREFIX}"

# Backup ChromaDB
if [ -d "/data/chromadb" ]; then
    echo "[$(date)] Backing up ChromaDB..."
    tar -czf "${BACKUP_DIR}/${BACKUP_PREFIX}/chromadb.tar.gz" -C /data chromadb
fi

# Backup Redis data
if [ -f "/data/lexicon-dump.rdb" ]; then
    echo "[$(date)] Backing up Redis..."
    cp /data/lexicon-dump.rdb "${BACKUP_DIR}/${BACKUP_PREFIX}/"
    cp /data/lexicon-appendonly.aof "${BACKUP_DIR}/${BACKUP_PREFIX}/" 2>/dev/null || true
fi

# Backup uploaded documents
if [ -d "/data/uploads" ]; then
    echo "[$(date)] Backing up uploaded documents..."
    tar -czf "${BACKUP_DIR}/${BACKUP_PREFIX}/uploads.tar.gz" -C /data uploads
fi

# Backup generated briefs
if [ -d "/data/generated-briefs" ]; then
    echo "[$(date)] Backing up generated briefs..."
    tar -czf "${BACKUP_DIR}/${BACKUP_PREFIX}/briefs.tar.gz" -C /data generated-briefs
fi

# Backup anonymized documents
if [ -d "/data/anonymized" ]; then
    echo "[$(date)] Backing up anonymized documents..."
    tar -czf "${BACKUP_DIR}/${BACKUP_PREFIX}/anonymized.tar.gz" -C /data anonymized
fi

# Create backup manifest
cat > "${BACKUP_DIR}/${BACKUP_PREFIX}/manifest.json" <<EOF
{
  "timestamp": "${TIMESTAMP}",
  "version": "1.0",
  "components": [
    "chromadb",
    "redis",
    "uploads",
    "generated-briefs",
    "anonymized"
  ]
}
EOF

# Compress full backup
cd "${BACKUP_DIR}"
tar -czf "${BACKUP_PREFIX}.tar.gz" "${BACKUP_PREFIX}/"
rm -rf "${BACKUP_PREFIX}/"

# Clean up old backups (keep last 30 days)
find "${BACKUP_DIR}" -name "lexicon_backup_*.tar.gz" -mtime +${BACKUP_RETENTION_DAYS:-30} -delete

echo "[$(date)] Backup completed: ${BACKUP_PREFIX}.tar.gz"

# Verify backup
if [ -f "${BACKUP_DIR}/${BACKUP_PREFIX}.tar.gz" ]; then
    SIZE=$(du -h "${BACKUP_DIR}/${BACKUP_PREFIX}.tar.gz" | cut -f1)
    echo "[$(date)] Backup size: ${SIZE}"
    exit 0
else
    echo "[$(date)] ERROR: Backup failed!"
    exit 1
fi