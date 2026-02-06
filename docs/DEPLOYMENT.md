# Low-Code Performance Scanner - Deployment Guide

This guide covers deployment options for the Low-Code Performance Scanner in various environments.

## Table of Contents

- [Deployment Options](#deployment-options)
- [Local Development](#local-development)
- [Docker Deployment](#docker-deployment)
- [Production Deployment](#production-deployment)
- [Cloud Deployment](#cloud-deployment)
- [Environment Configuration](#environment-configuration)
- [SSL/TLS Setup](#ssltls-setup)
- [Monitoring and Logging](#monitoring-and-logging)
- [Backup and Recovery](#backup-and-recovery)
- [Troubleshooting](#troubleshooting)

---

## Deployment Options

| Environment | Method | Best For |
|-------------|--------|----------|
| Development | Local Python | Development, testing |
| Staging | Docker Compose | Pre-production testing |
| Production | Docker + Nginx | Production workloads |
| Cloud | AWS/GCP/Azure | Scalable deployments |
| CI/CD | GitHub Actions | Automated testing |

---

## Local Development

### Prerequisites

- Python 3.8+
- Node.js 18+
- Git

### Backend Setup

```bash
# Clone repository
git clone https://github.com/your-org/lowcode-performance-scanner.git
cd lowcode-performance-scanner

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -e ".[dev]"

# Install Playwright browsers
playwright install chromium

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run backend
python backend/main.py
# Or with uvicorn
uvicorn backend.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/api/docs

---

## Docker Deployment

### Quick Start with Docker Compose

```bash
# Clone repository
git clone https://github.com/your-org/lowcode-performance-scanner.git
cd lowcode-performance-scanner

# Start production environment
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Services Included

| Service | Port | Description |
|---------|------|-------------|
| backend | 8000 | FastAPI server |
| frontend | 3000 | Next.js app |
| redis | 6379 | Session cache |
| nginx | 80/443 | Reverse proxy |

### Development Mode

```bash
# Start development services
docker-compose --profile dev up -d

# View backend logs
docker-compose logs -f backend-dev

# Execute commands in container
docker-compose exec backend-dev python -m pytest
```

### Production Mode

```bash
# Build production images
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

# Start production stack
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Docker Configuration

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  backend:
    restart: always
    environment:
      - ENVIRONMENT=production
      - LOG_LEVEL=warning
      - WORKERS=4
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G

  frontend:
    restart: always
    environment:
      - NODE_ENV=production
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 1G

  nginx:
    profiles:
      - production
    volumes:
      - ./nginx/nginx.prod.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - ./logs/nginx:/var/log/nginx
```

---

## Production Deployment

### System Requirements

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| CPU | 2 cores | 4+ cores |
| RAM | 4 GB | 8+ GB |
| Disk | 20 GB | 50+ GB SSD |
| Network | 100 Mbps | 1 Gbps |

### Server Setup (Ubuntu 22.04 LTS)

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
sudo apt install -y docker.io docker-compose
sudo systemctl enable docker
sudo usermod -aG docker $USER

# Install dependencies
sudo apt install -y git curl nginx

# Clone repository
git clone https://github.com/your-org/lowcode-performance-scanner.git /opt/scanner
cd /opt/scanner

# Create data directories
sudo mkdir -p /opt/scanner/{reports,logs,ssl}
sudo chown -R $USER:$USER /opt/scanner
```

### Nginx Configuration

Create `/opt/scanner/nginx/nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }

    upstream frontend {
        server frontend:3000;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/m;
    limit_req_zone $binary_remote_addr zone=ws:10m rate=60r/m;

    server {
        listen 80;
        server_name scanner.yourdomain.com;

        # Redirect to HTTPS
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name scanner.yourdomain.com;

        # SSL certificates
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;

        # Security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;

        # API endpoints
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_read_timeout 86400;
        }

        # WebSocket
        location /api/scans/ {
            limit_req zone=ws burst=100 nodelay;
            proxy_pass http://backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_read_timeout 86400;
        }

        # Frontend
        location / {
            proxy_pass http://frontend;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_cache_bypass $http_upgrade;
        }

        # Static files caching
        location /_next/static {
            proxy_pass http://frontend;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
}
```

### SSL/TLS Setup

#### Using Let's Encrypt

```bash
# Install certbot
sudo apt install -y certbot

# Obtain certificate
sudo certbot certonly --standalone -d scanner.yourdomain.com

# Copy certificates
sudo cp /etc/letsencrypt/live/scanner.yourdomain.com/fullchain.pem /opt/scanner/nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/scanner.yourdomain.com/privkey.pem /opt/scanner/ssl/key.pem

# Set up auto-renewal
sudo certbot renew --dry-run
```

#### Using Self-Signed (Development)

```bash
# Generate self-signed certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /opt/scanner/nginx/ssl/key.pem \
    -out /opt/scanner/nginx/ssl/cert.pem \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=scanner.yourdomain.com"
```

### Systemd Service

Create `/etc/systemd/system/scanner.service`:

```ini
[Unit]
Description=Low-Code Performance Scanner
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/scanner
ExecStart=/usr/bin/docker-compose up -d
ExecStop=/usr/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable scanner
sudo systemctl start scanner
sudo systemctl status scanner
```

---

## Cloud Deployment

### AWS Deployment

#### Using ECS (Elastic Container Service)

```bash
# Create ECS cluster
aws ecs create-cluster --cluster-name scanner-cluster

# Create task definition
aws ecs register-task-definition --cli-input-json file://ecs-task-definition.json

# Create service
aws ecs create-service \
    --cluster scanner-cluster \
    --service-name scanner-service \
    --task-definition scanner-task \
    --desired-count 2 \
    --launch-type FARGATE
```

#### ECS Task Definition

```json
{
    "family": "scanner-task",
    "networkMode": "awsvpc",
    "requiresCompatibilities": ["FARGATE"],
    "cpu": "2048",
    "memory": "4096",
    "containerDefinitions": [
        {
            "name": "backend",
            "image": "your-registry/scanner-backend:latest",
            "portMappings": [
                {
                    "containerPort": 8000,
                    "protocol": "tcp"
                }
            ],
            "environment": [
                {"name": "ENVIRONMENT", "value": "production"}
            ],
            "logConfiguration": {
                "logDriver": "awslogs",
                "options": {
                    "awslogs-group": "/ecs/scanner",
                    "awslogs-region": "us-east-1"
                }
            }
        }
    ]
}
```

### Google Cloud Platform

#### Using Cloud Run

```bash
# Build and push image
gcloud builds submit --tag gcr.io/your-project/scanner-backend

# Deploy to Cloud Run
gcloud run deploy scanner-backend \
    --image gcr.io/your-project/scanner-backend \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --memory 4Gi \
    --cpu 2 \
    --concurrency 10
```

### Azure Deployment

#### Using Container Instances

```bash
# Create resource group
az group create --name scanner-rg --location eastus

# Create container
az container create \
    --resource-group scanner-rg \
    --name scanner-backend \
    --image your-registry/scanner-backend:latest \
    --cpu 2 \
    --memory 4 \
    --ports 8000 \
    --ip-address Public
```

---

## Environment Configuration

### Production Environment Variables

Create `.env.production`:

```bash
# General
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=warning
SECRET_KEY=your-secure-secret-key-here

# Backend
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
BACKEND_WORKERS=4

# CORS (restrict in production)
CORS_ORIGINS=https://scanner.yourdomain.com

# Frontend
NEXT_PUBLIC_API_URL=https://scanner.yourdomain.com

# Scanner
MAX_CONCURRENT_SCANS=5
SCAN_TIMEOUT=300
DEFAULT_RUNS_PER_SCENARIO=3
OUTPUT_DIR=/app/reports

# Browser
HEADLESS=true
BROWSER_TYPE=chromium

# Redis (optional)
REDIS_URL=redis://redis:6379/0

# Monitoring
SENTRY_DSN=your-sentry-dsn
```

### Secrets Management

#### Using Docker Secrets

```bash
# Create secrets
echo "your-secret-key" | docker secret create scanner_secret_key -
echo "your-db-password" | docker secret create scanner_db_password -

# Use in docker-compose
version: '3.8'
secrets:
  secret_key:
    external: true
  
services:
  backend:
    secrets:
      - secret_key
    environment:
      - SECRET_KEY_FILE=/run/secrets/secret_key
```

#### Using AWS Secrets Manager

```python
import boto3
import json

def get_secret(secret_name):
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response['SecretString'])

secrets = get_secret('scanner/production')
SECRET_KEY = secrets['secret_key']
```

---

## SSL/TLS Setup

### Certificate Renewal (Let's Encrypt)

Create renewal script `/opt/scanner/scripts/renew-ssl.sh`:

```bash
#!/bin/bash

# Renew certificate
sudo certbot renew --quiet

# Copy new certificates
sudo cp /etc/letsencrypt/live/scanner.yourdomain.com/fullchain.pem /opt/scanner/nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/scanner.yourdomain.com/privkey.pem /opt/scanner/nginx/ssl/key.pem

# Reload nginx
sudo docker-compose exec nginx nginx -s reload
```

Add to crontab:

```bash
# Renew certificates weekly
0 2 * * 1 /opt/scanner/scripts/renew-ssl.sh >> /var/log/scanner-ssl-renewal.log 2>&1
```

---

## Monitoring and Logging

### Log Aggregation

#### Using Docker Logging Driver

```yaml
services:
  backend:
    logging:
      driver: "json-file"
      options:
        max-size: "100m"
        max-file: "3"
        labels: "service_name,environment"
```

#### Using Fluentd/Fluent Bit

```yaml
services:
  fluentd:
    image: fluent/fluentd
    volumes:
      - ./fluentd/conf:/fluentd/etc
    ports:
      - "24224:24224"

  backend:
    logging:
      driver: fluentd
      options:
        fluentd-address: localhost:24224
        tag: docker.scanner.backend
```

### Health Monitoring

#### Health Check Endpoint

```python
@app.get("/health")
async def health_check():
    checks = {
        "browser": await check_browser_health(),
        "disk": check_disk_space(),
        "memory": check_memory_usage()
    }
    
    healthy = all(c["status"] == "ok" for c in checks.values())
    
    return {
        "status": "healthy" if healthy else "unhealthy",
        "version": __version__,
        "checks": checks
    }
```

#### Prometheus Metrics (Future)

```python
from prometheus_client import Counter, Histogram, generate_latest

scan_counter = Counter('scans_total', 'Total scans', ['platform', 'status'])
scan_duration = Histogram('scan_duration_seconds', 'Scan duration')

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

### Alerting

#### Using Uptime Kuma

```bash
# Deploy Uptime Kuma
docker run -d \
    --name uptime-kuma \
    -p 3001:3001 \
    -v uptime-kuma:/app/data \
    louislam/uptime-kuma:1
```

Configure monitors for:
- API health endpoint
- Frontend availability
- SSL certificate expiration

---

## Backup and Recovery

### Database Backup

```bash
#!/bin/bash
# /opt/scanner/scripts/backup.sh

BACKUP_DIR="/opt/scanner/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Backup scan data
tar -czf "$BACKUP_DIR/scans_$DATE.tar.gz" /opt/scanner/reports

# Upload to S3 (optional)
aws s3 cp "$BACKUP_DIR/scans_$DATE.tar.gz" s3://scanner-backups/

# Keep only last 7 days
find $BACKUP_DIR -name "scans_*.tar.gz" -mtime +7 -delete
```

### Automated Backups

```bash
# Add to crontab
0 2 * * * /opt/scanner/scripts/backup.sh
```

### Recovery Procedure

```bash
# Stop services
docker-compose down

# Restore from backup
tar -xzf /opt/scanner/backups/scans_20260127_020000.tar.gz -C /

# Restart services
docker-compose up -d

# Verify
curl https://scanner.yourdomain.com/health
```

---

## Troubleshooting

### Common Issues

#### Container Won't Start

```bash
# Check logs
docker-compose logs backend

# Check resource usage
docker stats

# Verify configuration
docker-compose config
```

#### High Memory Usage

```bash
# Check memory limits
docker system df -v

# Prune unused images
docker system prune -a

# Adjust container limits in docker-compose.yml
```

#### SSL Certificate Errors

```bash
# Verify certificate
openssl x509 -in /opt/scanner/nginx/ssl/cert.pem -text -noout

# Check expiration date
echo | openssl s_client -servername scanner.yourdomain.com -connect scanner.yourdomain.com:443 2>/dev/null | openssl x509 -noout -dates
```

### Performance Tuning

#### Browser Pool Size

```python
# backend/main.py
MAX_CONCURRENT_SCANS = int(os.getenv("MAX_CONCURRENT_SCANS", 2))
```

#### Nginx Worker Processes

```nginx
# nginx/nginx.conf
worker_processes auto;
worker_connections 4096;
```

---

## Security Checklist

- [ ] Change default SECRET_KEY
- [ ] Enable HTTPS with valid certificate
- [ ] Restrict CORS origins
- [ ] Set up rate limiting
- [ ] Enable request logging
- [ ] Configure firewall rules
- [ ] Regular security updates
- [ ] Backup encryption
- [ ] Access controls for admin functions
- [ ] Audit logging enabled

---

## Support

For deployment support:
- GitHub Issues: [github.com/your-org/lowcode-performance-scanner/issues](https://github.com/your-org/lowcode-performance-scanner/issues)
- Documentation: [docs.lowcode-scanner.com](https://docs.lowcode-scanner.com)
- Email: support@lowcode-scanner.com
