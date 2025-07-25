# LEXICON Local Deployment Guide

## Overview

This guide covers deploying LEXICON locally with persistent storage, automated backups, and professional hosting setup.

## Prerequisites

1. **Docker Desktop** (Windows/Mac) or Docker Engine (Linux)
2. **Node.js** 18+ and npm
3. **Minimum 8GB RAM** (16GB recommended)
4. **50GB free disk space** for documents and backups
5. **Windows 10/11**, macOS 10.15+, or Linux

## Quick Start

### Windows (PowerShell)
```powershell
# Run with default settings
.\deploy-local.ps1

# Advanced options
.\deploy-local.ps1 -GenerateSSL -EnableMonitoring
```

### Windows (Command Prompt)
```batch
deploy-local.bat
```

### Linux/macOS
```bash
chmod +x deploy-local.sh
./deploy-local.sh
```

## Architecture

### Local Storage Structure
```
lexicon-mvp-alpha/
├── local-storage/
│   ├── chromadb/           # Vector database (8,505+ documents)
│   ├── redis/              # Cache and session data
│   ├── uploads/            # User uploaded documents
│   ├── generated-briefs/   # Generated legal briefs
│   ├── anonymized/         # HIPAA-compliant anonymized docs
│   ├── case-summaries/     # AI-generated case summaries
│   └── strategic-recommendations/  # Strategic advice
├── backups/
│   ├── daily/              # Automated daily backups
│   ├── weekly/             # Weekly full backups
│   └── monthly/            # Monthly archives
└── logs/
    ├── nginx/              # Web server logs
    ├── webapp/             # Application logs
    └── agents/             # AI agent logs
```

### Services

1. **Nginx** (Ports 80, 443, 8000)
   - Static file serving
   - API gateway
   - WebSocket proxy
   - SSL termination

2. **ChromaDB** (Port 8100)
   - Vector database
   - Document embeddings
   - Semantic search
   - Token authentication

3. **Redis** (Port 6379)
   - Session management
   - Real-time updates
   - Inter-agent communication
   - Persistent storage with AOF

4. **Web Application** (Port 5000)
   - Flask backend
   - Socket.IO real-time
   - Document processing
   - Agent orchestration

5. **File Server** (Port 8080)
   - Generated briefs access
   - Document downloads
   - Web-based file browser

## Security Configuration

### 1. Generate SSL Certificates

#### Self-Signed (Development)
```powershell
.\deploy-local.ps1 -GenerateSSL
```

#### Let's Encrypt (Production)
```bash
certbot certonly --standalone -d lexicon.yourdomain.com
```

### 2. Environment Variables

Edit `.env` file:
```env
# API Keys (Required)
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=AIza...
SERPAPI_API_KEY=...

# Security (Auto-generated if blank)
SECRET_KEY=your-secret-key
CHROMA_AUTH_TOKEN=your-chroma-token
REDIS_PASSWORD=your-redis-password

# Optional Services
COURTLISTENER_API_KEY=...
COURTWHISPERER_API_KEY=...
FIRECRAWL_API_KEY=...
PUBMED_API_KEY=...
```

### 3. Firewall Rules

Windows PowerShell (Admin):
```powershell
# Allow LEXICON ports
New-NetFirewallRule -DisplayName "LEXICON Web" -Direction Inbound -LocalPort 80,443 -Protocol TCP -Action Allow
New-NetFirewallRule -DisplayName "LEXICON API" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
```

## Data Management

### Automated Backups

Backups run daily at 2 AM and include:
- ChromaDB vector database
- Redis data (RDB + AOF)
- All uploaded documents
- Generated briefs
- Anonymized documents

### Manual Backup
```bash
docker exec lexicon-backup-local /scripts/backup.sh
```

### Restore from Backup
```bash
# List available backups
docker exec lexicon-backup-local ls -la /backups/

# Restore specific backup
docker exec lexicon-backup-local /scripts/restore.sh /backups/lexicon_backup_20240125_020000.tar.gz
```

### Backup Retention

- Daily: Last 7 days
- Weekly: Last 4 weeks  
- Monthly: Last 12 months

Configure in `docker-compose-local.yml`:
```yaml
environment:
  - BACKUP_RETENTION_DAYS=30
```

## Performance Optimization

### 1. Redis Configuration

Edit `redis-local.conf`:
```conf
# Memory limit
maxmemory 4gb
maxmemory-policy allkeys-lru

# Persistence tuning
save 900 1
save 300 10
save 60 10000
```

### 2. Nginx Caching

Enable in `nginx-local.conf`:
```nginx
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

### 3. ChromaDB Optimization

```yaml
environment:
  - CHROMA_SERVER_THREAD_POOL_SIZE=8
  - CHROMA_SERVER_GRPC_MAX_WORKERS=16
```

## Monitoring

### Basic Health Checks
```powershell
# Check all services
docker-compose -f docker-compose-local.yml ps

# View logs
docker-compose -f docker-compose-local.yml logs -f

# Check specific service
docker logs lexicon-webapp-local --tail 100
```

### Advanced Monitoring (Optional)

Deploy monitoring stack:
```powershell
.\deploy-local.ps1 -EnableMonitoring
```

Access:
- Grafana: http://localhost:3000
- Prometheus: http://localhost:9090

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```powershell
   # Find process using port 80
   netstat -ano | findstr :80
   
   # Kill process
   taskkill /PID <process_id> /F
   ```

2. **ChromaDB Connection Failed**
   ```bash
   # Restart ChromaDB
   docker-compose -f docker-compose-local.yml restart chromadb
   
   # Check logs
   docker logs lexicon-chromadb-local
   ```

3. **Out of Disk Space**
   ```bash
   # Clean up old backups
   docker exec lexicon-backup-local find /backups -name "*.tar.gz" -mtime +30 -delete
   
   # Prune Docker
   docker system prune -a
   ```

### Reset Everything
```powershell
# Stop all services
docker-compose -f docker-compose-local.yml down -v

# Remove all data (CAUTION!)
Remove-Item -Recurse -Force local-storage, backups, logs

# Redeploy
.\deploy-local.ps1
```

## Production Considerations

### 1. Domain Setup
- Configure DNS A record pointing to your server
- Update CORS_ORIGINS in .env
- Modify nginx-local.conf server_name

### 2. SSL/TLS
- Use proper SSL certificates (not self-signed)
- Enable HSTS in Nginx
- Configure SSL stapling

### 3. Backup Strategy
- Set up off-site backup replication
- Test restore procedures regularly
- Monitor backup job success

### 4. Security Hardening
- Change all default passwords
- Enable firewall rules
- Set up fail2ban for brute force protection
- Regular security updates

### 5. Scaling
- Add more Redis memory for larger deployments
- Consider ChromaDB clustering
- Use external PostgreSQL for metadata

## Support

For issues or questions:
1. Check logs: `docker-compose -f docker-compose-local.yml logs`
2. Review this documentation
3. Contact support with deployment logs

## License

This deployment configuration is part of the LEXICON system for Allen Law Group.