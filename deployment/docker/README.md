# 🐳 SampleMind AI - Docker Deployment Guide

Complete guide for building and deploying SampleMind AI using Docker and Docker Compose.

## 📋 Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Building Images](#building-images)
- [Local Development](#local-development)
- [Production Deployment](#production-deployment)
- [Configuration](#configuration)
- [Monitoring](#monitoring)
- [Troubleshooting](#troubleshooting)
- [Security Best Practices](#security-best-practices)

---

## 🎯 Overview

This Docker setup includes:

- **Multi-stage builds** for optimized image sizes
- **Backend API** (FastAPI with Python 3.12)
- **Celery Workers** for async task processing
- **Frontend** (React with Vite)
- **MongoDB** for data storage
- **Redis** for caching and message broker
- **ChromaDB** for vector storage
- **Nginx** reverse proxy (production)
- **Prometheus & Grafana** for monitoring

### Image Size Targets

| Image | Target Size | Actual Size |
|-------|-------------|-------------|
| Backend | < 500MB | ~450MB |
| Frontend | < 100MB | ~85MB |
| Celery | < 500MB | ~450MB |

---

## 📦 Prerequisites

### Required Software

- **Docker** 24.0+ ([Install Docker](https://docs.docker.com/get-docker/))
- **Docker Compose** 2.20+ ([Install Compose](https://docs.docker.com/compose/install/))
- **Git** (for cloning repository)

### System Requirements

**Minimum:**
- 4 CPU cores
- 8GB RAM
- 20GB disk space

**Recommended:**
- 8+ CPU cores
- 16GB+ RAM
- 50GB+ SSD storage

### Verify Installation

```bash
docker --version
docker-compose --version
```

---

## 🚀 Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/lchtangen/SampleMind-AI---Beta.git
cd SampleMind-AI---Beta/deployment/docker
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit with your values
nano .env  # or vim, code, etc.
```

**Required Variables:**
- `SECRET_KEY` - Strong random key (min 32 chars)
- `MONGO_PASSWORD` - MongoDB password
- `REDIS_PASSWORD` - Redis password
- `GOOGLE_AI_API_KEY` - Google AI API key
- `OPENAI_API_KEY` - OpenAI API key

### 3. Start Services

**Development:**
```bash
docker-compose -f docker-compose.yml up -d
```

**Production:**
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### 4. Verify Services

```bash
# Check running containers
docker-compose ps

# Check logs
docker-compose logs -f

# Health check
curl http://localhost:8000/api/v1/health
```

---

## 🏗️ Building Images

### Build All Images

```bash
# Development images
docker-compose -f docker-compose.yml build

# Production images with optimizations
docker-compose -f docker-compose.prod.yml build --no-cache
```

### Build Individual Images

```bash
# Backend
docker build -f Dockerfile.backend -t samplemind/backend:latest ../../

# Frontend
docker build -f Dockerfile.frontend -t samplemind/frontend:latest ../../

# Celery
docker build -f Dockerfile.celery -t samplemind/celery:latest ../../
```

### Build with Custom Tags

```bash
# Tag with version
docker build -f Dockerfile.backend -t samplemind/backend:v0.6.0 ../../

# Tag with commit hash
docker build -f Dockerfile.backend -t samplemind/backend:$(git rev-parse --short HEAD) ../../
```

---

## 💻 Local Development

### Start Development Stack

```bash
cd deployment/docker
docker-compose -f docker-compose.yml up -d
```

### Available Services

| Service | URL | Description |
|---------|-----|-------------|
| Backend API | http://localhost:8000 | FastAPI backend |
| API Docs | http://localhost:8000/docs | Swagger UI |
| Frontend | http://localhost:3000 | React frontend |
| Flower | http://localhost:5555 | Celery monitoring |
| Prometheus | http://localhost:9090 | Metrics collection |
| Grafana | http://localhost:3001 | Dashboards |
| MongoDB | localhost:27017 | Database |
| Redis | localhost:6379 | Cache & broker |

### Hot Reload

Development setup includes:
- **Backend**: Auto-reload on code changes (volume mount)
- **Frontend**: Vite HMR (Hot Module Replacement)
- **Celery**: Auto-reload with watchdog

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f celery-worker

# Last 100 lines
docker-compose logs --tail=100 backend
```

### Execute Commands

```bash
# Backend shell
docker-compose exec backend bash

# Run Python commands
docker-compose exec backend python -c "print('Hello')"

# Database migrations (if applicable)
docker-compose exec backend python manage.py migrate

# Celery status
docker-compose exec celery-worker celery -A src.samplemind.core.tasks.celery_app status
```

### Stop Services

```bash
# Stop all
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Stop specific service
docker-compose stop backend
```

---

## 🚀 Production Deployment

### Pre-deployment Checklist

- [ ] Update `.env` with production values
- [ ] Change all default passwords
- [ ] Configure SSL certificates
- [ ] Set up domain DNS
- [ ] Review resource limits
- [ ] Configure backup strategy
- [ ] Set up monitoring alerts

### Deploy to Production

```bash
cd deployment/docker

# Build production images
docker-compose -f docker-compose.prod.yml build

# Start with detached mode
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose -f docker-compose.prod.yml ps
```

### SSL/TLS Configuration

1. **Obtain SSL Certificate:**
```bash
# Using Let's Encrypt (Certbot)
sudo certbot certonly --standalone -d api.samplemind.ai
```

2. **Copy Certificates:**
```bash
mkdir -p ./ssl
sudo cp /etc/letsencrypt/live/api.samplemind.ai/fullchain.pem ./ssl/cert.pem
sudo cp /etc/letsencrypt/live/api.samplemind.ai/privkey.pem ./ssl/key.pem
```

3. **Update nginx.conf** with SSL configuration

### Scale Services

```bash
# Scale workers
docker-compose -f docker-compose.prod.yml up -d --scale celery-worker=4

# Scale backend (requires load balancer)
docker-compose -f docker-compose.prod.yml up -d --scale backend=3
```

### Update Deployment

```bash
# Pull latest code
git pull origin main

# Rebuild images
docker-compose -f docker-compose.prod.yml build

# Rolling update (zero downtime)
docker-compose -f docker-compose.prod.yml up -d --no-deps --build backend

# Verify update
docker-compose -f docker-compose.prod.yml ps
```

---

## ⚙️ Configuration

### Environment Variables

See [`.env.example`](.env.example) for all available variables.

**Critical Settings:**

```bash
# Security
SECRET_KEY=your-256-bit-secret-key-here
CORS_ORIGINS=https://samplemind.ai

# Database
MONGODB_URL=mongodb://admin:password@mongodb:27017/samplemind?authSource=admin
REDIS_URL=redis://:password@redis:6379/0

# AI APIs
GOOGLE_AI_API_KEY=your-key-here
OPENAI_API_KEY=your-key-here
```

### Resource Limits

Edit `docker-compose.prod.yml` to adjust:

```yaml
deploy:
  resources:
    limits:
      cpus: '2.0'
      memory: 2G
    reservations:
      cpus: '0.5'
      memory: 512M
```

### Networking

Custom network configuration:

```yaml
networks:
  samplemind-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.28.0.0/16
```

---

## 📊 Monitoring

### Health Checks

```bash
# Backend health
curl http://localhost:8000/api/v1/health

# Check all services
docker-compose ps

# Detailed health status
docker inspect --format='{{.State.Health.Status}}' samplemind-backend
```

### Metrics & Dashboards

**Prometheus:**
- URL: http://localhost:9090
- Collects metrics from all services

**Grafana:**
- URL: http://localhost:3001
- Default credentials: admin/admin
- Pre-configured dashboards

**Flower (Celery):**
- URL: http://localhost:5555
- Monitor task queues and workers

### Log Management

```bash
# View logs by time
docker-compose logs --since 1h backend

# Follow logs with grep
docker-compose logs -f | grep ERROR

# Export logs
docker-compose logs --no-color > logs.txt
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. Port Already in Use

```bash
# Find process using port
sudo lsof -i :8000

# Kill process
sudo kill -9 <PID>

# Or change port in docker-compose.yml
ports:
  - "8001:8000"
```

#### 2. Permission Denied

```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Re-login or
newgrp docker
```

#### 3. Out of Memory

```bash
# Check Docker memory
docker stats

# Increase Docker memory limit
# Docker Desktop: Settings > Resources > Memory

# Or reduce service limits in docker-compose.prod.yml
```

#### 4. Image Build Fails

```bash
# Clean build cache
docker builder prune -a

# Rebuild with no cache
docker-compose build --no-cache

# Check disk space
df -h
```

#### 5. Service Won't Start

```bash
# Check logs
docker-compose logs backend

# Check dependencies
docker-compose ps

# Restart service
docker-compose restart backend

# Remove and recreate
docker-compose up -d --force-recreate backend
```

### Debug Mode

Enable debug logging:

```bash
# In .env
DEBUG=true
LOG_LEVEL=debug

# Restart services
docker-compose restart
```

### Database Issues

```bash
# MongoDB shell
docker-compose exec mongodb mongosh -u admin -p password

# Redis CLI
docker-compose exec redis redis-cli -a password

# Reset databases (WARNING: DATA LOSS)
docker-compose down -v
docker-compose up -d
```

---

## 🔒 Security Best Practices

### 1. Secrets Management

**❌ Don't:**
- Commit `.env` to git
- Use default passwords
- Store secrets in Dockerfiles

**✅ Do:**
- Use Docker secrets or external vault
- Rotate credentials regularly
- Use strong random passwords

### 2. Network Security

```yaml
# Use internal networks
networks:
  backend:
    internal: true
  frontend:
    internal: false
```

### 3. Image Security

```bash
# Scan images for vulnerabilities
docker scan samplemind/backend:latest

# Use specific versions (not :latest)
FROM python:3.12-slim

# Run as non-root user
USER samplemind
```

### 4. Resource Limits

Always set resource limits in production:

```yaml
deploy:
  resources:
    limits:
      cpus: '2.0'
      memory: 2G
```

### 5. Update Strategy

```bash
# Regular security updates
docker-compose pull
docker-compose up -d

# Monitor security advisories
# https://github.com/advisories
```

---

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)
- [SampleMind AI Documentation](../../docs/)
- [Production Best Practices](../../docs/DEPLOYMENT_GUIDE.md)

---

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/lchtangen/SampleMind-AI---Beta/issues)
- **Discussions**: [GitHub Discussions](https://github.com/lchtangen/SampleMind-AI---Beta/discussions)
- **Email**: team@samplemind.ai

---

## 📝 License

MIT License - See [LICENSE](../../LICENSE) for details.

---

**Last Updated**: 2025-10-06  
**Version**: 0.6.0-beta  
**Maintainer**: SampleMind AI Team