# 🚀 CI/CD Workflows Documentation

This directory contains GitHub Actions workflows for automated testing, deployment, security scanning, and dependency management for SampleMind AI.

## 📋 Table of Contents

- [Overview](#overview)
- [Workflows](#workflows)
- [Pipeline Architecture](#pipeline-architecture)
- [Environment Setup](#environment-setup)
- [Usage Guide](#usage-guide)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

Our CI/CD pipeline implements enterprise-grade automation with:

- ✅ Automated testing with 80%+ coverage requirement
- 🔒 Comprehensive security scanning
- 🚀 Zero-downtime deployments
- 📦 Automated dependency updates
- 📚 Documentation deployment
- 🔄 Blue-green and canary deployment strategies

**Key Metrics:**
- Pipeline time: < 15 minutes
- Deployment frequency: On every merge to main
- Success rate target: 99%+
- Automatic rollback on failure

---

## 📂 Workflows

### 1. Main Deployment Pipeline (`deploy.yml`)

**Trigger:** Push to main, pull requests, manual dispatch

**Purpose:** Complete CI/CD pipeline from code validation to production deployment

**Stages:**

1. **Lint** (2-3 min)
   - Ruff linting
   - Black formatting check
   - isort import sorting check
   - Code quality validation

2. **Type Check** (2-3 min)
   - MyPy static type checking
   - Type annotation validation

3. **Test** (5-7 min)
   - Unit tests with pytest
   - Integration tests
   - 80% minimum coverage requirement
   - Parallel test execution

4. **Security** (3-5 min)
   - Bandit security scanner
   - Safety dependency vulnerability check
   - Trivy container vulnerability scan
   - SARIF upload to GitHub Security

5. **Build** (5-8 min)
   - Multi-architecture Docker build (amd64/arm64)
   - Push to GitHub Container Registry
   - Container security scan

6. **Deploy to Staging** (3-5 min)
   - Kubernetes blue-green deployment
   - Health checks
   - Automatic rollback on failure
   - Traffic switch to new version

7. **Load Test Staging** (5 min)
   - Automated load testing with Locust
   - 100 concurrent users
   - Performance validation
   - Error rate checking (< 0.1%)

8. **Deploy to Production** (15-20 min)
   - Manual approval required (2 reviewers + 5 min wait)
   - Canary deployment (10% → 50% → 100%)
   - Continuous monitoring between stages
   - Automatic rollback on errors
   - GitHub release creation

**Success Criteria:**
- All tests pass
- Coverage ≥ 80%
- No security vulnerabilities
- Load test passes
- Health checks successful

**Usage:**
```bash
# Automatic trigger on push to main
git push origin main

# Manual trigger via GitHub UI
# Actions > Deploy SampleMind AI > Run workflow
```

---

### 2. Security Scanning (`security-scan.yml`)

**Trigger:** Daily at 2 AM UTC, push to main (dependency changes), manual dispatch

**Purpose:** Comprehensive daily security audits

**Scans:**

1. **Dependency Security**
   - Safety: Python package vulnerabilities
   - pip-audit: Additional dependency checking
   - Severity-based alerting

2. **Code Security**
   - Bandit: Python code security issues
   - High/medium severity detection
   - Security anti-pattern identification

3. **Container Security**
   - Trivy: Container vulnerability scanning
   - Base image security
   - Package vulnerability detection

4. **Secret Detection**
   - Gitleaks: Secret scanning
   - TruffleHog: Additional secret detection
   - Full git history analysis

5. **License Compliance**
   - pip-licenses: License report generation
   - GPL license detection
   - License compatibility checking

**Alerting:**
- Creates GitHub issues for findings
- Uploads SARIF to GitHub Security
- Slack notifications (if configured)
- Security team notification

**Usage:**
```bash
# Manual trigger
gh workflow run security-scan.yml
```

---

### 3. Dependency Updates (`dependency-update.yml`)

**Trigger:** Weekly on Mondays at 9 AM UTC, manual dispatch

**Purpose:** Automated dependency maintenance with testing

**Process:**

1. **Check Updates**
   - Scan Python dependencies
   - Scan npm dependencies
   - Generate update reports

2. **Update Python**
   - Update requirements.txt
   - Update dev/test requirements
   - Run smoke tests
   - Create PR if successful

3. **Update npm**
   - Update package.json
   - Update frontend dependencies
   - Run build tests
   - Create PR if successful

4. **Security Audit**
   - Run safety check on updated deps
   - Run npm audit
   - Validate no new vulnerabilities

**Pull Request Features:**
- Automatic assignment
- Comprehensive change description
- Review checklist
- Test results included
- Security validation

**Usage:**
```bash
# Check what updates are available
gh workflow run dependency-update.yml

# Review auto-created PRs
gh pr list --label dependencies
```

---

### 4. Documentation Deployment (`docs.yml`)

**Trigger:** Push to main (docs changes), pull requests, manual dispatch

**Purpose:** Automated documentation building and deployment

**Process:**

1. **Build Documentation**
   - MkDocs site generation
   - API documentation from docstrings
   - Validation checks

2. **Test Documentation**
   - Markdown linting
   - Spell checking
   - Code example validation
   - Link checking

3. **Deploy to GitHub Pages**
   - Automatic deployment on main
   - Live at: `https://[org].github.io/SampleMind-AI/`

4. **Deploy to Docs Site**
   - Deploy to docs.samplemind.ai (if configured)
   - S3/CloudFront deployment
   - CDN cache invalidation

5. **Additional Tasks**
   - PDF generation
   - Search index update
   - Coverage reporting

**Usage:**
```bash
# Preview locally
mkdocs serve

# Manual deployment
gh workflow run docs.yml
```

---

## 🏗️ Pipeline Architecture

### Deployment Strategy

#### Staging Environment
- **URL:** https://staging.samplemind.ai
- **Strategy:** Blue-Green deployment
- **Protection:** None (automatic)
- **Purpose:** Integration testing, load testing

#### Production Environment
- **URL:** https://samplemind.ai
- **Strategy:** Canary deployment
- **Protection:** 
  - 2 required reviewers
  - 5-minute wait timer
- **Rollout:** 10% → 50% → 100% with 5-min monitoring between stages

### Deployment Flow

```
┌─────────────┐
│   Commit    │
└──────┬──────┘
       │
       v
┌─────────────┐
│  Lint/Test  │ ← Parallel execution
└──────┬──────┘
       │
       v
┌─────────────┐
│  Security   │ ← Scanning
└──────┬──────┘
       │
       v
┌─────────────┐
│    Build    │ ← Multi-arch Docker
└──────┬──────┘
       │
       v
┌─────────────┐
│   Staging   │ ← Blue-Green
└──────┬──────┘
       │
       v
┌─────────────┐
│  Load Test  │ ← Performance validation
└──────┬──────┘
       │
       v
┌─────────────┐
│  Approval   │ ← Manual gate
└──────┬──────┘
       │
       v
┌─────────────┐
│ Production  │ ← Canary (10% → 50% → 100%)
└─────────────┘
```

---

## ⚙️ Environment Setup

### Required Secrets

Configure these in GitHub Settings > Secrets and variables > Actions:

#### Authentication
- `GITHUB_TOKEN` - Automatically provided
- `CODECOV_TOKEN` - For coverage reporting
- `ANTHROPIC_API_KEY` - For AI testing
- `OPENAI_API_KEY` - For AI testing
- `GOOGLE_API_KEY` - For AI testing

#### Kubernetes
- `KUBE_CONFIG_STAGING` - Base64 encoded kubeconfig
- `KUBE_CONFIG_PRODUCTION` - Base64 encoded kubeconfig

#### AWS (Optional)
- `AWS_ACCESS_KEY_ID` - For S3 docs deployment
- `AWS_SECRET_ACCESS_KEY` - For S3 docs deployment
- `CLOUDFRONT_DISTRIBUTION_ID` - For CDN invalidation

#### Notifications (Optional)
- `SLACK_WEBHOOK_URL` - For Slack notifications
- `GITLEAKS_LICENSE` - For Gitleaks Pro features
- `ALGOLIA_API_KEY` - For documentation search

### Environment Configuration

#### Staging
```yaml
name: staging
url: https://staging.samplemind.ai
protection_rules: []
```

#### Production
```yaml
name: production
url: https://samplemind.ai
protection_rules:
  - required_reviewers: 2
  - wait_timer: 300  # 5 minutes
```

### Local Testing

Test workflows locally using `act`:

```bash
# Install act
brew install act  # macOS
# or
sudo apt install act  # Linux

# Test a workflow
act -W .github/workflows/deploy.yml -j lint

# Test with secrets
act -W .github/workflows/deploy.yml --secret-file .secrets
```

---

## 📖 Usage Guide

### Deploying to Staging

Staging deploys automatically on merge to main:

```bash
# Create feature branch
git checkout -b feature/my-feature

# Make changes and commit
git add .
git commit -m "feat: add new feature"

# Push and create PR
git push origin feature/my-feature
gh pr create

# After review and merge
# Staging deployment happens automatically
```

### Deploying to Production

Production requires manual approval:

```bash
# 1. Merge to main (triggers staging)
# 2. Staging deployment completes
# 3. Load tests pass
# 4. Production approval request sent
# 5. Two reviewers approve
# 6. Wait 5 minutes
# 7. Canary deployment begins
```

### Manual Workflow Triggers

```bash
# Security scan
gh workflow run security-scan.yml

# Dependency updates
gh workflow run dependency-update.yml

# Documentation deployment
gh workflow run docs.yml

# Manual production deploy
gh workflow run deploy.yml -f environment=production
```

### Monitoring Deployments

```bash
# Watch workflow run
gh run watch

# View recent runs
gh run list --workflow=deploy.yml

# View specific run
gh run view <run-id>

# Download artifacts
gh run download <run-id>
```

---

## 🔧 Troubleshooting

### Common Issues

#### Failed Tests

**Issue:** Tests fail in CI but pass locally

**Solutions:**
```bash
# Run tests in same environment as CI
docker run --rm -it python:3.12 /bin/bash
pip install -r requirements.txt
pytest tests/

# Check test isolation
pytest tests/ --lf  # Last failed
pytest tests/ -x    # Stop on first failure

# Check for timing issues
pytest tests/ --durations=10
```

#### Deployment Failures

**Issue:** Deployment fails health checks

**Solutions:**
```bash
# Check logs
kubectl logs -n staging deployment/samplemind-backend

# Check pod status
kubectl get pods -n staging

# Manual rollback
kubectl rollout undo deployment/samplemind-backend -n staging

# Check events
kubectl get events -n staging --sort-by='.lastTimestamp'
```

#### Security Scan Failures

**Issue:** Security scanner reports false positives

**Solutions:**
```yaml
# Add to .bandit config
[bandit]
exclude = /tests/

# Ignore specific issues
skips = B101,B601

# Add safety ignore
# In pyproject.toml
[tool.safety]
ignore = ["51668"]  # Specific CVE
```

#### Docker Build Failures

**Issue:** Multi-arch build times out or fails

**Solutions:**
```bash
# Test build locally
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -f deployment/docker/Dockerfile.backend \
  -t test:local .

# Use cache
docker buildx build \
  --cache-from=type=gha \
  --cache-to=type=gha,mode=max \
  -t test:local .

# Build single arch for testing
docker build \
  -f deployment/docker/Dockerfile.backend \
  -t test:local .
```

### Debugging Workflows

#### Enable Debug Logging

```bash
# Set repository secrets
ACTIONS_RUNNER_DEBUG=true
ACTIONS_STEP_DEBUG=true
```

#### View Detailed Logs

```bash
# Download logs
gh run download <run-id>

# View specific job logs
gh run view <run-id> --log --job=<job-id>
```

#### Test Workflow Syntax

```bash
# Validate workflow syntax
gh workflow view deploy.yml

# List all workflows
gh workflow list
```

---

## 📊 Metrics and Monitoring

### Pipeline Metrics

Monitor these metrics in GitHub Actions:

- **Pipeline Success Rate:** Target 99%+
- **Average Pipeline Time:** Target < 15 minutes
- **Deployment Frequency:** Daily average
- **Mean Time to Recovery:** Target < 30 minutes
- **Change Failure Rate:** Target < 5%

### Accessing Metrics

```bash
# View workflow runs
gh run list --workflow=deploy.yml --limit=50

# Success rate
gh run list --workflow=deploy.yml --json conclusion \
  | jq '[.[] | select(.conclusion=="success")] | length'

# Average duration
gh run list --workflow=deploy.yml --json startedAt,completedAt \
  | jq '[.[] | (.completedAt - .startedAt)] | add / length'
```

---

## 🔗 Related Documentation

- [Deployment Guide](../../docs/DEPLOYMENT_GUIDE.md)
- [Security Policy](../../SECURITY.md)
- [Contributing Guidelines](../../docs/CONTRIBUTING.md)
- [Phase 6 Implementation Plan](../../docs/PHASES_3-6_IMPLEMENTATION_PLAN.md)

---

## 📝 Maintenance

### Regular Tasks

**Weekly:**
- Review Dependabot PRs
- Check security scan results
- Update blocked dependencies

**Monthly:**
- Review workflow performance metrics
- Update GitHub Actions versions
- Audit deployment logs

**Quarterly:**
- Review and update deployment strategies
- Conduct chaos engineering tests
- Update documentation

---

## 🆘 Support

**Issues with workflows?**
1. Check [Troubleshooting](#troubleshooting) section
2. Review workflow logs
3. Create an issue with workflow run ID
4. Tag: `ci/cd`, `deployment`, or `security`

**Need help?**
- GitHub Discussions: Technical questions
- Slack: `#devops` channel (if configured)
- Email: devops@samplemind.ai

---

**Last Updated:** January 6, 2025  
**Maintained by:** SampleMind AI DevOps Team  
**Version:** 1.0