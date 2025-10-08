# 🛠️ SampleMind AI - Operations Manual

**Version:** 1.0  
**Last Updated:** October 6, 2025  
**For:** Production Operations Team

---

## 📋 Table of Contents

- [Overview](#overview)
- [Service Health Checks](#service-health-checks)
- [Performance Monitoring](#performance-monitoring)
- [Log Management](#log-management)
- [Backup and Restore](#backup-and-restore)
- [Scaling Operations](#scaling-operations)
- [Upgrade Procedures](#upgrade-procedures)
- [Maintenance Windows](#maintenance-windows)
- [Common Operational Tasks](#common-operational-tasks)
- [Service Restart Procedures](#service-restart-procedures)
- [Configuration Management](#configuration-management)
- [User Management](#user-management)
- [Database Operations](#database-operations)

---

## 🎯 Overview

This manual provides standard operating procedures for the day-to-day operation of SampleMind AI production systems. All operations should follow these documented procedures to ensure consistency and minimize risk.

### Team Responsibilities

| Team | Primary Responsibilities |
|------|--------------------------|
| **DevOps** | Infrastructure, deployments, monitoring |
| **SRE** | Reliability, performance, incident response |
| **Backend** | API issues, bug fixes, feature support |
| **ML Ops** | Model performance, inference optimization |
| **Database** | Data integrity, performance, backups |

### Communication Channels

- **Slack:** #prod-operations (primary)
- **PagerDuty:** Critical alerts only
- **Email:** ops@samplemind.ai (non-urgent)
- **Incident Channel:** #incident-response

---

## 🏥 Service Health Checks

### Daily Health Check Routine

Perform these checks every morning (09:00 UTC):

#### 1. API Health Status

```bash
# Quick health check
curl https://samplemind.ai/api/v1/health

# Expected response:
# {
#   "status": "healthy",
#   "version": "0.6.0",
#   "timestamp": "2025-10-06T09:00:00Z",
#   "components": {
#     "database": "healthy",
#     "redis": "healthy",
#     "celery": "healthy"
#   }
# }

# Detailed health check
curl https://samplemind.ai/api/v1/health/detailed
```

#### 2. Service Availability

**Docker:**
```bash
cd /path/to/deployment/docker
docker-compose -f docker-compose.prod.yml ps

# All services should show "Up" status
```

**Kubernetes:**
```bash
# Check all pods
kubectl get pods -n samplemind-production

# All pods should be "Running" with READY count matching

# Check deployments
kubectl get deployments -n samplemind-production

# Check HPA status
kubectl get hpa -n samplemind-production
```

#### 3. Database Connectivity

**MongoDB:**
```bash
# Docker
docker-compose exec mongodb mongosh -u admin -p password --eval "db.runCommand({ ping: 1 })"

# Kubernetes
kubectl exec -it mongodb-0 -n samplemind-production -- \
  mongosh -u admin -p password --eval "db.runCommand({ ping: 1 })"

# Check replica set status
kubectl exec -it mongodb-0 -n samplemind-production -- \
  mongosh -u admin -p password --eval "rs.status()"
```

**Redis:**
```bash
# Docker
docker-compose exec redis redis-cli -a password ping

# Kubernetes
kubectl exec -it redis-0 -n samplemind-production -- \
  redis-cli -a password ping

# Expected: PONG
```

#### 4. Queue Health

```bash
# Check Celery worker status
# Docker
docker-compose exec celery-worker celery -A src.samplemind.core.tasks.celery_app inspect active

# Kubernetes
kubectl exec -it deployment/celery-worker -n samplemind-production -- \
  celery -A src.samplemind.core.tasks.celery_app inspect stats

# Check queue depth
kubectl exec -it redis-0 -n samplemind-production -- \
  redis-cli -a password LLEN celery

# Queue depth should be < 100 under normal load
```

### Health Check Automation

Create a monitoring script (`scripts/health_check.sh`):

```bash
#!/bin/bash
# Daily health check script

SLACK_WEBHOOK="$SLACK_WEBHOOK_URL"
TIMESTAMP=$(date -u +"%Y-%m-%d %H:%M:%S UTC")

# Function to send Slack notification
notify_slack() {
    local message=$1
    local status=$2
    local color="${3:-#36a64f}"
    
    curl -X POST "$SLACK_WEBHOOK" \
        -H 'Content-Type: application/json' \
        -d "{
            \"attachments\": [{
                \"color\": \"$color\",
                \"title\": \"Health Check: $status\",
                \"text\": \"$message\",
                \"footer\": \"SampleMind Operations\",
                \"ts\": $(date +%s)
            }]
        }"
}

# Check API health
api_health=$(curl -s https://samplemind.ai/api/v1/health | jq -r .status)
if [ "$api_health" != "healthy" ]; then
    notify_slack "⚠️ API Health Check Failed" "CRITICAL" "#d9534f"
    exit 1
fi

# Check pod status (K8s)
unhealthy_pods=$(kubectl get pods -n samplemind-production --field-selector=status.phase!=Running --no-headers | wc -l)
if [ "$unhealthy_pods" -gt 0 ]; then
    notify_slack "⚠️ $unhealthy_pods pods not in Running state" "WARNING" "#f0ad4e"
fi

# Check queue depth
queue_depth=$(kubectl exec -it redis-0 -n samplemind-production -- redis-cli -a $REDIS_PASSWORD LLEN celery 2>/dev/null | tr -d '\r')
if [ "$queue_depth" -gt 1000 ]; then
    notify_slack "⚠️ High queue depth: $queue_depth tasks" "WARNING" "#f0ad4e"
fi

# All checks passed
notify_slack "✅ All health checks passed at $TIMESTAMP" "HEALTHY" "#36a64f"
```

Schedule with cron:
```bash
# Run daily at 09:00 UTC
0 9 * * * /path/to/scripts/health_check.sh
```

---

## 📊 Performance Monitoring

### Real-Time Monitoring

#### Access Grafana Dashboards

```bash
# Kubernetes port-forward
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80

# Open browser: http://localhost:3000
# Login: admin / prom-operator
```

**Key Dashboards:**
1. **System Overview** - Request rate, response times, errors
2. **Audio Processing** - Queue depth, processing times
3. **Database Performance** - Query times, connection pool
4. **ML Models** - Inference times, GPU usage

#### Monitor Metrics via CLI

```bash
# CPU usage
kubectl top nodes
kubectl top pods -n samplemind-production

# Memory usage
kubectl top pods -n samplemind-production --sort-by=memory

# Detailed pod metrics
kubectl describe pod <pod-name> -n samplemind-production
```

### Performance Baselines

Normal operating ranges:

| Metric | Normal Range | Warning | Critical |
|--------|--------------|---------|----------|
| API Response Time (p95) | < 300ms | > 500ms | > 1s |
| Error Rate | < 0.1% | > 0.5% | > 1% |
| CPU Usage | 30-60% | > 80% | > 95% |
| Memory Usage | 40-70% | > 80% | > 90% |
| Queue Depth | 0-100 | > 1000 | > 5000 |
| DB Connections | 10-30 | > 75 | > 95 |

### Performance Optimization Checks

**Weekly Performance Review (Friday 14:00 UTC):**

1. **Identify Slow Queries:**
```bash
# MongoDB slow queries
kubectl exec -it mongodb-0 -n samplemind-production -- \
  mongosh -u admin -p password --eval "db.system.profile.find({millis:{$gt:100}}).sort({ts:-1}).limit(10)"
```

2. **Check Cache Hit Rate:**
```bash
# Redis cache stats
kubectl exec -it redis-0 -n samplemind-production -- \
  redis-cli -a password INFO stats | grep keyspace_hits

# Target: > 70% hit rate
```

3. **Review Resource Utilization:**
```bash
# Generate resource report
kubectl top pods -n samplemind-production --sort-by=cpu > /tmp/resource_report.txt
kubectl top pods -n samplemind-production --sort-by=memory >> /tmp/resource_report.txt
```

---

## 📝 Log Management

### Accessing Logs

#### Docker Deployment

```bash
# View live logs
docker-compose -f docker-compose.prod.yml logs -f [service]

# View last 100 lines
docker-compose -f docker-compose.prod.yml logs --tail=100 backend

# Filter by time
docker-compose -f docker-compose.prod.yml logs --since 1h backend

# Search for errors
docker-compose -f docker-compose.prod.yml logs backend | grep ERROR

# Export logs
docker-compose -f docker-compose.prod.yml logs --no-color > logs.txt
```

#### Kubernetes Deployment

```bash
# View pod logs
kubectl logs -f deployment/backend -n samplemind-production

# View logs from all replicas
kubectl logs -f deployment/backend --all-containers=true -n samplemind-production

# View previous container logs (after crash)
kubectl logs deployment/backend --previous -n samplemind-production

# Filter logs
kubectl logs deployment/backend -n samplemind-production | grep ERROR

# Export logs
kubectl logs deployment/backend -n samplemind-production > backend-logs.txt
```

### Log Analysis

**Common Log Queries:**

```bash
# Count errors in last hour
kubectl logs deployment/backend -n samplemind-production --since=1h | grep ERROR | wc -l

# Find most common errors
kubectl logs deployment/backend -n samplemind-production --since=1h | \
  grep ERROR | sort | uniq -c | sort -rn | head -10

# Search for specific user issues
kubectl logs deployment/backend -n samplemind-production | grep "user_id: USER_ID"

# Track request IDs
kubectl logs deployment/backend -n samplemind-production | grep "request_id: REQ_ID"
```

### Log Rotation

**Docker (already configured in docker-compose.prod.yml):**
```yaml
logging:
  driver: "json-file"
  options:
    max-size: "100m"
    max-file: "5"
```

**Kubernetes (manual cleanup):**
```bash
# Clean old logs (older than 7 days)
kubectl get pods -n samplemind-production -o json | \
  jq -r '.items[].metadata.name' | \
  xargs -I {} kubectl logs {} -n samplemind-production --since=168h > /dev/null

# Or use log aggregation (recommended)
# - ELK Stack (Elasticsearch, Logstash, Kibana)
# - Loki (Grafana Loki)
# - CloudWatch Logs (AWS)
# - Stackdriver (GCP)
```

### Log Aggregation Setup

For production, implement centralized logging:

```bash
# Deploy Loki (Kubernetes)
helm repo add grafana https://grafana.github.io/helm-charts
helm install loki grafana/loki-stack \
  --namespace monitoring \
  --set grafana.enabled=false \
  --set promtail.enabled=true

# Query logs from Grafana
# Grafana > Explore > Loki data source
# Query: {namespace="samplemind-production", app="backend"}
```

---

## 💾 Backup and Restore

### Automated Backup Schedule

| Component | Frequency | Retention | Location |
|-----------|-----------|-----------|----------|
| MongoDB | Daily (02:00 UTC) | 30 days | S3/GCS |
| Redis | Daily (03:00 UTC) | 7 days | S3/GCS |
| Config/Secrets | Weekly | 90 days | S3/GCS |
| Application Logs | Daily | 30 days | S3/GCS |

### MongoDB Backup

#### Automated Backup Script

Create `scripts/backup_mongodb.sh`:

```bash
#!/bin/bash
set -e

BACKUP_DIR="/backups/mongodb"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="mongodb_backup_$TIMESTAMP"
MONGODB_URI="$MONGODB_URL"
S3_BUCKET="s3://samplemind-backups/mongodb"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Run mongodump
mongodump --uri="$MONGODB_URI" \
  --out="$BACKUP_DIR/$BACKUP_NAME" \
  --gzip

# Upload to S3
aws s3 sync "$BACKUP_DIR/$BACKUP_NAME" "$S3_BUCKET/$BACKUP_NAME/"

# Clean local backups older than 7 days
find "$BACKUP_DIR" -type d -mtime +7 -exec rm -rf {} \;

# Delete S3 backups older than 30 days
aws s3 ls "$S3_BUCKET/" | while read -r line; do
  createDate=$(echo $line | awk {'print $1" "$2'})
  createDate=$(date -d "$createDate" +%s)
  olderThan=$(date -d "30 days ago" +%s)
  if [[ $createDate -lt $olderThan ]]; then
    fileName=$(echo $line | awk {'print $4'})
    if [[ $fileName != "" ]]; then
      aws s3 rm "$S3_BUCKET/$fileName" --recursive
    fi
  fi
done

echo "Backup completed: $BACKUP_NAME"
```

Schedule with cron:
```bash
# Daily at 02:00 UTC
0 2 * * * /path/to/scripts/backup_mongodb.sh >> /var/log/mongodb_backup.log 2>&1
```

#### Manual Backup

```bash
# Kubernetes
kubectl exec -it mongodb-0 -n samplemind-production -- \
  mongodump --uri="$MONGODB_URL" \
  --out=/backup/manual_$(date +%Y%m%d) \
  --gzip

# Copy backup locally
kubectl cp samplemind-production/mongodb-0:/backup/manual_20251006 ./mongodb-backup

# Upload to cloud storage
aws s3 cp ./mongodb-backup s3://samplemind-backups/manual/ --recursive
```

#### Restore from Backup

```bash
# Download backup from S3
aws s3 cp s3://samplemind-backups/mongodb/mongodb_backup_20251006/ ./restore/ --recursive

# Restore to MongoDB
mongorestore --uri="$MONGODB_URL" \
  --dir=./restore \
  --gzip \
  --drop

# Verify restoration
mongosh "$MONGODB_URL" --eval "db.stats()"
```

### Redis Backup

#### Automated Backup

```bash
#!/bin/bash
# scripts/backup_redis.sh

BACKUP_DIR="/backups/redis"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
S3_BUCKET="s3://samplemind-backups/redis"

mkdir -p "$BACKUP_DIR"

# Trigger Redis BGSAVE
kubectl exec -it redis-0 -n samplemind-production -- \
  redis-cli -a "$REDIS_PASSWORD" BGSAVE

# Wait for save to complete
sleep 10

# Copy dump.rdb
kubectl cp samplemind-production/redis-0:/data/dump.rdb "$BACKUP_DIR/dump_$TIMESTAMP.rdb"

# Upload to S3
aws s3 cp "$BACKUP_DIR/dump_$TIMESTAMP.rdb" "$S3_BUCKET/"

# Clean old local backups
find "$BACKUP_DIR" -type f -mtime +7 -delete

echo "Redis backup completed: dump_$TIMESTAMP.rdb"
```

#### Restore Redis

```bash
# Download backup
aws s3 cp s3://samplemind-backups/redis/dump_20251006.rdb ./dump.rdb

# Stop Redis
kubectl scale statefulset redis --replicas=0 -n samplemind-production

# Copy dump.rdb to volume
kubectl cp ./dump.rdb samplemind-production/redis-0:/data/dump.rdb

# Start Redis
kubectl scale statefulset redis --replicas=1 -n samplemind-production

# Verify
kubectl exec -it redis-0 -n samplemind-production -- \
  redis-cli -a "$REDIS_PASSWORD" DBSIZE
```

### Configuration Backup

```bash
# Backup Kubernetes configs
kubectl get all,configmap,secret,pvc -n samplemind-production -o yaml > backup_k8s_config.yaml

# Backup to S3
aws s3 cp backup_k8s_config.yaml s3://samplemind-backups/configs/config_$(date +%Y%m%d).yaml
```

### Disaster Recovery Test

**Quarterly DR Test (First Monday of quarter):**

1. Restore to isolated test environment
2. Verify data integrity
3. Test application functionality
4. Document recovery time (RTO/RPO)
5. Update DR procedures if needed

```bash
# Test restore procedure
./scripts/test_disaster_recovery.sh
```

---

## ⚖️ Scaling Operations

### Manual Scaling

#### Docker Deployment

```bash
# Scale Celery workers
docker-compose -f docker-compose.prod.yml up -d --scale celery-worker=5

# Scale backend (requires load balancer)
docker-compose -f docker-compose.prod.yml up -d --scale backend=3
```

#### Kubernetes Deployment

```bash
# Scale backend
kubectl scale deployment backend --replicas=5 -n samplemind-production

# Scale Celery workers
kubectl scale deployment celery-worker --replicas=4 -n samplemind-production

# Verify scaling
kubectl get pods -n samplemind-production -w
```

### Auto-Scaling Configuration

**Current HPA Settings:**

```bash
# View HPA status
kubectl get hpa -n samplemind-production

# Backend: 3-10 pods, target 70% CPU, 80% memory
# Frontend: 2-5 pods, target 60% CPU, 70% memory
# Celery: 2-5 pods, target 80% CPU, 85% memory
```

**Adjust HPA Thresholds:**

```bash
# Edit HPA
kubectl edit hpa backend-hpa -n samplemind-production

# Example: Change target CPU to 60%
spec:
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 60  # Changed from 70
```

### Scaling Events

**When to Scale Up:**
- CPU > 80% for 5+ minutes
- Memory > 85% for 5+ minutes
- Queue depth > 1000 for 10+ minutes
- Response time p95 > 500ms consistently

**When to Scale Down:**
- CPU < 30% for 15+ minutes (off-peak)
- Memory < 40% for 15+ minutes
- Queue depth = 0 for 20+ minutes
- Outside peak hours (defined schedule)

### Pre-emptive Scaling

For known high-traffic events:

```bash
# Before event (scale up)
kubectl scale deployment backend --replicas=8 -n samplemind-production
kubectl scale deployment celery-worker --replicas=5 -n samplemind-production

# After event (scale down)
kubectl scale deployment backend --replicas=3 -n samplemind-production
kubectl scale deployment celery-worker --replicas=2 -n samplemind-production
```

---

## 🔄 Upgrade Procedures

### Application Upgrade

#### Pre-Upgrade Checklist

- [ ] Backup all databases
- [ ] Notify team in #prod-operations
- [ ] Check for breaking changes in CHANGELOG
- [ ] Test upgrade in staging
- [ ] Prepare rollback plan
- [ ] Schedule maintenance window (if needed)

#### Rolling Update (Zero-Downtime)

**Docker:**
```bash
# Pull new images
docker-compose -f docker-compose.prod.yml pull

# Rolling update
docker-compose -f docker-compose.prod.yml up -d --no-deps backend
docker-compose -f docker-compose.prod.yml up -d --no-deps celery-worker
docker-compose -f docker-compose.prod.yml up -d --no-deps frontend

# Verify
docker-compose -f docker-compose.prod.yml ps
```

**Kubernetes:**
```bash
# Update image tag
kubectl set image deployment/backend \
  backend=samplemind/backend:v0.7.0 \
  -n samplemind-production

# Watch rollout
kubectl rollout status deployment/backend -n samplemind-production

# Verify new version
kubectl get pods -n samplemind-production -o wide

# Check logs for errors
kubectl logs -f deployment/backend -n samplemind-production
```

#### Database Migrations

```bash
# Run migrations
kubectl exec -it deployment/backend -n samplemind-production -- \
  python -m alembic upgrade head

# Verify migration
kubectl exec -it deployment/backend -n samplemind-production -- \
  python -m alembic current
```

### Dependency Upgrades

**Monthly Dependency Review (First Tuesday):**

```bash
# Check for security updates
pip list --outdated

# Update dependencies
pip install --upgrade package-name

# Test in staging first
# Then update requirements.txt and redeploy
```

---

## 🕐 Maintenance Windows

### Scheduled Maintenance

**Regular Maintenance Windows:**
- **Weekly:** Sunday 02:00-04:00 UTC (low traffic)
- **Monthly:** First Sunday 02:00-06:00 UTC (major updates)
- **Emergency:** As needed (with 4-hour notice if possible)

### Maintenance Notification Template

Post to #prod-operations and status page:

```
🔧 SCHEDULED MAINTENANCE

**Date:** Sunday, October 15, 2025
**Time:** 02:00-04:00 UTC (convert to your timezone)
**Duration:** Up to 2 hours
**Impact:** No expected downtime (rolling updates)

**Changes:**
- Application upgrade to v0.7.0
- Database minor version upgrade
- Security patches

**Rollback Plan:** Automated rollback if issues detected

Questions? Contact: ops@samplemind.ai
```

### Maintenance Procedures

1. **Pre-Maintenance (T-24 hours):**
   - [ ] Post maintenance notification
   - [ ] Complete all backups
   - [ ] Verify staging upgrades
   - [ ] Prepare rollback scripts

2. **During Maintenance:**
   - [ ] Execute upgrade plan
   - [ ] Monitor metrics closely
   - [ ] Test critical functionality
   - [ ] Document any issues

3. **Post-Maintenance:**
   - [ ] Verify all services healthy
   - [ ] Check error rates
   - [ ] Monitor for 2 hours
   - [ ] Post completion message

---

## 🔧 Common Operational Tasks

### Restart a Service

**Backend Restart:**
```bash
# Kubernetes (rolling restart)
kubectl rollout restart deployment/backend -n samplemind-production

# Kubernetes (force restart single pod)
kubectl delete pod <pod-name> -n samplemind-production

# Docker
docker-compose -f docker-compose.prod.yml restart backend
```

### Clear Cache

```bash
# Clear Redis cache
kubectl exec -it redis-0 -n samplemind-production -- \
  redis-cli -a "$REDIS_PASSWORD" FLUSHDB

# Selective cache clear
kubectl exec -it redis-0 -n samplemind-production -- \
  redis-cli -a "$REDIS_PASSWORD" --scan --pattern "cache:*" | \
  xargs redis-cli -a "$REDIS_PASSWORD" DEL
```

### Purge Celery Queue

```bash
# Purge all tasks
kubectl exec -it deployment/celery-worker -n samplemind-production -- \
  celery -A src.samplemind.core.tasks.celery_app purge

# Confirm with: y
```

### Update Environment Variables

```bash
# Kubernetes
kubectl set env deployment/backend NEW_VAR=value -n samplemind-production

# Or edit ConfigMap
kubectl edit configmap samplemind-config -n samplemind-production

# Restart to apply changes
kubectl rollout restart deployment/backend -n samplemind-production
```

### Certificate Renewal

```bash
# Check certificate expiry
kubectl get certificate -n samplemind-production

# Force renewal (if needed)
kubectl delete certificate samplemind-tls -n samplemind-production

# Cert-manager will automatically renew
```

---

## 🔄 Service Restart Procedures

### Safe Restart Checklist

Before restarting any service:

1. **Check Dependencies:**
   - Will restart affect other services?
   - Are there active user sessions?
   - Are there running tasks/jobs?

2. **Notify:**
   - Post to #prod-operations
   - If high-impact, notify users

3. **Backup:**
   - Ensure recent backup exists
   - Document current state

4. **Execute:**
   - Use rolling restart if available
   - Monitor logs during restart
   - Verify health after restart

### Individual Service Restarts

**Backend API:**
```bash
# Zero-downtime rolling restart
kubectl rollout restart deployment/backend -n samplemind-production
kubectl rollout status deployment/backend -n samplemind-production

# Verify
curl https://samplemind.ai/api/v1/health
```

**Celery Workers:**
```bash
# Graceful shutdown (finish current tasks)
kubectl exec -it deployment/celery-worker -n samplemind-production -- \
  celery -A src.samplemind.core.tasks.celery_app control shutdown

# Or rolling restart
kubectl rollout restart deployment/celery-worker -n samplemind-production
```

**MongoDB:**
```bash
# Restart replica set members one at a time
# Start with secondaries, then primary

# Restart secondary
kubectl delete pod mongodb-1 -n samplemind-production
# Wait for it to become healthy

kubectl delete pod mongodb-2 -n samplemind-production
# Wait for it to become healthy

# Step down primary and restart
kubectl exec -it mongodb-0 -n samplemind-production -- \
  mongosh -u admin -p password --eval "rs.stepDown()"

kubectl delete pod mongodb-0 -n samplemind-production
```

**Redis:**
```bash
# Save data first
kubectl exec -it redis-0 -n samplemind-production -- \
  redis-cli -a "$REDIS_PASSWORD" BGSAVE

# Restart
kubectl delete pod redis-0 -n samplemind-production

# Verify
kubectl exec -it redis-0 -n samplemind-production -- \
  redis-cli -a "$REDIS_PASSWORD" ping
```

---

## ⚙️ Configuration Management

### Environment-Specific Configs

Maintain separate configs for each environment:

```
configs/
├── development.yaml
├── staging.yaml
└── production.yaml
```

### Update Configuration

**Kubernetes ConfigMap:**
```bash
# Edit ConfigMap
kubectl edit configmap samplemind-config -n samplemind-production

# Or update from file
kubectl create configmap samplemind-config \
  --from-file=configs/production.yaml \
  --dry-run=client -o yaml | kubectl apply -f -

# Restart pods to apply
kubectl rollout restart deployment/backend -n samplemind-production
```

**Docker .env file:**
```bash
# Edit .env file
nano /path/to/.env

# Restart services
docker-compose -f docker-compose.prod.yml up -d
```

### Feature Flags

Toggle features without deployment:

```bash
# Enable feature
kubectl set env deployment/backend ENABLE_NEW_FEATURE=true -n samplemind-production

# Disable feature
kubectl set env deployment/backend ENABLE_NEW_FEATURE=false -n samplemind-production

# No restart needed if application supports dynamic config reload
```

---

## 👥 User Management

### Create User Account

```bash
# Via API (admin token required)
curl -X POST https://samplemind.ai/api/v1/admin/users \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "name": "User Name",
    "role": "user"
  }'

# Or via database
kubectl exec -it mongodb-0 -n samplemind-production -- \
  mongosh -u admin -p password samplemind
  
# In MongoDB shell:
db.users.insertOne({
  email: "user@example.com",
  name: "User Name",
  role: "user",
  created_at: new Date()
})
```

### Reset User Password

```bash
# Generate password reset token
curl -X POST https://samplemind.ai/api/v1/auth/password-reset \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com"}'

# User receives reset email with token
```

### Disable User Account

```bash
# Via API
curl -X PATCH https://samplemind.ai/api/v1/admin/users/USER_ID \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "disabled"}'

# Or via database
kubectl exec -it mongodb-0 -n samplemind-production -- \
  mongosh -u admin -p password samplemind --eval \
  'db.users.updateOne({_id: ObjectId("USER_ID")}, {$set: {status: "disabled"}})'
```

### View User Activity

```bash
# Check recent API calls
kubectl logs deployment/backend -n samplemind-production | grep "user_id: USER_ID"

# Check user's files
kubectl exec -it mongodb-0 -n samplemind-production -- \
  mongosh -u admin -p password samplemind --eval \
  'db.audio_files.find({user_id: "USER_ID"}).count()'
```

---

## 🗄️ Database Operations

### MongoDB Maintenance

**Reindex Collection:**
```bash
kubectl exec -it mongodb-0 -n samplemind-production -- \
  mongosh -u admin -p password samplemind --eval \
  'db.audio_files.reIndex()'
```

**Compact Database:**
```bash
# Run during low-traffic period
kubectl exec -it mongodb-0 -n samplemind-production -- \
  mongosh -u admin -p password samplemind --eval \
  'db.runCommand({compact: "audio_files"})'
```

**Check Database Size:**
```bash
kubectl exec -it mongodb-0 -n samplemind-production -- \
  mongosh -u admin -p password samplemind --eval \
  'db.stats(1024*1024)' # Size in MB
```

### Redis Maintenance

**Monitor Memory Usage:**
```bash
kubectl exec -it redis-0 -n samplemind-production -- \
  redis-cli -a "$REDIS_PASSWORD" INFO memory
```

**Clear Expired Keys:**
```bash
# Redis auto-expires, but can force:
kubectl exec -it redis-0 -n samplemind-production -- \
  redis-cli -a "$REDIS_PASSWORD" --scan --pattern "cache:*" | \
  while read key; do
    ttl=$(redis-cli -a "$REDIS_PASSWORD" TTL "$key")
    if [ "$ttl" -lt 0 ]; then
      redis-cli -a "$REDIS_PASSWORD" DEL "$key"
    fi
  done
```

---

## 📞 On-Call Procedures

### On-Call Responsibilities

- Monitor #prod-operations Slack channel
- Respond to PagerDuty alerts within 5 minutes
- Escalate if unable to resolve within 30 minutes
- Document all incidents

### Handoff Checklist

When starting on-call shift:

- [ ] Review current system status
- [ ] Check recent alerts and incidents
- [ ] Verify access to all systems
- [ ] Review upcoming maintenance
- [ ] Update on-call schedule

### Emergency Contacts

| Role | Primary | Secondary |
|------|---------|-----------|
| DevOps Lead | +1-555-0101 | +1-555-0102 |
| Backend Lead | +1-555-0103 | +1-555-0104 |
| Database Admin | +1-555-0105 | +1-555-0106 |
| CTO | +1-555-0107 | - |

---

## 📚 Related Documentation

- [`DEPLOYMENT_GUIDE.md`](DEPLOYMENT_GUIDE.md:1) - Deployment procedures
- [`INCIDENT_RESPONSE.md`](INCIDENT_RESPONSE.md:1) - Incident response
- [`monitoring/README.md`](../monitoring/README.md:1) - Monitoring setup
- [`monitoring/ALERTING_GUIDE.md`](../monitoring/ALERTING_GUIDE.md:1) - Alert runbooks

---

## 📝 Change Log

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2025-10-06 | 1.0 | Initial release | DevOps Team |

---

**Document Owner:** DevOps Team  
**Review Schedule:** Monthly  
**Last Reviewed:** October 6, 2025