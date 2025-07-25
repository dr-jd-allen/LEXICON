#!/bin/sh
# LEXICON Restore Script
# Restores data from backup

BACKUP_DIR="/backups"
DATA_DIR="/data"

if [ -z "$1" ]; then
    echo "Usage: ./restore.sh <backup_file>"
    echo "Available backups:"
    ls -la ${BACKUP_DIR}/lexicon_backup_*.tar.gz
    exit 1
fi

BACKUP_FILE="$1"

if [ ! -f "${BACKUP_FILE}" ]; then
    echo "ERROR: Backup file not found: ${BACKUP_FILE}"
    exit 1
fi

echo "[$(date)] Starting restore from ${BACKUP_FILE}..."

# Create temp directory
TEMP_DIR="/tmp/restore_$$"
mkdir -p "${TEMP_DIR}"

# Extract backup
echo "[$(date)] Extracting backup..."
tar -xzf "${BACKUP_FILE}" -C "${TEMP_DIR}"

# Find the backup directory
BACKUP_NAME=$(basename "${BACKUP_FILE}" .tar.gz)

# Stop services before restore
echo "[$(date)] Please ensure all services are stopped before proceeding."
echo "Press Enter to continue or Ctrl+C to cancel..."
read

# Restore ChromaDB
if [ -f "${TEMP_DIR}/${BACKUP_NAME}/chromadb.tar.gz" ]; then
    echo "[$(date)] Restoring ChromaDB..."
    rm -rf "${DATA_DIR}/chromadb"
    tar -xzf "${TEMP_DIR}/${BACKUP_NAME}/chromadb.tar.gz" -C "${DATA_DIR}"
fi

# Restore Redis
if [ -f "${TEMP_DIR}/${BACKUP_NAME}/lexicon-dump.rdb" ]; then
    echo "[$(date)] Restoring Redis..."
    cp "${TEMP_DIR}/${BACKUP_NAME}/lexicon-dump.rdb" "${DATA_DIR}/"
    [ -f "${TEMP_DIR}/${BACKUP_NAME}/lexicon-appendonly.aof" ] && \
        cp "${TEMP_DIR}/${BACKUP_NAME}/lexicon-appendonly.aof" "${DATA_DIR}/"
fi

# Restore uploads
if [ -f "${TEMP_DIR}/${BACKUP_NAME}/uploads.tar.gz" ]; then
    echo "[$(date)] Restoring uploaded documents..."
    rm -rf "${DATA_DIR}/uploads"
    tar -xzf "${TEMP_DIR}/${BACKUP_NAME}/uploads.tar.gz" -C "${DATA_DIR}"
fi

# Restore briefs
if [ -f "${TEMP_DIR}/${BACKUP_NAME}/briefs.tar.gz" ]; then
    echo "[$(date)] Restoring generated briefs..."
    rm -rf "${DATA_DIR}/generated-briefs"
    tar -xzf "${TEMP_DIR}/${BACKUP_NAME}/briefs.tar.gz" -C "${DATA_DIR}"
fi

# Restore anonymized
if [ -f "${TEMP_DIR}/${BACKUP_NAME}/anonymized.tar.gz" ]; then
    echo "[$(date)] Restoring anonymized documents..."
    rm -rf "${DATA_DIR}/anonymized"
    tar -xzf "${TEMP_DIR}/${BACKUP_NAME}/anonymized.tar.gz" -C "${DATA_DIR}"
fi

# Clean up
rm -rf "${TEMP_DIR}"

echo "[$(date)] Restore completed!"
echo "[$(date)] Please restart all services."