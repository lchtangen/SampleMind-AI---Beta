# SampleMind AI - Kubernetes Deployment Guide

Complete guide for deploying SampleMind AI to Kubernetes with auto-scaling, monitoring, and production-grade security.

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Deployment Steps](#deployment-steps)
- [Configuration](#configuration)
- [Auto-Scaling](#auto-scaling)
- [Monitoring](#monitoring)
- [Security](#security)
- [Troubleshooting](#troubleshooting)
- [Maintenance](#maintenance)

---

## 🔧 Prerequisites

### Required Tools

```bash
# Kubernetes CLI
kubectl version --client

# Kustomize (optional, built into kubectl)
kustomize version

# Helm (for dependencies)
helm version

# OpenSSL (for generating secrets)
openssl version
```

### Cluster Requirements

- **Kubernetes Version:** 1.25+
- **Nodes:** 3+ nodes (recommended)
- **Total Resources:**
  - CPU: 20+ cores
  - Memory: 40+ GB RAM
  - Storage: 200+ GB

### Required Add-ons

1. **Metrics Server** (for HPA):
   ```bash
   kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
   ```

2. **Ingress Controller** (NGINX):
   ```bash
   helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
   helm install ingress-nginx ingress-nginx/ingress-nginx \
     --namespace ingress-nginx --create-namespace
   ```

3. **Cert-Manager** (for TLS):
   ```bash
   kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml
   ```

4. **Prometheus Operator** (for monitoring):
   ```bash
   helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
   helm install kube-prometheus prometheus-community/kube-prometheus-stack \
     --namespace monitoring --create-namespace
   ```

---

## 🚀 Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/your-org/samplemind-ai.git
cd samplemind-ai/deployment/kubernetes
```

### 2. Configure Secrets

```bash
# Copy secrets template
cp secrets.yaml secrets-actual.yaml

# Generate strong passwords
export MONGODB_PASSWORD=$(openssl rand -base64 32)
export REDIS_PASSWORD=$(openssl rand -base64 32)
export JWT_SECRET=$(openssl rand -hex 32)

# Edit secrets-actual.yaml and replace CHANGE_ME placeholders
nano secrets-actual.yaml
```

### 3. Deploy to Kubernetes

```bash
# Create namespace
kubectl apply -f namespace.yaml

# Apply secrets (never commit secrets-actual.yaml!)
kubectl apply -f secrets-actual.yaml

# Deploy all resources
kubectl apply -f configmap.yaml
kubectl apply -f pvc.yaml
kubectl apply -f serviceaccount.yaml
kubectl apply -f backend-deployment.yaml
kubectl apply -f celery-deployment.yaml
kubectl apply -f frontend-deployment.yaml
kubectl apply -f service.yaml
kubectl apply -f ingress.yaml
kubectl apply -f hpa.yaml
kubectl apply -f networkpolicy.yaml
kubectl apply -f monitoring.yaml

# Or use kustomize
kubectl apply -k .
```

### 4. Verify Deployment

```bash
# Check pod status
kubectl get pods -n samplemind-production

# Check services
kubectl get svc -n samplemind-production

# Check ingress
kubectl get ingress -n samplemind-production

# Check HPA
kubectl get hpa -n samplemind-production
```

---

## 📝 Deployment Steps

### Step 1: Namespace & Resource Quotas

```bash
kubectl apply -f namespace.yaml
```

This creates:
- `samplemind-production` namespace
- Resource quotas (CPU, memory, storage limits)
- Limit ranges (default resource limits)

Verify:
```bash
kubectl describe namespace samplemind-production
kubectl get resourcequota -n samplemind-production
```

### Step 2: Secrets Configuration

**CRITICAL:** Never commit actual secrets to git!

```bash
# Create secrets from template
cp secrets.yaml secrets-actual.yaml

# Generate secure passwords
echo "MongoDB Password: $(openssl rand -base64 32)"
echo "Redis Password: $(openssl rand -base64 32)"
echo "JWT Secret: $(openssl rand -hex 32)"

# Edit and replace all CHANGE_ME values
vi secrets-actual.yaml

# Apply secrets
kubectl apply -f secrets-actual.yaml

# Verify (don't display values!)
kubectl get secrets -n samplemind-production

# Delete the file after applying
rm secrets-actual.yaml
```

### Step 3: Configuration

```bash
# Apply ConfigMaps
kubectl apply -f configmap.yaml

# Verify
kubectl get configmap -n samplemind-production
kubectl describe configmap samplemind-config -n samplemind-production
```

### Step 4: Storage

```bash
# Apply Persistent Volume Claims
kubectl apply -f pvc.yaml

# Verify PVCs
kubectl get pvc -n samplemind-production

# Check PV binding
kubectl get pv
```

**Storage Classes:**
- `fast-ssd`: High-performance SSD for databases
- `standard`: Standard storage for logs
- `standard-rwx`: ReadWriteMany for shared volumes

### Step 5: RBAC & Service Accounts

```bash
# Apply service accounts and RBAC
kubectl apply -f serviceaccount.yaml

# Verify
kubectl get serviceaccount -n samplemind-production
kubectl get role,rolebinding -n samplemind-production
```

### Step 6: Database & Cache Deployments

```bash
# Deploy MongoDB (if not using external)
# Deploy Redis (if not using external)
# Deploy ChromaDB

# Note: Consider using managed services in production:
# - AWS DocumentDB (MongoDB-compatible)
# - AWS ElastiCache (Redis)
# - Cloud storage for vector DB
```

### Step 7: Application Deployments

```bash
# Deploy backend
kubectl apply -f backend-deployment.yaml

# Deploy Celery workers
kubectl apply -f celery-deployment.yaml

# Deploy frontend
kubectl apply -f frontend-deployment.yaml

# Check deployments
kubectl get deployments -n samplemind-production
kubectl rollout status deployment/backend -n samplemind-production
```

### Step 8: Services

```bash
# Create services
kubectl apply -f service.yaml

# Verify services
kubectl get svc -n samplemind-production

# Test internal connectivity
kubectl run test-pod --rm -it --image=busybox -n samplemind-production -- sh
wget -O- http://backend-service:8000/health
```

### Step 9: Ingress & TLS

```bash
# Apply ingress
kubectl apply -f ingress.yaml

# Check ingress
kubectl get ingress -n samplemind-production
kubectl describe ingress samplemind-ingress -n samplemind-production

# Wait for TLS certificate
kubectl get certificate -n samplemind-production
kubectl describe certificate samplemind-tls -n samplemind-production
```

### Step 10: Auto-Scaling

```bash
# Apply HPA
kubectl apply -f hpa.yaml

# Verify HPA
kubectl get hpa -n samplemind-production

# Watch auto-scaling in action
kubectl get hpa -n samplemind-production --watch
```

### Step 11: Network Policies

```bash
# Apply network policies
kubectl apply -f networkpolicy.yaml

# Verify
kubectl get networkpolicy -n samplemind-production
kubectl describe networkpolicy backend-network-policy -n samplemind-production
```

### Step 12: Monitoring

```bash
# Apply monitoring configuration
kubectl apply -f monitoring.yaml

# Verify ServiceMonitors
kubectl get servicemonitor -n samplemind-production

# Check Prometheus targets
kubectl port-forward -n monitoring svc/prometheus-kube-prometheus-prometheus 9090:9090
# Open: http://localhost:9090/targets
```

---

## ⚙️ Configuration

### Environment Variables

Edit [`configmap.yaml`](configmap.yaml:1) to configure:
- Application settings
- Feature flags
- API endpoints
- Cache settings

### Secrets Management

**Production Best Practices:**

1. **External Secret Management:**
   ```bash
   # Use AWS Secrets Manager
   # Use HashiCorp Vault
   # Use Azure Key Vault
   # Use Google Secret Manager
   ```

2. **Sealed Secrets:**
   ```bash
   # Install sealed-secrets
   helm install sealed-secrets sealed-secrets/sealed-secrets -n kube-system
   
   # Seal a secret
   kubeseal -f secrets-actual.yaml -w sealed-secrets.yaml
   ```

3. **Secret Rotation:**
   - Rotate secrets every 90 days
   - Use automated rotation tools
   - Update secrets without downtime

### Resource Limits

Adjust in deployment files:

```yaml
resources:
  requests:
    memory: "512Mi"
    cpu: "500m"
  limits:
    memory: "2Gi"
    cpu: "2000m"
```

---

## 📈 Auto-Scaling

### Horizontal Pod Autoscaler (HPA)

**Backend Scaling:**
- Min: 3 pods
- Max: 10 pods
- Target CPU: 70%
- Target Memory: 80%

**Frontend Scaling:**
- Min: 2 pods
- Max: 5 pods
- Target CPU: 60%
- Target Memory: 70%

**Celery Scaling:**
- Min: 2 pods
- Max: 5 pods
- Target CPU: 80%
- Target Memory: 85%

### Monitor Scaling

```bash
# Watch HPA
kubectl get hpa -n samplemind-production --watch

# Check current metrics
kubectl top pods -n samplemind-production

# Describe HPA for details
kubectl describe hpa backend-hpa -n samplemind-production
```

### Test Auto-Scaling

```bash
# Generate load
kubectl run load-generator --rm -it --image=busybox -n samplemind-production -- sh
while true; do wget -q -O- http://backend-service:8000/health; done

# Watch scaling
kubectl get hpa -n samplemind-production --watch
```

---

## 📊 Monitoring

### Prometheus

Access Prometheus:
```bash
kubectl port-forward -n monitoring svc/prometheus-kube-prometheus-prometheus 9090:9090
```
Open: http://localhost:9090

### Grafana

Access Grafana:
```bash
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80
```
Open: http://localhost:3000
- Username: `admin`
- Password: `prom-operator`

### Key Metrics

**Application Metrics:**
- Request rate
- Error rate
- Response time (P50, P95, P99)
- Active connections

**Resource Metrics:**
- CPU usage
- Memory usage
- Disk I/O
- Network throughput

**Business Metrics:**
- Audio files processed
- AI analysis completion time
- User activity

### Alerts

Configure Alertmanager:
```bash
kubectl edit alertmanager -n monitoring
```

Alert channels:
- Slack
- PagerDuty
- Email
- Webhook

---

## 🔒 Security

### TLS/SSL

Certificates managed by cert-manager:
```bash
# Check certificate status
kubectl get certificate -n samplemind-production

# Describe certificate
kubectl describe certificate samplemind-tls -n samplemind-production

# Force renewal
kubectl delete secret samplemind-tls -n samplemind-production
```

### Network Policies

Network policies enforce:
- Pod-to-pod communication rules
- Ingress/egress restrictions
- Database access control

Test connectivity:
```bash
kubectl run test-pod --rm -it --image=busybox -n samplemind-production -- sh
wget -O- http://backend-service:8000/health
```

### RBAC

Service accounts with minimal permissions:
- `samplemind-backend`: Backend API
- `samplemind-celery`: Celery workers
- `samplemind-frontend`: Frontend app
- `samplemind-monitoring`: Metrics collection

### Security Scanning

```bash
# Scan images
trivy image samplemind/backend:latest

# Check pod security
kubectl auth can-i --list -n samplemind-production
```

---

## 🔧 Troubleshooting

### Pod Issues

```bash
# Check pod status
kubectl get pods -n samplemind-production

# Describe pod
kubectl describe pod <pod-name> -n samplemind-production

# Check logs
kubectl logs <pod-name> -n samplemind-production

# Follow logs
kubectl logs -f <pod-name> -n samplemind-production

# Previous container logs
kubectl logs <pod-name> --previous -n samplemind-production

# Execute commands in pod
kubectl exec -it <pod-name> -n samplemind-production -- bash
```

### Service Issues

```bash
# Check services
kubectl get svc -n samplemind-production

# Test service connectivity
kubectl run test-pod --rm -it --image=busybox -n samplemind-production -- sh
wget -O- http://backend-service:8000/health

# Check endpoints
kubectl get endpoints -n samplemind-production
```

### Ingress Issues

```bash
# Check ingress
kubectl describe ingress samplemind-ingress -n samplemind-production

# Check ingress controller logs
kubectl logs -n ingress-nginx -l app.kubernetes.io/component=controller

# Test external access
curl -v https://samplemind.ai/health
```

### Storage Issues

```bash
# Check PVC status
kubectl get pvc -n samplemind-production

# Describe PVC
kubectl describe pvc mongodb-data-pvc -n samplemind-production

# Check PV
kubectl get pv

# Check storage class
kubectl get storageclass
```

### HPA Issues

```bash
# Check HPA status
kubectl get hpa -n samplemind-production

# Describe HPA
kubectl describe hpa backend-hpa -n samplemind-production

# Check metrics server
kubectl top pods -n samplemind-production
kubectl top nodes
```

### Network Policy Issues

```bash
# Test connectivity
kubectl run test-pod --rm -it --image=busybox -n samplemind-production -- sh
wget -O- http://backend-service:8000/health

# Check network policies
kubectl describe networkpolicy -n samplemind-production
```

---

## 🔄 Maintenance

### Update Deployments

```bash
# Update image
kubectl set image deployment/backend backend=samplemind/backend:v2.0 -n samplemind-production

# Or edit deployment
kubectl edit deployment backend -n samplemind-production

# Check rollout status
kubectl rollout status deployment/backend -n samplemind-production

# View rollout history
kubectl rollout history deployment/backend -n samplemind-production
```

### Rollback

```bash
# Rollback to previous version
kubectl rollout undo deployment/backend -n samplemind-production

# Rollback to specific revision
kubectl rollout undo deployment/backend --to-revision=2 -n samplemind-production
```

### Scaling

```bash
# Manual scaling
kubectl scale deployment backend --replicas=5 -n samplemind-production

# Auto-scaling is handled by HPA
```

### Backup & Restore

```bash
# Backup using Velero
velero backup create samplemind-backup --include-namespaces samplemind-production

# Restore from backup
velero restore create --from-backup samplemind-backup
```

### Database Maintenance

```bash
# MongoDB backup
kubectl exec -it mongodb-0 -n samplemind-production -- mongodump --out=/backup

# Redis backup
kubectl exec -it redis-0 -n samplemind-production -- redis-cli BGSAVE
```

---

## 📚 Additional Resources

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [NGINX Ingress Controller](https://kubernetes.github.io/ingress-nginx/)
- [Cert-Manager Documentation](https://cert-manager.io/docs/)
- [Helm Charts](https://helm.sh/docs/)

---

## 🆘 Support

For issues or questions:
- GitHub Issues: https://github.com/your-org/samplemind-ai/issues
- Documentation: https://docs.samplemind.ai
- Slack: #samplemind-support

---

**Last Updated:** January 2025  
**Version:** 1.0  
**Maintainer:** SampleMind AI DevOps Team