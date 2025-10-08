# Alerting Setup and Runbook Guide

Comprehensive guide for alert configuration, response procedures, and runbooks for SampleMind AI.

## Table of Contents

1. [Alert Overview](#alert-overview)
2. [Alert Severity Levels](#alert-severity-levels)
3. [Critical Alerts & Runbooks](#critical-alerts--runbooks)
4. [Warning Alerts & Runbooks](#warning-alerts--runbooks)
5. [Alert Response Procedures](#alert-response-procedures)
6. [Notification Channels](#notification-channels)
7. [Alert Management](#alert-management)
8. [Testing & Validation](#testing--validation)

## Alert Overview

### Alert Architecture

```
Prometheus → Alert Rules → AlertManager → Notification Channels
     ↓           ↓              ↓                ↓
  Metrics    Evaluation    Routing         Slack/Email/PagerDuty
```

### Alert Configuration Files

- **Critical Rules**: `prometheus/alerts/critical.yml`
- **Warning Rules**: `prometheus/alerts/warning.yml`
- **Routing Config**: `alertmanager/alertmanager.yml`

### Key Concepts

**Alert States**:
- **Inactive**: Condition not met
- **Pending**: Condition met, waiting for `for` duration
- **Firing**: Alert active and sending notifications

**Labels**: Categorize and route alerts
- `severity`: critical, warning
- `component`: api, database, ml, infrastructure
- `team`: backend, devops, ml-ops, security

## Alert Severity Levels

### Critical (P1)

**Characteristics**:
- Immediate response required
- Service degradation or outage
- User impact: High
- Response time: < 15 minutes
- Escalation: PagerDuty + Slack + Email

**Examples**:
- Service completely down
- API error rate > 1%
- Database connections exhausted
- Disk space < 10%

### Warning (P2)

**Characteristics**:
- Attention needed but not urgent
- Potential future issues
- User impact: Low to Medium
- Response time: < 1 hour
- Escalation: Slack + Email

**Examples**:
- Error rate > 0.5%
- Cache hit rate < 60%
- Memory usage > 80%
- Queue depth > 1000

## Critical Alerts & Runbooks

### 1. HighAPIErrorRate

**Trigger**: API error rate > 1% for 2 minutes

**Severity**: Critical

**Impact**: Users experiencing service degradation

**Immediate Actions**:
1. Check Grafana System Overview dashboard
2. Identify failing endpoints:
   ```bash
   # View error logs
   docker-compose logs api | grep "ERROR"
   ```
3. Check recent deployments:
   ```bash
   # Review recent changes
   git log --since="1 hour ago"
   ```
4. Review application logs for stack traces
5. If deployment related, consider rollback

**Investigation**:
- Check database connectivity
- Verify external service dependencies
- Review error patterns by endpoint
- Check for resource constraints

**Resolution**:
- Fix code issue and deploy
- Scale resources if needed
- Rollback if deployment caused issue

**Prevention**:
- Improve testing coverage
- Add canary deployments
- Implement circuit breakers

---

### 2. HighAPIResponseTime

**Trigger**: API p95 response time > 1s for 3 minutes

**Severity**: Critical

**Impact**: Severe user experience degradation

**Immediate Actions**:
1. Check Database Performance dashboard
2. Identify slow queries:
   ```bash
   # MongoDB slow query log
   docker-compose exec mongodb mongo --eval "db.setProfilingLevel(2)"
   docker-compose exec mongodb mongo --eval "db.system.profile.find().limit(10).sort({ts:-1})"
   ```
3. Check Redis cache status
4. Review CPU/Memory on System Overview

**Investigation**:
- Identify slow endpoints
- Review database query plans
- Check for missing indexes
- Verify cache effectiveness
- Check for resource contention

**Resolution**:
- Add database indexes
- Optimize slow queries
- Scale resources vertically/horizontally
- Implement query caching
- Review and optimize code

**Prevention**:
- Query performance testing
- Index optimization
- Caching strategy review

---

### 3. ServiceDown

**Trigger**: Service unreachable for 1 minute

**Severity**: Critical

**Impact**: Complete service unavailability

**Immediate Actions**:
1. Identify affected service:
   ```bash
   # Check service status
   docker-compose ps
   
   # Check service health
   curl -f http://localhost:8000/health || echo "Service down"
   ```
2. Check service logs:
   ```bash
   docker-compose logs --tail=100 [service-name]
   ```
3. Verify network connectivity
4. Check resource availability (disk, memory)

**Investigation**:
- Review crash logs
- Check OOM killer logs:
   ```bash
   dmesg | grep -i "out of memory"
   ```
- Verify configuration changes
- Check dependency services

**Resolution**:
- Restart service if crashed:
   ```bash
   docker-compose restart [service-name]
   ```
- Fix configuration issues
- Scale resources if OOM
- Fix code bug if crash loop

**Prevention**:
- Implement health checks
- Add resource limits
- Improve error handling
- Add crash recovery mechanisms

---

### 4. DatabaseConnectionsExhausted

**Trigger**: Connection pool > 95% for 2 minutes

**Severity**: Critical

**Impact**: New requests will fail

**Immediate Actions**:
1. Check Database Performance dashboard
2. Identify connection leaks:
   ```bash
   # MongoDB connections
   docker-compose exec mongodb mongo --eval "db.serverStatus().connections"
   ```
3. Review active connections:
   ```bash
   # Application connections
   docker-compose logs api | grep "connection"
   ```

**Investigation**:
- Check for connection leaks in code
- Review long-running queries
- Verify connection timeout settings
- Check connection pool configuration

**Resolution**:
- Increase connection pool size (temporary):
   ```python
   # In database config
   max_pool_size=100  # Increase from default
   ```
- Fix connection leaks in code
- Implement connection retry logic
- Add connection timeout handling

**Prevention**:
- Use connection context managers
- Implement connection pooling properly
- Monitor connection patterns
- Add connection leak detection

---

### 5. DiskSpaceCritical

**Trigger**: Disk space < 10% for 5 minutes

**Severity**: Critical

**Impact**: System instability, crashes

**Immediate Actions**:
1. Check disk usage:
   ```bash
   df -h
   du -sh /* | sort -hr | head -10
   ```
2. Identify large files:
   ```bash
   find / -type f -size +1G -exec ls -lh {} \;
   ```
3. Clean up immediately:
   ```bash
   # Remove old logs
   find /var/log -type f -name "*.log" -mtime +7 -delete
   
   # Clean Docker
   docker system prune -a -f
   
   # Clean Prometheus data (if safe)
   # rm -rf /prometheus/old-data
   ```

**Investigation**:
- Review log rotation policies
- Check for runaway processes
- Identify data growth patterns
- Verify backup processes

**Resolution**:
- Implement log rotation
- Archive old data
- Expand disk capacity
- Optimize data retention

**Prevention**:
- Monitor disk growth trends
- Implement automated cleanup
- Set retention policies
- Alert at 20% threshold

---

### 6. CeleryWorkersDown

**Trigger**: No active Celery workers for 2 minutes

**Severity**: Critical

**Impact**: Background processing stopped

**Immediate Actions**:
1. Check worker status:
   ```bash
   docker-compose ps | grep celery
   celery -A samplemind.celery inspect active
   ```
2. View worker logs:
   ```bash
   docker-compose logs --tail=100 celery-worker
   ```
3. Check broker connectivity:
   ```bash
   docker-compose logs redis
   ```

**Investigation**:
- Review worker crash logs
- Check Redis/RabbitMQ status
- Verify configuration
- Check for OOM issues

**Resolution**:
- Restart workers:
   ```bash
   docker-compose restart celery-worker
   ```
- Fix broker connection issues
- Scale workers if needed
- Fix code bugs causing crashes

**Prevention**:
- Implement worker health checks
- Add auto-restart policies
- Monitor worker memory usage
- Implement graceful shutdown

## Warning Alerts & Runbooks

### 1. ElevatedAPIErrorRate

**Trigger**: API error rate > 0.5% for 5 minutes

**Severity**: Warning

**Impact**: Degraded experience for some users

**Actions**:
1. Monitor trends - check if increasing
2. Review error patterns in logs
3. Check if specific endpoints affected
4. Investigate if near critical threshold

**Resolution**:
- Fix identified issues during business hours
- Monitor for escalation to critical
- Plan preventive measures

---

### 2. LowCacheHitRate

**Trigger**: Redis cache hit rate < 60% for 10 minutes

**Severity**: Warning

**Impact**: Increased database load, slower responses

**Actions**:
1. Review cache configuration:
   ```bash
   docker-compose exec redis redis-cli INFO stats | grep hits
   ```
2. Check cache TTL settings
3. Identify frequently missed keys
4. Review cache warming strategies

**Resolution**:
- Adjust TTL values
- Implement cache warming
- Review caching strategy
- Consider cache expansion

---

### 3. HighMemoryUsage

**Trigger**: Memory usage > 80% for 10 minutes

**Severity**: Warning

**Impact**: Risk of performance degradation

**Actions**:
1. Identify memory-intensive processes:
   ```bash
   ps aux --sort=-%mem | head -10
   docker stats --no-stream
   ```
2. Check for memory leaks
3. Review recent deployments
4. Monitor for escalation

**Resolution**:
- Fix memory leaks
- Optimize memory usage
- Scale vertically if needed
- Implement memory limits

---

### 4. HighQueueDepth

**Trigger**: Queue depth > 1000 for 15 minutes

**Severity**: Warning

**Impact**: Processing delays

**Actions**:
1. Check queue metrics:
   ```bash
   celery -A samplemind.celery inspect stats
   ```
2. Review worker capacity
3. Identify task bottlenecks
4. Monitor queue growth rate

**Resolution**:
- Scale workers horizontally
- Optimize slow tasks
- Implement task prioritization
- Review task scheduling

## Alert Response Procedures

### Critical Alert Response (P1)

**Response SLA**: 15 minutes

1. **Acknowledge** (< 5 min)
   - Acknowledge in PagerDuty/Slack
   - Join war room (if configured)

2. **Assess** (< 5 min)
   - Check dashboards
   - Identify scope and impact
   - Determine if customer-facing

3. **Mitigate** (< 15 min)
   - Implement immediate fix
   - Communicate status
   - Document actions taken

4. **Resolve**
   - Apply permanent fix
   - Monitor for recurrence
   - Update runbooks

5. **Post-Mortem** (within 48 hours)
   - Root cause analysis
   - Action items
   - Prevention measures

### Warning Alert Response (P2)

**Response SLA**: 1 hour

1. **Review** (< 15 min)
   - Check alert details
   - Review dashboards
   - Assess urgency

2. **Investigate** (< 30 min)
   - Identify root cause
   - Check for patterns
   - Determine impact

3. **Plan** (< 1 hour)
   - Create action plan
   - Schedule fix
   - Document findings

4. **Resolve**
   - Implement fix
   - Monitor results
   - Update documentation

## Notification Channels

### Slack Configuration

**Channels**:
- `#alerts-critical`: Critical alerts only
- `#alerts-warning`: Warning alerts
- `#team-backend`: Backend-specific alerts
- `#team-ml-ops`: ML/GPU alerts
- `#team-devops`: Infrastructure alerts
- `#team-security`: Security alerts

**Configuration**:
```yaml
slack_configs:
  - channel: '#alerts-critical'
    username: 'SampleMind AlertManager'
    icon_emoji: ':fire:'
```

### Email Configuration

**Recipients**:
- `oncall@samplemind.ai`: Critical alerts
- `devops@samplemind.ai`: All alerts
- `[team]@samplemind.ai`: Team-specific alerts

**Configuration**:
```yaml
email_configs:
  - to: 'oncall@samplemind.ai'
    headers:
      Priority: 'urgent'
```

### PagerDuty Configuration

**Service Keys**:
- Production: Critical alerts only
- Staging: High-severity alerts

**Escalation Policy**:
1. On-call engineer (immediate)
2. Team lead (15 min)
3. Engineering manager (30 min)

## Alert Management

### Viewing Active Alerts

**Prometheus**:
```
http://localhost:9090/alerts
```

**AlertManager**:
```
http://localhost:9093/#/alerts
```

**Grafana**:
Navigate to Alerting → Alert Rules

### Silencing Alerts

**Use cases**:
- Planned maintenance
- Known issues being addressed
- False positives being fixed

**via AlertManager UI**:
1. Navigate to http://localhost:9093/#/silences
2. Click "New Silence"
3. Set matchers (e.g., `alertname=HighAPIErrorRate`)
4. Set duration
5. Add comment explaining reason

**via CLI**:
```bash
# Create silence
amtool silence add \
  alertname="HighAPIErrorRate" \
  --duration=1h \
  --comment="Maintenance window"

# List silences
amtool silence query

# Expire silence
amtool silence expire [silence-id]
```

### Modifying Alert Thresholds

1. Edit alert rules:
   ```yaml
   # prometheus/alerts/critical.yml
   expr: |
     rate(http_requests_total{status=~"5.."}[5m]) > 0.02  # Changed from 0.01
   ```

2. Reload Prometheus:
   ```bash
   curl -X POST http://localhost:9090/-/reload
   ```

3. Verify changes:
   ```bash
   promtool check rules prometheus/alerts/*.yml
   ```

### Adding New Alerts

1. **Create rule**:
   ```yaml
   - alert: NewAlertName
     expr: your_metric > threshold
     for: 5m
     labels:
       severity: warning
       component: api
     annotations:
       summary: "Brief description"
       description: "Detailed description with {{ $value }}"
       runbook: "Link to runbook"
   ```

2. **Validate**:
   ```bash
   promtool check rules prometheus/alerts/warning.yml
   ```

3. **Reload**:
   ```bash
   docker-compose exec prometheus kill -HUP 1
   ```

4. **Test**: Trigger condition and verify notification

## Testing & Validation

### Testing Alert Rules

**1. Validate syntax**:
```bash
promtool check rules prometheus/alerts/*.yml
```

**2. Test expression**:
```bash
# In Prometheus UI
# Navigate to http://localhost:9090/graph
# Enter alert expression and check results
```

**3. Unit test alerts**:
```bash
promtool test rules tests/alerts_test.yml
```

### Testing Notifications

**1. Send test alert**:
```bash
# Using amtool
amtool alert add \
  alertname="TestAlert" \
  severity="critical" \
  instance="test" \
  --annotation=summary="Test alert" \
  --generator-url="http://localhost:9093"
```

**2. Verify delivery**:
- Check Slack channels
- Check email inbox
- Check PagerDuty incidents

**3. Test routing**:
- Create test alerts with different labels
- Verify correct channel delivery
- Check inhibition rules work

### Alert Runbook Testing

**Quarterly testing schedule**:
1. Test critical alert procedures
2. Verify runbooks are up-to-date
3. Practice incident response
4. Update documentation
5. Train team members

**Testing checklist**:
- [ ] All runbooks accessible
- [ ] Commands work as documented
- [ ] Contact information current
- [ ] Escalation paths clear
- [ ] Recovery procedures tested

## Best Practices

### Alert Design

1. **Actionable**: Every alert should require action
2. **Meaningful**: Alert on symptoms, not causes
3. **Timely**: Alert before customer impact
4. **Accurate**: Minimize false positives
5. **Clear**: Provide context and next steps

### Alert Fatigue Prevention

1. **Tune thresholds** based on actual behavior
2. **Use inhibition** to reduce noise
3. **Group related alerts** together
4. **Regular review** and cleanup
5. **Silence known issues** being addressed

### Documentation

1. **Keep runbooks updated** after incidents
2. **Document all changes** to alerts
3. **Share learnings** from incidents
4. **Maintain contact lists**
5. **Version control** all configurations

### Continuous Improvement

1. **Review alerts** after each incident
2. **Measure MTTA/MTTR** (Mean Time To Acknowledge/Repair)
3. **Conduct post-mortems** for P1 incidents
4. **Update thresholds** based on trends
5. **Automate** remediation where possible

## Escalation Matrix

| Severity | First Response | Escalation (15 min) | Escalation (30 min) |
|----------|---------------|---------------------|---------------------|
| Critical | On-call Engineer | Team Lead | Engineering Manager |
| Warning | Team Channel | (Business hours only) | - |

## Contact Information

- **On-call**: oncall@samplemind.ai
- **DevOps Team**: devops@samplemind.ai
- **ML Ops Team**: ml-ops@samplemind.ai
- **Security Team**: security@samplemind.ai
- **Engineering Manager**: [Contact]

## Additional Resources

- [Prometheus Alerting Docs](https://prometheus.io/docs/alerting/latest/overview/)
- [AlertManager Configuration](https://prometheus.io/docs/alerting/latest/configuration/)
- [Grafana Alerting](https://grafana.com/docs/grafana/latest/alerting/)
- [SRE Book - Monitoring](https://sre.google/sre-book/monitoring-distributed-systems/)

---

**Last Updated**: 2025-10-06  
**Version**: 1.0  
**Maintained by**: DevOps Team