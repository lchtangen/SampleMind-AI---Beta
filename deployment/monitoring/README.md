# SampleMind AI - Monitoring Infrastructure

Comprehensive monitoring, alerting, and observability setup for SampleMind AI platform.

## Overview

This monitoring stack provides:

- **Metrics Collection**: Prometheus for time-series data
- **Visualization**: Grafana dashboards for system, database, audio processing, and ML models
- **Alerting**: AlertManager with multi-channel notifications (Slack, Email, PagerDuty)
- **Exporters**: Node, cAdvisor, MongoDB, Redis, GPU metrics
- **Health Checks**: Endpoint monitoring and service health

## Architecture

```
┌─────────────────┐
│   Application   │
│   (FastAPI)     │
└────────┬────────┘
         │ metrics
         ▼
┌─────────────────┐      ┌──────────────┐
│   Prometheus    │─────▶│ AlertManager │
└────────┬────────┘      └──────┬───────┘
         │                       │
         │ queries               │ notifications
         ▼                       ▼
┌─────────────────┐      ┌──────────────┐
│    Grafana      │      │ Slack/Email  │
│   Dashboards    │      │  PagerDuty   │
└─────────────────┘      └──────────────┘
```

## Quick Start

### Prerequisites

- Docker & Docker Compose
- 2GB+ RAM for monitoring stack
- Port availability: 3000 (Grafana), 9090 (Prometheus), 9093 (AlertManager)

### 1. Environment Setup

Create `.env` file in the monitoring directory:

```bash
# Grafana
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=your_secure_password

# Database (for Grafana persistence)
POSTGRES_HOST=postgres:5432
GRAFANA_DB_NAME=grafana
GRAFANA_DB_USER=grafana
GRAFANA_DB_PASSWORD=your_db_password

# MongoDB
MONGODB_URI=mongodb://samplemind:password@mongodb:27017/samplemind

# Redis
REDIS_ADDR=redis:6379
REDIS_PASSWORD=your_redis_password

# Email (SMTP)
SMTP_HOST=smtp.gmail.com:587
SMTP_USER=alerts@samplemind.ai
SMTP_PASSWORD=your_smtp_password
SMTP_FROM=alerts@samplemind.ai

# Slack
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# PagerDuty
PAGERDUTY_SERVICE_KEY=your_pagerduty_integration_key
```

### 2. Start Monitoring Stack

```bash
# Start all services
cd monitoring
docker-compose -f docker-compose.monitoring.yml up -d

# Check service status
docker-compose -f docker-compose.monitoring.yml ps

# View logs
docker-compose -f docker-compose.monitoring.yml logs -f
```

### 3. Access Services

- **Grafana**: http://localhost:3000 (admin/your_password)
- **Prometheus**: http://localhost:9090
- **AlertManager**: http://localhost:9093

### 4. Import Dashboards

Dashboards are automatically provisioned from `grafana/dashboards/`:

1. System Overview: `samplemind-system-overview`
2. Audio Processing: `samplemind-audio-processing`
3. Database Performance: `samplemind-database-performance`
4. ML Models: `samplemind-ml-models`

## Configuration

### Prometheus

Main configuration: `prometheus/prometheus.yml`

**Scrape Intervals**:
- Global: 15s
- Critical services: Can be adjusted per job

**Retention**:
- Time: 15 days
- Size: 50GB

**Alert Rules**:
- Critical: `prometheus/alerts/critical.yml`
- Warning: `prometheus/alerts/warning.yml`

### AlertManager

Configuration: `alertmanager/alertmanager.yml`

**Alert Routing**:
- Critical → PagerDuty + Slack + Email
- Warning → Slack + Email
- Team-specific → Respective channels

**Inhibition Rules**:
- Suppress warnings when critical alerts fire
- Suppress specific alerts when service is down

### Grafana

**Dashboards**: Auto-provisioned from `grafana/dashboards/`

**Data Sources**: Prometheus (auto-configured)

**Plugins**: Pre-installed
- grafana-piechart-panel
- grafana-worldmap-panel

## Dashboards

### 1. System Overview (`system-overview.json`)

**Key Metrics**:
- Request rate (req/s)
- Response times (p50, p95, p99)
- Error rates (4xx, 5xx)
- CPU & Memory usage
- Network I/O
- Active connections

**Thresholds**:
- Response time p95 > 500ms (warning), > 1s (critical)
- Error rate > 0.5% (warning), > 1% (critical)
- CPU/Memory > 80% (warning), > 95% (critical)

### 2. Audio Processing (`audio-processing.json`)

**Key Metrics**:
- Processing time by task type
- Queue depth (Celery)
- Success/failure rates
- Batch processing metrics
- File size distribution
- Processing throughput

**Thresholds**:
- Queue depth > 1000 (warning), > 5000 (critical)
- Task failure rate > 5% (warning)

### 3. Database Performance (`database-performance.json`)

**Key Metrics**:
- Query performance (slow queries)
- Connection pool utilization
- Cache hit rates (Redis)
- Index efficiency
- MongoDB operations/sec
- Vector search latency

**Thresholds**:
- Connection pool > 75% (warning), > 95% (critical)
- Cache hit rate < 60% (warning)
- Query latency > 200ms (warning), > 500ms (critical)

### 4. ML Models (`ml-models.json`)

**Key Metrics**:
- Inference time per model
- ONNX vs original usage
- Model accuracy
- GPU/CPU utilization
- Batch size optimization
- Model loading time

**Thresholds**:
- GPU memory > 80% (warning), > 95% (critical)
- Inference failure rate > 5% (critical)

## Alert Configuration

### Critical Alerts (Immediate Response)

1. **API Error Rate > 1%**
   - Impact: Users experiencing service degradation
   - Action: Check logs, investigate endpoints

2. **Response Time p95 > 1s**
   - Impact: Severe UX degradation
   - Action: Check slow queries, database performance

3. **Service Down**
   - Impact: Complete outage possible
   - Action: Restart service, check logs

4. **Database Connections Exhausted**
   - Impact: New requests failing
   - Action: Scale pool, check for leaks

5. **Disk Space < 10%**
   - Impact: System instability
   - Action: Clean logs, expand disk

### Warning Alerts (Monitor & Plan)

1. **Error Rate > 0.5%**
   - Action: Monitor for escalation

2. **Response Time p95 > 500ms**
   - Action: Review slow queries

3. **Cache Hit Rate < 60%**
   - Action: Adjust TTLs, cache warming

4. **Memory Usage > 80%**
   - Action: Monitor, plan scaling

5. **Queue Depth > 1000**
   - Action: Consider scaling workers

## Troubleshooting

### Services Not Starting

```bash
# Check logs
docker-compose -f docker-compose.monitoring.yml logs [service]

# Verify configuration
docker-compose -f docker-compose.monitoring.yml config

# Restart specific service
docker-compose -f docker-compose.monitoring.yml restart [service]
```

### No Metrics in Grafana

1. Check Prometheus targets: http://localhost:9090/targets
2. Verify data source in Grafana (Configuration → Data Sources)
3. Check if application is exposing metrics at `/metrics`

### Alerts Not Firing

1. Verify AlertManager is running: http://localhost:9093
2. Check alert rules in Prometheus: http://localhost:9090/alerts
3. Verify SMTP/Slack/PagerDuty credentials in `.env`
4. Check AlertManager logs:
   ```bash
   docker-compose -f docker-compose.monitoring.yml logs alertmanager
   ```

### High Resource Usage

**Prometheus**:
- Reduce retention time: `--storage.tsdb.retention.time=7d`
- Reduce scrape interval: `scrape_interval: 30s`
- Limit series per job

**Grafana**:
- Reduce dashboard refresh rate
- Limit time range on queries
- Use recording rules for complex queries

## Best Practices

### Metrics

1. **Label Cardinality**: Keep labels low-cardinality
   - ✅ `{method="GET", endpoint="/api/audio"}`
   - ❌ `{user_id="12345"}` (high cardinality)

2. **Naming Convention**:
   - Counter: `_total` suffix (e.g., `http_requests_total`)
   - Gauge: No suffix (e.g., `queue_depth`)
   - Histogram: `_bucket`, `_sum`, `_count` (e.g., `response_time_seconds`)

3. **Units**: Use base units
   - Time: seconds (not ms)
   - Size: bytes (not KB/MB)
   - Percentage: 0-1 (not 0-100)

### Dashboards

1. **Organization**: Group related metrics
2. **Thresholds**: Set meaningful warning/critical levels
3. **Drill-down**: Link to detailed views
4. **Context**: Add descriptions to panels

### Alerting

1. **Severity**: Use appropriate levels
   - Critical: Immediate action required
   - Warning: Monitor and plan

2. **Actionable**: Include runbook links
3. **Deduplication**: Use inhibition rules
4. **Testing**: Test alert flows regularly

## Maintenance

### Daily

- Monitor dashboard for anomalies
- Review critical alerts

### Weekly

- Check disk space for Prometheus data
- Review slow queries in Database dashboard
- Verify backup of alert configurations

### Monthly

- Update exporters and monitoring stack
- Review and tune alert thresholds
- Clean up old data if needed
- Test alert routing and notifications

## Security

### Access Control

- Change default Grafana credentials immediately
- Use strong passwords for all services
- Enable TLS for production (see nginx config)
- Restrict access to monitoring ports

### Secrets Management

- Store sensitive data in `.env` (not committed)
- Use secret management tools (Vault, AWS Secrets Manager)
- Rotate credentials regularly

## Scaling

### Horizontal Scaling

For high-volume environments:

1. **Prometheus Federation**: Split metrics collection
2. **Thanos**: Long-term storage and querying
3. **Cortex**: Multi-tenant Prometheus

### Optimization

1. **Recording Rules**: Pre-compute expensive queries
2. **Remote Write**: Send metrics to long-term storage
3. **Downsampling**: Reduce resolution for old data

## Support

For issues or questions:

- Check logs: `docker-compose logs -f [service]`
- Review documentation: See `DASHBOARD_GUIDE.md`, `ALERTING_GUIDE.md`
- Open an issue on GitHub

## Additional Resources

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [AlertManager Documentation](https://prometheus.io/docs/alerting/latest/alertmanager/)
- [PromQL Basics](https://prometheus.io/docs/prometheus/latest/querying/basics/)

## License

Part of SampleMind AI platform - See main LICENSE file