# SampleMind AI - Load Testing Suite

**Phase 6: Production Deployment - Task 6.1**

Comprehensive load testing suite for validating production readiness and performance at scale.

## Overview

This load testing suite simulates realistic production traffic patterns to ensure SampleMind AI can handle enterprise-level workloads. It includes three distinct user types with weighted behaviors:

- **AudioAnalysisUser** (50% weight) - Typical end-users analyzing audio files
- **APIUser** (30% weight) - Automated systems and integrations
- **AdminUser** (10% weight) - Administrators and system monitoring

## Success Criteria

✅ **Performance Targets:**
- Handle 1000+ concurrent users
- p95 response time < 500ms
- Error rate < 0.1%
- No memory leaks
- CPU usage < 80%

## Installation

### 1. Install Dependencies

```bash
# From project root
pip install -r tests/load/requirements.txt
```

### 2. Verify Installation

```bash
locust --version
# Should output: locust 2.20.0 or higher
```

## Usage

### Basic Usage - Web UI Mode

The easiest way to run load tests with interactive controls:

```bash
# Start Locust with web UI
locust -f tests/load/locustfile.py --host=http://localhost:8000

# Then open browser to: http://localhost:8089
```

In the web UI:
1. Enter number of users (e.g., 100)
2. Enter spawn rate (e.g., 10 users/second)
3. Click "Start swarming"
4. Monitor real-time metrics and charts

### Headless Mode - Automated Testing

For CI/CD pipelines and automated testing:

```bash
# Run with specific configuration
locust -f tests/load/locustfile.py \
    --host=http://localhost:8000 \
    --users 1000 \
    --spawn-rate 50 \
    --run-time 10m \
    --headless \
    --html report.html
```

**Parameters:**
- `--users`: Total number of concurrent users
- `--spawn-rate`: Users to spawn per second
- `--run-time`: Test duration (e.g., 10m, 1h)
- `--headless`: Run without web UI
- `--html`: Generate HTML report

### Progressive Load Testing (Recommended)

Test with increasing load stages to identify breaking points:

#### Stage 1: Baseline (100 users, 1 min)
```bash
locust -f tests/load/locustfile.py \
    --host=http://localhost:8000 \
    --users 100 \
    --spawn-rate 10 \
    --run-time 1m \
    --headless \
    --html baseline-report.html
```

#### Stage 2: Normal Load (500 users, 5 min)
```bash
locust -f tests/load/locustfile.py \
    --host=http://localhost:8000 \
    --users 500 \
    --spawn-rate 20 \
    --run-time 5m \
    --headless \
    --html normal-report.html
```

#### Stage 3: Peak Load (1000 users, 10 min)
```bash
locust -f tests/load/locustfile.py \
    --host=http://localhost:8000 \
    --users 1000 \
    --spawn-rate 50 \
    --run-time 10m \
    --headless \
    --html peak-report.html
```

#### Stage 4: Stress Test (2000 users, 5 min)
```bash
locust -f tests/load/locustfile.py \
    --host=http://localhost:8000 \
    --users 2000 \
    --spawn-rate 100 \
    --run-time 5m \
    --headless \
    --html stress-report.html
```

### Distributed Load Testing

For very high load, run Locust in distributed mode:

#### Master Node
```bash
locust -f tests/load/locustfile.py \
    --host=http://production.samplemind.ai \
    --master \
    --expect-workers=4
```

#### Worker Nodes (run on 4 different machines)
```bash
locust -f tests/load/locustfile.py \
    --worker \
    --master-host=<master-ip>
```

## Test Scenarios

### AudioAnalysisUser (Weight: 5)

Simulates typical user behavior:

| Task | Weight | Description |
|------|--------|-------------|
| analyze_audio | 3 | Primary operation - analyze uploaded audio |
| upload_file | 1 | Upload new audio files |
| view_results | 2 | View analysis results |
| list_files | 2 | Browse file library |
| search_files | 1 | Search for specific samples |

**Wait time:** 1-5 seconds between tasks

### APIUser (Weight: 3)

Simulates programmatic API access:

| Task | Weight | Description |
|------|--------|-------------|
| api_analyze | 5 | API-based audio analysis |
| api_batch_process | 2 | Batch processing jobs |
| api_get_status | 3 | Job status polling |

**Wait time:** 0.5-2 seconds (faster than humans)

### AdminUser (Weight: 1)

Simulates administrative operations:

| Task | Weight | Description |
|------|--------|-------------|
| view_dashboard | 3 | Admin dashboard monitoring |
| manage_users | 1 | User management operations |
| system_health_check | 2 | System health monitoring |

**Wait time:** 5-10 seconds (less frequent)

## Metrics Collection

The load tests automatically collect and report:

### Response Time Metrics
- **p50** (median): 50% of requests faster than this
- **p95**: 95% of requests faster than this (target: < 500ms)
- **p99**: 99% of requests faster than this

### Throughput Metrics
- **Requests/second**: Total request rate
- **Failures/second**: Error rate
- **Average response time**: Mean response time

### Error Metrics
- **Total errors**: Count of failed requests
- **Error rate**: Percentage of failures (target: < 0.1%)
- **Errors by endpoint**: Breakdown by API route

## Understanding Results

### Good Performance Indicators ✅
- p95 response time < 500ms
- Error rate < 0.1%
- Stable memory usage
- CPU usage < 80%
- No timeout errors

### Warning Signs ⚠️
- p95 response time 500-1000ms
- Error rate 0.1-1%
- Increasing response times over test duration
- Memory usage trending upward

### Critical Issues 🚨
- p95 response time > 1000ms
- Error rate > 1%
- Memory leaks (continuous growth)
- CPU saturation (100%)
- Database connection exhaustion

## Monitoring During Tests

### System Metrics to Monitor

While load tests run, monitor these system metrics:

```bash
# CPU usage
top -bn1 | grep "Cpu(s)"

# Memory usage
free -h

# Network connections
netstat -an | grep :8000 | wc -l

# Database connections
# Check MongoDB/Redis connection pools
```

### Application Metrics

Monitor via Prometheus/Grafana dashboards:
- API endpoint response times
- Database query performance
- Cache hit rates
- Celery queue depth
- Error rates by endpoint

## Troubleshooting

### Issue: Connection Refused

**Cause:** Target server not running

**Solution:**
```bash
# Ensure backend is running
python -m uvicorn src.samplemind.main:app --host 0.0.0.0 --port 8000
```

### Issue: High Error Rate

**Cause:** Database/Redis not available or overwhelmed

**Solution:**
1. Check database connection limits
2. Verify Redis is running
3. Review application logs for errors
4. Scale database resources if needed

### Issue: Slow Response Times

**Cause:** Insufficient resources or unoptimized queries

**Solution:**
1. Profile slow endpoints
2. Check database indexes
3. Review cache hit rates
4. Scale application horizontally

### Issue: Memory Leaks

**Cause:** Unclosed connections or memory not being freed

**Solution:**
1. Review connection pool settings
2. Check for circular references
3. Profile memory usage over time
4. Update to latest dependencies

## Best Practices

### 1. Start Small, Scale Up
Begin with low user counts and gradually increase:
- 10 → 50 → 100 → 500 → 1000 users

### 2. Monitor Everything
Keep these open during tests:
- System resource monitors (CPU, RAM, disk)
- Application logs
- Database metrics
- Load test dashboard

### 3. Test Realistic Scenarios
- Use production-like data
- Simulate real user wait times
- Include error scenarios (404s, timeouts)

### 4. Isolate Test Environment
- Use dedicated test infrastructure
- Don't test against production
- Ensure consistent baseline (no other load)

### 5. Document Results
Save reports for comparison:
```bash
# Organized by date and test type
reports/
├── 2025-01-06/
│   ├── baseline-100users.html
│   ├── normal-500users.html
│   ├── peak-1000users.html
│   └── stress-2000users.html
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Load Testing

on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM
  workflow_dispatch:  # Manual trigger

jobs:
  load-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          pip install -r tests/load/requirements.txt
      
      - name: Start application
        run: |
          docker-compose up -d
          sleep 30  # Wait for startup
      
      - name: Run load test
        run: |
          locust -f tests/load/locustfile.py \
            --host=http://localhost:8000 \
            --users 500 \
            --spawn-rate 25 \
            --run-time 5m \
            --headless \
            --html load-test-report.html
      
      - name: Upload report
        uses: actions/upload-artifact@v3
        with:
          name: load-test-report
          path: load-test-report.html
      
      - name: Check success criteria
        run: |
          # Parse report and fail if criteria not met
          python scripts/check_load_test_results.py load-test-report.html
```

## Advanced Configuration

### Custom User Distribution

Edit [`locustfile.py`](locustfile.py:35) to adjust user weights:

```python
class AudioAnalysisUser(HttpUser):
    weight = 5  # 50% of users

class APIUser(HttpUser):
    weight = 3  # 30% of users

class AdminUser(HttpUser):
    weight = 1  # 10% of users
```

### Custom Wait Times

Adjust think time between tasks:

```python
# Fast users (API clients)
wait_time = between(0.5, 2)

# Normal users (web interface)
wait_time = between(1, 5)

# Slow users (research/browsing)
wait_time = between(5, 10)
```

### Environment Variables

Configure via environment variables:

```bash
export TARGET_HOST="http://staging.samplemind.ai"
export AUTH_TOKEN="your-test-token"
export TEST_DURATION="15m"

locust -f tests/load/locustfile.py --host=$TARGET_HOST
```

## Reference

### Official Locust Documentation
- [Locust Docs](https://docs.locust.io/)
- [Writing Tests](https://docs.locust.io/en/stable/writing-a-locustfile.html)
- [Running Distributed](https://docs.locust.io/en/stable/running-distributed.html)

### Phase 6 Implementation Plan
- See [`docs/PHASES_3-6_IMPLEMENTATION_PLAN.md`](../../docs/PHASES_3-6_IMPLEMENTATION_PLAN.md) lines 935-986

## Support

For issues or questions:
1. Check this README first
2. Review [`locustfile.py`](locustfile.py) comments
3. Check application logs
4. Open an issue on GitHub

---

**Last Updated:** January 6, 2025  
**Phase:** 6.1 - Comprehensive Load Testing Suite  
**Status:** Ready for Production Testing ✅