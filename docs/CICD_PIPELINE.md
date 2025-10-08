# 🔄 CI/CD Pipeline Documentation

**Overview:** Automated testing, building, and deployment workflows  
**Status:** Configured for backend and frontend  
**Update Required:** Python version 3.11

---

## 📋 Current Workflows

### 1. **ci.yml** - Unified CI Pipeline
**Triggers:**
- Push to `main` branch
- Pull requests to `main`

**Jobs:**
- ✅ Lint & Test (Python 3.12)
- ✅ Docker Build

**Issues:**
- ❌ Python version: Should be 3.11 (currently 3.12)
- ❌ Missing coverage reporting
- ❌ Incomplete dependency installation

---

### 2. **backend-ci.yml** - Backend CI/CD
**Triggers:**
- Push to `main`, `develop`
- Pull requests on backend files

**Jobs:**
1. **Lint** - Code quality checks
   - Black formatter
   - isort imports
   - flake8 linting
   - mypy type checking
   - pylint code analysis
   - Bandit security scanning

2. **Test** - Unit & integration tests
   - MongoDB service
   - Redis service
   - pytest with coverage
   - Codecov upload

3. **Build** - Docker image
   - Multi-platform buildx
   - Docker Hub push
   - Caching enabled

4. **Deploy** - Environment deployment
   - Dev environment (develop branch)
   - Prod environment (main branch)

**Issues:**
- ❌ Python version: Should be 3.11 (currently 3.12)
- ⚠️ Deployment steps placeholder only

---

### 3. **frontend-ci.yml** - Frontend CI/CD
**Triggers:**
- Push to `main`, `develop`
- Pull requests on frontend files

**Jobs:**
1. **Lint & Test**
   - ESLint
   - TypeScript check
   - Jest tests
   - Next.js build

2. **Build & Push** - Docker image
   - Docker Hub push
   - Build args for API URL

3. **Deploy**
   - Vercel preview (PRs)
   - Vercel production (main)

**Status:** ✅ Looks good!

---

## 🔧 Required Fixes

### Priority 1: Python Version Update
**Files to fix:**
- `.github/workflows/ci.yml` (line 16)
- `.github/workflows/backend-ci.yml` (line 21)

**Change:**
```yaml
# FROM:
PYTHON_VERSION: '3.12'

# TO:
PYTHON_VERSION: '3.11'
```

**Reason:** Project migrated to Python 3.11 for compatibility

---

### Priority 2: Add Coverage Reporting to ci.yml
**File:** `.github/workflows/ci.yml`

**Add after pytest:**
```yaml
- name: Test with coverage
  run: |
    pip install pytest-cov
    pytest tests/ --cov=src --cov-report=xml --cov-report=term

- name: Upload coverage
  uses: codecov/codecov-action@v3
  with:
    file: ./coverage.xml
    fail_ci_if_error: false
```

---

### Priority 3: Complete Dependency Installation
**File:** `.github/workflows/ci.yml`

**Replace line 20 with:**
```yaml
- name: Install dependencies
  run: |
    python -m pip install --upgrade pip
    pip install -e .
    pip install pytest pytest-cov pytest-asyncio
```

**Reason:** Use proper editable install with all dependencies

---

### Priority 4: Add CI Status Badge to README
**File:** `README.md`

**Add:**
```markdown
[![CI Status](https://github.com/YOUR-USERNAME/samplemind-ai-v6/workflows/CI/badge.svg)](https://github.com/YOUR-USERNAME/samplemind-ai-v6/actions)
[![Coverage](https://codecov.io/gh/YOUR-USERNAME/samplemind-ai-v6/branch/main/graph/badge.svg)](https://codecov.io/gh/YOUR-USERNAME/samplemind-ai-v6)
```

---

## 🚀 Recommended Additions

### 1. **Release Workflow**
**File:** `.github/workflows/release.yml` (new)

```yaml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  create-release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Create Release
        uses: actions/create-release@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          tag_name: ${{ github.ref }}
          release_name: Release ${{ github.ref }}
          draft: false
          prerelease: false

  publish-pypi:
    runs-on: ubuntu-latest
    needs: create-release
    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Build package
        run: |
          pip install build
          python -m build
      
      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          user: __token__
          password: ${{ secrets.PYPI_TOKEN }}
```

---

### 2. **Security Scanning Workflow**
**File:** `.github/workflows/security.yml` (new)

```yaml
name: Security Scan

on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly on Sunday
  workflow_dispatch:

jobs:
  dependency-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install pip-audit safety
      
      - name: Run pip-audit
        run: pip-audit
      
      - name: Run safety check
        run: safety check --json
      
      - name: SAST with Bandit
        run: |
          pip install bandit
          bandit -r src/ -f json -o bandit-report.json || true
      
      - name: Upload results
        uses: actions/upload-artifact@v3
        with:
          name: security-reports
          path: |
            bandit-report.json

  code-scanning:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Initialize CodeQL
        uses: github/codeql-action/init@v2
        with:
          languages: python
      
      - name: Perform CodeQL Analysis
        uses: github/codeql-action/analyze@v2
```

---

### 3. **Performance Testing Workflow**
**File:** `.github/workflows/performance.yml` (new)

```yaml
name: Performance Tests

on:
  push:
    branches: [main]
  schedule:
    - cron: '0 0 * * 1'  # Weekly on Monday

jobs:
  benchmark:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -e .
          pip install pytest-benchmark memory-profiler
      
      - name: Run benchmarks
        run: |
          pytest tests/performance/ --benchmark-only
      
      - name: Memory profiling
        run: |
          python -m memory_profiler tests/performance/memory_test.py
```

---

### 4. **Automated Dependency Updates**
**File:** `.github/dependabot.yml` (new)

```yaml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10
    labels:
      - "dependencies"
      - "python"

  - package-ecosystem: "npm"
    directory: "/frontend/web"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10
    labels:
      - "dependencies"
      - "frontend"

  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
```

---

### 5. **Beta Release Workflow**
**File:** `.github/workflows/beta-release.yml` (new)

```yaml
name: Beta Release

on:
  push:
    branches:
      - develop
  workflow_dispatch:

jobs:
  beta-release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -e .
      
      - name: Run tests
        run: pytest tests/ -v
      
      - name: Build package
        run: |
          pip install build
          python -m build
      
      - name: Create pre-release
        uses: actions/create-release@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          tag_name: v0.6.0-beta.${{ github.run_number }}
          release_name: Beta v0.6.0-${{ github.run_number }}
          draft: false
          prerelease: true
          body: |
            Beta release for testing purposes.
            
            **Changes:**
            - See commits since last release
            
            **Test Status:** ${{ job.status }}
```

---

## 📊 CI/CD Pipeline Flow

```
┌─────────────┐
│  Git Push   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│    Lint     │ ← Black, ruff, isort, mypy
└──────┬──────┘
       │ Pass
       ▼
┌─────────────┐
│  Run Tests  │ ← pytest, coverage
└──────┬──────┘
       │ Pass
       ▼
┌─────────────┐
│   Build     │ ← Docker, package
└──────┬──────┘
       │ Pass
       ▼
┌─────────────┐
│   Deploy    │ ← Dev/Prod environments
└─────────────┘
```

---

## 🔒 Required Secrets

### GitHub Secrets to Set

**Docker Hub:**
- `DOCKER_USERNAME` - Docker Hub username
- `DOCKER_PASSWORD` - Docker Hub token

**Vercel (Frontend):**
- `VERCEL_TOKEN` - Vercel deployment token
- `VERCEL_ORG_ID` - Vercel organization ID
- `VERCEL_PROJECT_ID` - Vercel project ID

**PyPI (Optional):**
- `PYPI_TOKEN` - PyPI API token for package publishing

**Codecov (Optional):**
- `CODECOV_TOKEN` - Codecov upload token

**API URLs:**
- `API_URL` - Production API URL for frontend

---

## 🎯 Testing Strategy in CI

### Unit Tests
- Run on every push
- Fast execution (< 2 min)
- No external dependencies
- 100% must pass

### Integration Tests
- Run on PR to main
- Require services (MongoDB, Redis)
- Slower execution (< 5 min)
- 95% must pass

### E2E Tests
- Run on schedule (daily)
- Full application workflow
- Slow execution (< 15 min)
- 90% must pass

---

## 📈 Performance Targets

**CI/CD Speed:**
- Lint: < 1 minute
- Tests: < 5 minutes
- Build: < 3 minutes
- Deploy: < 2 minutes
- **Total:** < 12 minutes

**Current:**
- Backend CI: ~8 minutes
- Frontend CI: ~5 minutes

---

## 🐛 Common CI Issues & Solutions

### Issue: Tests fail in CI but pass locally
**Cause:** Environment differences  
**Solution:**
```bash
# Match CI environment
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e .
pytest tests/
```

### Issue: Docker build fails
**Cause:** Missing files or wrong context  
**Solution:** Check `.dockerignore` and build context

### Issue: Secrets not available
**Cause:** Not set in GitHub settings  
**Solution:** Settings → Secrets and variables → Actions

### Issue: Flaky tests
**Cause:** Race conditions or network issues  
**Solution:** Add retries or mark as flaky:
```python
@pytest.mark.flaky(reruns=3)
def test_network_call():
    pass
```

---

## 📝 Deployment Process

### Development Environment
1. Push to `develop` branch
2. CI runs tests
3. Docker image built
4. Auto-deploy to dev environment
5. Smoke tests run

### Production Environment
1. Create release tag (v*.*.*)
2. CI runs full test suite
3. Build production images
4. Manual approval required
5. Deploy to production
6. Health checks
7. Rollback if needed

---

## 🔧 Local CI Testing

**Test CI workflows locally using act:**
```bash
# Install act
brew install act  # macOS
# or
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash

# Run CI workflow
act push

# Run specific job
act -j lint

# Use secrets
act -s GITHUB_TOKEN=your_token
```

---

## ✅ CI/CD Checklist

**Before Merge:**
- [ ] All tests pass
- [ ] Coverage > 60%
- [ ] Lint checks pass
- [ ] No security issues
- [ ] Build succeeds
- [ ] Docker image builds

**After Merge:**
- [ ] CI runs successfully
- [ ] Coverage uploaded
- [ ] Docker pushed
- [ ] Deploy successful (if applicable)

---

## 📞 Support

**CI/CD Issues?**
- Check workflow logs
- Review this documentation
- Ask in #dev-discussion (Discord)
- Open issue with `ci/cd` label

---

**Last Updated:** 2025-01-04  
**Maintained by:** Core Team  
**CI Platform:** GitHub Actions
