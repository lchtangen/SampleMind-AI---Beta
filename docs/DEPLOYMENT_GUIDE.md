# 🚀 SampleMind AI - Production Deployment Guide

**Version:** 1.0  
**Last Updated:** October 6, 2025  
**Status:** Production Ready

---

## 📋 Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Infrastructure Setup](#infrastructure-setup)
- [Environment Configuration](#environment-configuration)
- [Docker Deployment](#docker-deployment)
- [Kubernetes Deployment](#kubernetes-deployment)
- [Database Initialization](#database-initialization)
- [SSL/TLS Certificate Setup](#ssltls-certificate-setup)
- [Monitoring Stack Deployment](#monitoring-stack-deployment)
- [Post-Deployment Verification](#post-deployment-verification)
- [Rollback Procedures](#rollback-procedures)
- [Troubleshooting](#troubleshooting)
- [Security Checklist](#security-checklist)

---

## 🎯 Overview

This guide provides comprehensive instructions for deploying SampleMind AI to production environments. The platform supports both Docker Compose (single-server) and Kubernetes (multi-server) deployments.

### Deployment Architecture

```
┌─────────────────────────────────────────────────┐
│               Load Balancer / Ingress            │
│            (HTTPS, Rate Limiting, WAF)           │
└────────────────────┬────────────────────────────┘
                     │
         ┌───────────┼───────────┐
         │           │           │
    ┌────▼────┐ ┌───▼────┐ ┌───▼────┐
    │ Frontend│ │Backend │ │Backend │ (Auto-scaled 3-10)
    │  (2-5)  │ │  API   │ │  API   │
    └─────────┘ └───┬────┘ └───┬────┘
                    │           │
         ┌──────────┼───────────┴──────┐
         │          │                   │
    ┌────▼────┐ ┌──▼──────┐ ┌────────▼─────┐
    │ MongoDB │ │  Redis  │ │   ChromaDB   │
    │ (Replica│ │ (Cache) │ │   (Vector)   │
    │   Set)  │ └─────────┘ └──────────────┘
    └────┬────┘
         │
    ┌────▼──────────────┐
    │  Celery Workers   │
    │  (2-5, Auto-scale)│
    └───────────────────┘
```

### Supported Platforms

- **Cloud Providers:** AWS, GCP, Azure, DigitalOcean
- **Container Orchestration:** Kubernetes 1.25+, Docker Swarm
- **Operating Systems:** Ubuntu 22.04+, Debian 11+, RHEL 8+

---

## ✅ Prerequisites

### Required Infrastructure

#### Minimum (Small-Scale Production)
- **Compute:**
  - 4 vCPUs
  - 16GB RAM
  - 100GB SSD storage
- **Network:**
  - Public IP address
  - Domain name configured
  - SSL certificate (Let's Encrypt)

#### Recommended (Production)
- **Compute:**
  - 3+ nodes (Kubernetes)
  - 8 vCPUs per node
  - 32GB RAM per node
  - 200GB SSD storage per node
- **Network:**
  - Load balancer
  - CDN for static assets
  - WAF (Web Application Firewall)

#### Enterprise
- **Compute:**
  - 5+ nodes
  - 16+ vCPUs per node
  - 64GB+ RAM per node
  - 500GB+ SSD storage
- **High Availability:**
  - Multi-region deployment
  - Auto-scaling groups
  - Disaster recovery setup

### Required Tools

```bash
# Verify installations
docker --version          # 24.0+
docker-compose --version  # 2.20+
kubectl version --client  # 1.25+
helm version             # 3.12+
```

### Required Credentials

Prepare the following:

1. **Database Credentials:**
   - MongoDB connection string
   - Redis password
   - ChromaDB API key (if using hosted)

2. **AI Service API Keys:**
   - Google AI API key
   - OpenAI API key
   - Anthropic API key (optional)

3. **Infrastructure Credentials:**
   - Cloud provider credentials (AWS/GCP/Azure)
   - Container registry credentials
   - DNS provider API token

4. **Monitoring & Alerting:**
   - Slack webhook URL
   - PagerDuty integration key
   - SMTP credentials

---

## 🏗️ Infrastructure Setup

### Cloud Provider Setup

#### AWS

```bash
# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Configure credentials
aws configure

# Create EKS cluster
eksctl create cluster \
  --name samplemind-prod \
  --region us-east-1 \
  --nodegroup-name standard-workers \
  --node-type t3.xlarge \
  --nodes 3 \
  --nodes-min 3 \
  --nodes-max 10 \
  --managed
```

#### GCP

```bash
# Install gcloud CLI
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
gcloud init

# Create GKE cluster
gcloud container clusters create samplemind-prod \
  --num-nodes=3 \
  --machine-type=n1-standard-4 \
  --enable-autoscaling \
  --min-nodes=3 \
  --max-nodes=10 \
  --zone=us-central1-a
```

#### Azure

```bash
# Install Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Login
az login

# Create AKS cluster
az aks create \
  --resource-group samplemind-rg \
  --name samplemind-prod \
  --node-count 3 \
  --enable-addons monitoring \
  --generate-ssh-keys
```

### Storage Configuration

#### Block Storage (Databases)

```bash
# AWS EBS
aws ec2 create-volume \
  --size 200 \
  --availability-zone us-east-1a \
  --volume-type gp3 \
  --iops 3000

# GCP Persistent Disk
gcloud compute disks create samplemind-db-disk \
  --size=200GB \
  --type=pd-ssd

# Azure Disk
az disk create \
  --resource-group samplemind-rg \
  --name samplemind-db-disk \
  --size-gb 200 \
  --sku Premium_LRS
```

#### Object Storage (Files, Backups)

```bash
# AWS S3
aws s3 mb s3://samplemind-prod-files

# GCP Cloud Storage
gsutil mb gs://samplemind-prod-files

# Azure Blob Storage
az storage container create \
  --name samplemind-prod-files \
  --account-name samplemindprod
```

### Network Configuration

#### DNS Setup

```bash
# Point domain to load balancer
# A Record: samplemind.ai → [LOAD_BALANCER_IP]
# A Record: api.samplemind.ai → [LOAD_BALANCER_IP]
# CNAME: www.samplemind.ai → samplemind.ai
```

#### Firewall Rules

```bash
# Allow HTTPS (443)
# Allow HTTP (80) - redirect to HTTPS
# Allow SSH (22) - restricted to admin IPs
# Allow internal cluster communication

# Example: AWS Security Group
aws ec2 authorize-security-group-ingress \
  --group-id sg-xxxxx \
  --protocol tcp \
  --port 443 \
  --cidr 0.0.0.0/0
```

---

## ⚙️ Environment Configuration

### 1. Create Environment Files

```bash
cd /path/to/samplemind-ai

# Development
cp .env.example .env.dev

# Staging
cp .env.example .env.staging

# Production
cp .env.example .env.production
```

### 2. Configure Production Environment

Edit `.env.production`:

```bash
# Application
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=info
SECRET_KEY=<generate-256-bit-key>

# API
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4
CORS_ORIGINS=https://samplemind.ai,https://www.samplemind.ai

# Database
MONGODB_URL=mongodb://samplemind:password@mongodb-primary:27017,mongodb-secondary:27017/samplemind?replicaSet=rs0&authSource=admin
MONGODB_MAX_POOL_SIZE=50
MONGODB_MIN_POOL_SIZE=10

# Redis
REDIS_URL=redis://:password@redis-master:6379/0
REDIS_MAX_CONNECTIONS=50

# Vector Database
CHROMADB_HOST=chromadb
CHROMADB_PORT=8000
CHROMADB_API_KEY=<your-api-key>

# AI Services
GOOGLE_AI_API_KEY=<your-google-api-key>
OPENAI_API_KEY=<your-openai-api-key>
ANTHROPIC_API_KEY=<your-anthropic-api-key>

# Authentication
JWT_SECRET=<generate-secure-secret>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=30

# Celery
CELERY_BROKER_URL=redis://:password@redis-master:6379/1
CELERY_RESULT_BACKEND=redis://:password@redis-master:6379/2
CELERY_WORKER_CONCURRENCY=4

# Monitoring
PROMETHEUS_ENABLED=true
SENTRY_DSN=<your-sentry-dsn>

# Storage
UPLOAD_DIR=/app/data/uploads
MAX_UPLOAD_SIZE=104857600  # 100MB

# Feature Flags
ENABLE_VECTOR_SEARCH=true
ENABLE_AI_ANALYSIS=true
ENABLE_BATCH_PROCESSING=true
```

### 3. Generate Secure Secrets

```bash
# Generate SECRET_KEY (256-bit)
openssl rand -hex 32

# Generate JWT_SECRET
openssl rand -hex 32

# Generate MongoDB password
openssl rand -base64 32

# Generate Redis password
openssl rand -base64 32
```

---

## 🐳 Docker Deployment

### Single-Server Deployment

Best for: Small to medium production workloads (< 10K users)

#### 1. Prepare Server

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### 2. Deploy Application

```bash
cd /path/to/samplemind-ai/deployment/docker

# Copy production environment
cp .env.example .env
# Edit .env with production values

# Build images
docker-compose -f docker-compose.prod.yml build

# Start services
docker-compose -f docker-compose.prod.yml up -d

# Verify
docker-compose -f docker-compose.prod.yml ps
```

#### 3. Configure Nginx Reverse Proxy

```bash
# Install Nginx
sudo apt install nginx

# Create configuration
sudo nano /etc/nginx/sites-available/samplemind
```

Nginx configuration:

```nginx
upstream backend {
    least_conn;
    server localhost:8000;
}

server {
    listen 80;
    server_name samplemind.ai www.samplemind.ai;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name samplemind.ai www.samplemind.ai;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/samplemind.ai/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/samplemind.ai/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # API Proxy
    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # Rate Limiting
        limit_req zone=api_limit burst=20 nodelay;
    }

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Health Check
    location /health {
        proxy_pass http://backend/health;
        access_log off;
    }
}

# Rate Limiting
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
```

#### 4. Enable and Test

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/samplemind /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx

# Verify
curl https://samplemind.ai/api/v1/health
```

### Docker Swarm Deployment

For multi-server Docker deployments:

```bash
# Initialize Swarm (on manager node)
docker swarm init

# Add worker nodes
docker swarm join --token <token> <manager-ip>:2377

# Deploy stack
docker stack deploy -c docker-compose.prod.yml samplemind

# Check services
docker stack services samplemind
```

---

## ☸️ Kubernetes Deployment

### Full Production Deployment

Best for: Large-scale production (10K+ users), high availability

#### 1. Prerequisites Installation

```bash
# Metrics Server (required for HPA)
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# Ingress Controller (NGINX)
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace \
  --set controller.service.type=LoadBalancer

# Cert-Manager (SSL certificates)
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Prometheus Operator (monitoring)
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install kube-prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace
```

#### 2. Prepare Kubernetes Manifests

```bash
cd /path/to/samplemind-ai/deployment/kubernetes

# Configure secrets
cp secrets.yaml secrets-actual.yaml
# Edit secrets-actual.yaml with production values
```

**IMPORTANT:** Never commit `secrets-actual.yaml` to version control!

#### 3. Deploy Application

```bash
# Create namespace and resources
kubectl apply -f namespace.yaml

# Apply secrets
kubectl apply -f secrets-actual.yaml

# Deploy configuration
kubectl apply -f configmap.yaml

# Deploy storage
kubectl apply -f pvc.yaml

# Deploy RBAC
kubectl apply -f serviceaccount.yaml

# Deploy database statefulsets (if not using managed services)
# kubectl apply -f mongodb-statefulset.yaml
# kubectl apply -f redis-statefulset.yaml

# Deploy application
kubectl apply -f backend-deployment.yaml
kubectl apply -f celery-deployment.yaml
kubectl apply -f frontend-deployment.yaml

# Create services
kubectl apply -f service.yaml

# Configure ingress
kubectl apply -f ingress.yaml

# Enable auto-scaling
kubectl apply -f hpa.yaml

# Apply network policies
kubectl apply -f networkpolicy.yaml

# Deploy monitoring
kubectl apply -f monitoring.yaml
```

#### 4. Verify Deployment

```bash
# Check all resources
kubectl get all -n samplemind-production

# Check pod status
kubectl get pods -n samplemind-production

# Check services
kubectl get svc -n samplemind-production

# Check ingress
kubectl get ingress -n samplemind-production

# Check HPA
kubectl get hpa -n samplemind-production

# Check logs
kubectl logs -n samplemind-production deployment/backend
```

#### 5. Alternative: Deploy with Kustomize

```bash
# Deploy everything at once
kubectl apply -k deployment/kubernetes/

# Verify
kubectl get all -n samplemind-production
```

---

## 🗄️ Database Initialization

### MongoDB Setup

#### Option 1: Managed Service (Recommended)

```bash
# AWS DocumentDB
# GCP Cloud Firestore
# Azure Cosmos DB
# MongoDB Atlas

# Get connection string from provider
# Update MONGODB_URL in .env
```

#### Option 2: Self-Hosted

```bash
# Deploy MongoDB ReplicaSet
kubectl apply -f deployment/kubernetes/mongodb-statefulset.yaml

# Initialize replica set
kubectl exec -it mongodb-0 -n samplemind-production -- mongosh

# In MongoDB shell:
rs.initiate({
  _id: "rs0",
  members: [
    { _id: 0, host: "mongodb-0.mongodb-service:27017" },
    { _id: 1, host: "mongodb-1.mongodb-service:27017" },
    { _id: 2, host: "mongodb-2.mongodb-service:27017" }
  ]
})

# Create admin user
use admin
db.createUser({
  user: "admin",
  pwd: "your-secure-password",
  roles: ["root"]
})

# Create application database and user
use samplemind
db.createUser({
  user: "samplemind",
  pwd: "your-app-password",
  roles: [
    { role: "readWrite", db: "samplemind" }
  ]
})
```

### Create Indexes

```bash
# Apply indexes for performance
kubectl exec -it mongodb-0 -n samplemind-production -- mongosh -u samplemind -p password samplemind

# In MongoDB shell:
use samplemind

# Audio files collection
db.audio_files.createIndex({ "user_id": 1, "created_at": -1 })
db.audio_files.createIndex({ "status": 1 })
db.audio_files.createIndex({ "file_hash": 1 }, { unique: true })

# Analysis results collection
db.analysis_results.createIndex({ "file_id": 1, "analysis_type": 1 })
db.analysis_results.createIndex({ "created_at": -1 })

# Users collection
db.users.createIndex({ "email": 1 }, { unique: true })
db.users.createIndex({ "created_at": -1 })

# API keys collection
db.api_keys.createIndex({ "key_hash": 1 }, { unique: true })
db.api_keys.createIndex({ "user_id": 1 })
db.api_keys.createIndex({ "expires_at": 1 })

# Verify indexes
db.audio_files.getIndexes()
```

### Redis Setup

```bash
# For managed service:
# - AWS ElastiCache
# - GCP Memorystore
# - Azure Cache for Redis

# For self-hosted:
kubectl apply -f deployment/kubernetes/redis-statefulset.yaml

# Configure Redis
kubectl exec -it redis-0 -n samplemind-production -- redis-cli
AUTH your-redis-password
CONFIG SET maxmemory 2gb
CONFIG SET maxmemory-policy allkeys-lru
CONFIG REWRITE
```

### Database Migrations

```bash
# Run migrations (if applicable)
kubectl exec -it deployment/backend -n samplemind-production -- \
  python -m alembic upgrade head

# Or for Django-style migrations:
kubectl exec -it deployment/backend -n samplemind-production -- \
  python manage.py migrate
```

---

## 🔒 SSL/TLS Certificate Setup

### Option 1: Let's Encrypt (Automatic)

```bash
# Cert-manager with Let's Encrypt
cat <<EOF | kubectl apply -f -
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@samplemind.ai
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF

# Certificate is automatically created by ingress
kubectl get certificate -n samplemind-production
```

### Option 2: Manual Certificate

```bash
# Obtain certificate (e.g., from CloudFlare, DigiCert)
# Create secret with certificate
kubectl create secret tls samplemind-tls \
  --cert=path/to/cert.pem \
  --key=path/to/key.pem \
  -n samplemind-production
```

### Verify SSL

```bash
# Check certificate
kubectl describe certificate samplemind-tls -n samplemind-production

# Test HTTPS
curl -v https://samplemind.ai/health

# Check SSL rating
# Visit: https://www.ssllabs.com/ssltest/analyze.html?d=samplemind.ai
```

---

## 📊 Monitoring Stack Deployment

### Deploy Monitoring with Docker

```bash
cd monitoring
docker-compose -f docker-compose.monitoring.yml up -d

# Verify services
docker-compose -f docker-compose.monitoring.yml ps
```

### Deploy Monitoring on Kubernetes

```bash
# Monitoring already deployed with Prometheus Operator
# Access Grafana
kubectl port-forward -n monitoring svc/kube-prometheus-stack-grafana 3000:80

# Login to Grafana (admin/prom-operator)
# Import dashboards from monitoring/grafana/dashboards/

# Configure AlertManager
kubectl edit alertmanager -n monitoring
```

### Configure Alerts

```bash
# Update AlertManager configuration
kubectl create configmap alertmanager-config \
  --from-file=monitoring/alertmanager/alertmanager.yml \
  -n monitoring \
  --dry-run=client -o yaml | kubectl apply -f -

# Test alert
kubectl apply -f - <<EOF
apiVersion: v1
kind: Pod
metadata:
  name: test-alert
  namespace: samplemind-production
spec:
  containers:
  - name: stress
    image: containerstack/alpine-stress
    command: ["stress", "--cpu", "10"]
EOF
```

---

## ✅ Post-Deployment Verification

### 1. Health Checks

```bash
# API health
curl https://samplemind.ai/api/v1/health

# Expected response:
# {"status":"healthy","version":"0.6.0","timestamp":"..."}

# Database connectivity
curl https://samplemind.ai/api/v1/health/db

# Redis connectivity
curl https://samplemind.ai/api/v1/health/redis

# All services
curl https://samplemind.ai/api/v1/health/all
```

### 2. Functional Testing

```bash
# Test file upload
curl -X POST https://samplemind.ai/api/v1/audio/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@test-audio.wav"

# Test analysis
curl https://samplemind.ai/api/v1/audio/$FILE_ID/analyze \
  -H "Authorization: Bearer $TOKEN"

# Test search
curl "https://samplemind.ai/api/v1/audio/search?q=upbeat+drums" \
  -H "Authorization: Bearer $TOKEN"
```

### 3. Performance Testing

```bash
# Install Apache Bench
sudo apt install apache2-utils

# Load test
ab -n 1000 -c 10 https://samplemind.ai/api/v1/health

# Or use Locust
cd tests/load
locust -f locustfile.py --host=https://samplemind.ai
```

### 4. Security Verification

```bash
# SSL/TLS check
nmap --script ssl-enum-ciphers -p 443 samplemind.ai

# Security headers check
curl -I https://samplemind.ai

# Expected headers:
# - Strict-Transport-Security
# - X-Frame-Options
# - X-Content-Type-Options
# - X-XSS-Protection
```

### 5. Monitoring Verification

```bash
# Check Prometheus targets
curl https://prometheus.samplemind.ai/api/v1/targets

# Check Grafana dashboards
curl https://grafana.samplemind.ai/api/dashboards/

# Test alerts
# Trigger high CPU usage and verify alert fires
```

---

## 🔄 Rollback Procedures

### Docker Rollback

```bash
# Stop current version
docker-compose -f docker-compose.prod.yml down

# Restore previous version
docker-compose -f docker-compose.prod.yml up -d --scale backend=3 backend:previous-tag

# Or restore from backup
docker load < backup/samplemind-backend-v0.5.0.tar
docker-compose -f docker-compose.prod.yml up -d
```

### Kubernetes Rollback

```bash
# View rollout history
kubectl rollout history deployment/backend -n samplemind-production

# Rollback to previous version
kubectl rollout undo deployment/backend -n samplemind-production

# Rollback to specific revision
kubectl rollout undo deployment/backend --to-revision=3 -n samplemind-production

# Verify rollback
kubectl rollout status deployment/backend -n samplemind-production

# Check pods
kubectl get pods -n samplemind-production
```

### Database Rollback

```bash
# Restore MongoDB from backup
mongorestore --uri="$MONGODB_URL" \
  --drop \
  /path/to/backup/$(date -d yesterday +%Y-%m-%d)

# Restore Redis from backup
redis-cli -h redis-master --rdb /path/to/dump.rdb
```

---

## 🔧 Troubleshooting

### Common Deployment Issues

#### 1. Pods Not Starting

```bash
# Check pod status
kubectl describe pod <pod-name> -n samplemind-production

# Common causes:
# - Image pull errors
# - Resource limits
# - Config/Secret missing
# - Health checks failing

# Fix: Check logs
kubectl logs <pod-name> -n samplemind-production

# Fix: Increase resources
kubectl edit deployment backend -n samplemind-production
```

#### 2. Service Unavailable

```bash
# Check service endpoints
kubectl get endpoints -n samplemind-production

# Check if pods are ready
kubectl get pods -n samplemind-production

# Test internal connectivity
kubectl run test-pod --rm -it --image=busybox -n samplemind-production -- sh
wget -O- http://backend-service:8000/health
```

#### 3. SSL Certificate Issues

```bash
# Check certificate status
kubectl describe certificate -n samplemind-production

# Check cert-manager logs
kubectl logs -n cert-manager deployment/cert-manager

# Manual renewal
kubectl delete certificate samplemind-tls -n samplemind-production
kubectl apply -f deployment/kubernetes/ingress.yaml
```

#### 4. Database Connection Issues

```bash
# Test MongoDB connectivity
kubectl run mongodb-client --rm -it --image=mongo -n samplemind-production -- \
  mongosh "$MONGODB_URL"

# Test Redis connectivity
kubectl run redis-client --rm -it --image=redis -n samplemind-production -- \
  redis-cli -h redis-master -a password ping
```

#### 5. High Memory Usage

```bash
# Check memory usage
kubectl top pods -n samplemind-production

# Increase memory limits
kubectl set resources deployment backend \
  --limits=memory=4Gi \
  --requests=memory=2Gi \
  -n samplemind-production

# Or trigger garbage collection
kubectl exec -it deployment/backend -n samplemind-production -- \
  python -c "import gc; gc.collect()"
```

### Debug Mode

```bash
# Enable debug logging
kubectl set env deployment/backend DEBUG=true -n samplemind-production

# View logs
kubectl logs -f deployment/backend -n samplemind-production

# Disable debug after troubleshooting
kubectl set env deployment/backend DEBUG=false -n samplemind-production
```

### Emergency Procedures

```bash
# Scale down to single replica (maintenance mode)
kubectl scale deployment backend --replicas=1 -n samplemind-production

# Complete shutdown
kubectl scale deployment --all --replicas=0 -n samplemind-production

# Restore service
kubectl scale deployment backend --replicas=3 -n samplemind-production
```

---

## 🔐 Security Checklist

### Pre-Deployment Security

- [ ] All secrets generated with cryptographically secure methods
- [ ] Default passwords changed
- [ ] `.env` files not committed to git
- [ ] SSL/TLS certificates configured
- [ ] Firewall rules configured
- [ ] Network policies applied
- [ ] RBAC roles configured with least privilege
- [ ] Container images scanned for vulnerabilities
- [ ] Security headers configured in ingress

### Post-Deployment Security

- [ ] Change default admin credentials (Grafana, databases)
- [ ] Enable audit logging
- [ ] Configure fail2ban or similar
- [ ] Set up intrusion detection (if required)
- [ ] Enable WAF rules
- [ ] Configure DDoS protection
- [ ] Set up regular security scanning
- [ ] Configure automated backups
- [ ] Test disaster recovery procedures
- [ ] Document incident response procedures

### Ongoing Security

- [ ] Regular security updates (weekly)
- [ ] Credential rotation (monthly)
- [ ] Security audit (quarterly)
- [ ] Penetration testing (annually)
- [ ] Review access logs (daily)
- [ ] Monitor security alerts (real-time)
- [ ] Update dependencies (weekly)
- [ ] Backup verification (weekly)

---

## 📚 Related Documentation

- [`OPERATIONS_MANUAL.md`](OPERATIONS_MANUAL.md:1) - Day-to-day operations
- [`INCIDENT_RESPONSE.md`](INCIDENT_RESPONSE.md:1) - Incident response procedures
- [`ARCHITECTURE_DIAGRAMS.md`](ARCHITECTURE_DIAGRAMS.md:1) - System architecture
- [`deployment/kubernetes/README.md`](../deployment/kubernetes/README.md:1) - Kubernetes details
- [`deployment/docker/README.md`](../deployment/docker/README.md:1) - Docker details
- [`monitoring/README.md`](../monitoring/README.md:1) - Monitoring setup

---

## 🆘 Support

For deployment assistance:

- **Documentation:** https://docs.samplemind.ai
- **GitHub Issues:** https://github.com/lchtangen/SampleMind-AI---Beta/issues
- **Slack:** #deployment-support
- **Email:** devops@samplemind.ai

---

**Document Version:** 1.0  
**Last Updated:** October 6, 2025  
**Maintained by:** SampleMind AI DevOps Team