# 🚨 SampleMind AI - Incident Response Playbook

**Version:** 1.0  
**Last Updated:** October 6, 2025  
**Status:** Active

---

## 📋 Table of Contents

- [Overview](#overview)
- [Incident Classification](#incident-classification)
- [Response Procedures](#response-procedures)
- [Escalation Matrix](#escalation-matrix)
- [Communication Templates](#communication-templates)
- [Common Incident Scenarios](#common-incident-scenarios)
- [Recovery Procedures](#recovery-procedures)
- [Post-Incident Review](#post-incident-review)

---

## 🎯 Overview

This playbook provides structured procedures for responding to production incidents affecting SampleMind AI services. All team members should be familiar with these procedures.

### Incident Response Goals

1. **Minimize Impact:** Reduce user impact and restore service quickly
2. **Clear Communication:** Keep stakeholders informed
3. **Root Cause Analysis:** Understand why incidents occur
4. **Continuous Improvement:** Learn and prevent recurrence

### Key Principles

- **Customer First:** Prioritize service restoration over investigation
- **Clear Ownership:** Every incident has a designated incident commander
- **Blameless Culture:** Focus on systems, not individuals
- **Document Everything:** Maintain detailed incident logs

---

## 🏷️ Incident Classification

### Severity Levels

| Severity | Description | Response Time | Examples |
|----------|-------------|---------------|----------|
| **SEV1** | Critical - Service down or severely degraded | < 5 min | Complete outage, data loss, security breach |
| **SEV2** | Major - Significant feature degradation | < 15 min | API errors >5%, slow response times, partial outage |
| **SEV3** | Minor - Limited impact to non-critical features | < 1 hour | Single feature issue, cosmetic bugs, monitoring alerts |

### SEV1 - Critical Incidents

**Characteristics:**
- Complete service outage
- Data loss or corruption
- Security breach
- Revenue-impacting issues
- Legal/compliance violations

**Response Requirements:**
- Immediate response (< 5 minutes)
- Incident commander assigned immediately
- Executive notification within 15 minutes
- Hourly status updates
- All hands on deck if needed

**Examples:**
- API completely unreachable
- Database corruption
- Security breach detected
- Payment system failure
- Data leak

### SEV2 - Major Incidents

**Characteristics:**
- Significant feature degradation
- High error rates (> 5%)
- Performance severely impacted
- Multiple users affected

**Response Requirements:**
- Response within 15 minutes
- Incident commander assigned
- Team lead notification
- Updates every 2 hours
- Dedicated team assigned

**Examples:**
- API error rate > 5%
- Audio processing failures
- Slow response times (> 2s)
- Database connection issues
- Cache failures

### SEV3 - Minor Incidents

**Characteristics:**
- Limited user impact
- Single feature affected
- Degraded non-critical functionality
- Monitoring alerts without service impact

**Response Requirements:**
- Response within 1 hour
- Can be handled during business hours
- Standard ticket tracking
- Update at resolution

**Examples:**
- Single endpoint intermittent errors
- UI cosmetic issues
- Non-critical feature bug
- Warning-level alerts
- Performance degradation in off-peak

---

## 🔧 Response Procedures

### SEV1 Response Procedure

#### Phase 1: Detection & Initial Response (0-5 minutes)

**1. Incident Detection:**
```
□ Alert received (PagerDuty/Monitoring)
□ User report via support
□ Team member discovers issue
```

**2. Immediate Actions:**
```bash
# 1. Acknowledge alert
# In PagerDuty: Click "Acknowledge"

# 2. Quick health check
curl https://samplemind.ai/api/v1/health
kubectl get pods -n samplemind-production

# 3. Post to #incident-response
"🚨 SEV1: [Brief description]
Status: Investigating
IC: [Your name]
Started: [Time]"

# 4. Create incident channel
# Slack: /incident sev1 [description]
```

**3. Assign Incident Commander (IC):**
- First responder becomes IC unless escalated
- IC coordinates all response efforts
- IC maintains communication

#### Phase 2: Investigation & Mitigation (5-30 minutes)

**1. Gather Information:**
```bash
# Check recent changes
kubectl rollout history deployment/backend -n samplemind-production

# Check logs
kubectl logs --since=30m deployment/backend -n samplemind-production | grep ERROR

# Check metrics
# Open Grafana → System Overview dashboard

# Check alerts
# Open Prometheus → Alerts page
```

**2. Immediate Mitigation:**

```bash
# Option A: Rollback recent deployment
kubectl rollout undo deployment/backend -n samplemind-production

# Option B: Scale up if resource issue
kubectl scale deployment backend --replicas=10 -n samplemind-production

# Option C: Restart if application hung
kubectl rollout restart deployment/backend -n samplemind-production

# Option D: Enable maintenance mode
kubectl apply -f maintenance-mode.yaml
```

**3. Escalate if needed:**
```
□ Can't identify root cause in 15 minutes → Escalate
□ Need specialist (DB, security, etc.) → Page specialist
□ Executive awareness needed → Notify CTO
```

#### Phase 3: Service Restoration (30-60 minutes)

**1. Implement Fix:**
```bash
# Deploy hotfix
kubectl set image deployment/backend backend=samplemind/backend:hotfix -n samplemind-production

# Or apply configuration change
kubectl edit configmap samplemind-config -n samplemind-production
kubectl rollout restart deployment/backend -n samplemind-production
```

**2. Verify Resolution:**
```bash
# Health check
curl https://samplemind.ai/api/v1/health

# Check error rates
# Grafana → System Overview → Error Rate panel

# Test critical flows
curl -X POST https://samplemind.ai/api/v1/audio/upload \
  -H "Authorization: Bearer $TEST_TOKEN" \
  -F "file=@test.wav"
```

**3. Monitor Stability:**
```
□ Watch metrics for 15 minutes
□ No new errors appearing
□ Response times normal
□ User reports decreasing
```

#### Phase 4: Communication & Closure

**1. Internal Communication:**
```
"✅ SEV1 RESOLVED: [Brief description]
Duration: [Start time] - [End time]
Root Cause: [Brief explanation]
Resolution: [What was done]
Follow-up: PIR scheduled for [date/time]"
```

**2. Customer Communication:**
- Post status update
- Email affected customers
- Update status page

**3. Documentation:**
```
□ Update incident ticket with timeline
□ Save all logs and screenshots
□ Document commands executed
□ Schedule PIR (Post-Incident Review)
```

### SEV2 Response Procedure

Similar structure but with relaxed timelines:

1. **Detection & Response:** < 15 minutes
2. **Investigation:** 15-60 minutes
3. **Mitigation:** 1-4 hours
4. **Resolution:** 4-8 hours

**Key Differences:**
- More time for investigation
- Can wait for next business hours if detected off-hours
- Bi-hourly updates instead of hourly
- Smaller response team

### SEV3 Response Procedure

**Characteristics:**
- Can be handled during business hours
- Standard ticket workflow
- Single update at resolution

**Procedure:**
1. Create ticket in issue tracker
2. Assign to appropriate team
3. Fix within SLA (24-48 hours)
4. Verify and close

---

## 📞 Escalation Matrix

### On-Call Rotation

| Role | Primary | Secondary | Escalation Point |
|------|---------|-----------|------------------|
| **First Responder** | On-call engineer | Backup on-call | Can't diagnose in 15 min |
| **Incident Commander** | Engineering Lead | Senior Engineer | Need additional resources |
| **Backend Specialist** | Backend Lead | Senior Backend Dev | Backend-specific issues |
| **Database Specialist** | DBA | DevOps Lead | Database issues |
| **Security Specialist** | Security Lead | CTO | Security incidents |
| **Executive** | CTO | CEO | Business-critical, data loss |

### Escalation Triggers

**Escalate to IC when:**
- Can't diagnose root cause in 15 minutes
- Incident scope expanding
- Need coordination of multiple teams
- Public/customer-facing incident

**Escalate to Executive when:**
- SEV1 lasting > 1 hour
- Data loss or security breach
- Legal/compliance implications
- Media attention likely
- Revenue impact > $10K

### Contact Methods

**Priority Order:**
1. PagerDuty (SEV1)
2. Phone call (SEV1/SEV2)
3. Slack mention (SEV2/SEV3)
4. Email (SEV3)

### Escalation Script

```
"Hi [Name], escalating [SEV1/2/3] incident.

Brief: [One sentence description]
Impact: [Users/systems affected]
Duration: [Started at X time, ongoing Y minutes]
Actions taken: [What we've tried]
Need: [Specific help needed]

Incident channel: #incident-[number]
IC: [Name]"
```

---

## 💬 Communication Templates

### Internal Alert (Slack)

**Initial Alert:**
```
🚨 [SEV1/SEV2/SEV3]: [Brief Description]

Status: INVESTIGATING
Started: [Time]
IC: @[username]
Impact: [Affected systems/users]

Incident Channel: #incident-[number]
Updates: Every [frequency]
```

**Status Update:**
```
📊 [SEV1/SEV2] UPDATE - [Time]

Current Status: [Investigating/Mitigating/Resolved]
Progress: [What we've learned/done]
Next Steps: [What's being tried next]
ETA: [Estimated resolution time]

IC: @[username]
Channel: #incident-[number]
```

**Resolution:**
```
✅ [SEV1/SEV2] RESOLVED - [Time]

Duration: [X hours Y minutes]
Root Cause: [Brief explanation]
Resolution: [What fixed it]
Impact: [Final scope]
Follow-up: PIR scheduled [date/time]

IC: @[username]
```

### Customer Communication

**Status Page Update:**
```
🔴 Investigating - [Service Name]
We are investigating reports of [issue]. 
Updates will be provided as we learn more.
Posted: [Time UTC]
```

```
🟡 Identified - [Service Name]
We have identified the issue as [brief cause].
Engineers are working on a fix.
Updated: [Time UTC]
```

```
🟢 Resolved - [Service Name]  
The issue has been resolved.
Service is fully operational.
Root cause: [Brief explanation]
Resolved: [Time UTC]
```

**Email to Affected Customers:**
```
Subject: [Resolved] Brief Service Disruption - [Date]

Dear SampleMind User,

We experienced a service disruption today between [Start Time] 
and [End Time] UTC affecting [specific features].

What happened:
[Brief explanation in customer-friendly terms]

What we did:
[How we resolved it]

What we're doing to prevent recurrence:
[Prevention measures]

We apologize for any inconvenience. If you have questions,
please contact support@samplemind.ai.

Best regards,
SampleMind AI Team
```

### Executive Brief

```
INCIDENT EXECUTIVE BRIEF

Severity: [SEV1/SEV2]
Status: [Investigating/Resolved]
Duration: [Start] - [End/Ongoing]

IMPACT:
- Users affected: [Number/percentage]
- Features impacted: [List]
- Revenue impact: [Estimate]

ROOT CAUSE:
[Technical explanation + business context]

RESOLUTION:
[What was done]

PREVENTION:
[Action items to prevent recurrence]

FOLLOW-UP:
PIR scheduled: [Date/Time]
Action items owner: [Name]

IC: [Name]
Report prepared: [Time]
```

---

## 🔥 Common Incident Scenarios

### Scenario 1: Complete API Outage

**Symptoms:**
- All API requests returning 502/503
- Health check failing
- All backend pods down or crash-looping

**Runbook:**

```bash
# 1. Check pod status
kubectl get pods -n samplemind-production
# Look for: CrashLoopBackOff, Error, ImagePullBackOff

# 2. Check recent events
kubectl get events -n samplemind-production --sort-by='.lastTimestamp' | head -20

# 3. Check logs
kubectl logs deployment/backend -n samplemind-production --tail=100

# Common causes and fixes:

# A. Configuration issue - Rollback
kubectl rollout undo deployment/backend -n samplemind-production

# B. Resource exhaustion
kubectl describe nodes | grep -A5 "Allocated resources"
# If nodes full, scale down other services or add nodes

# C. Database connection failure
kubectl logs deployment/backend -n samplemind-production | grep "database"
# Check MongoDB connectivity
kubectl exec -it mongodb-0 -n samplemind-production -- mongosh --eval "db.runCommand({ ping: 1 })"

# D. Image pull failure
kubectl describe pod <pod-name> -n samplemind-production | grep "Image"
# Fix: Re-push image or update image tag

# 4. Verify recovery
curl https://samplemind.ai/api/v1/health
# Should return 200 with {"status":"healthy"}

# 5. Monitor for 15 minutes
watch -n 10 'curl -s https://samplemind.ai/api/v1/health | jq'
```

**Prevention:**
- Always test deployments in staging first
- Use gradual rollouts (canary/blue-green)
- Set up pre-deployment validation
- Monitor deployment metrics closely

### Scenario 2: Database Connection Exhaustion

**Symptoms:**
- "Too many connections" errors
- Slow API responses
- Sporadic timeouts

**Runbook:**

```bash
# 1. Check connection count
kubectl exec -it mongodb-0 -n samplemind-production -- \
  mongosh -u admin -p password --eval "db.serverStatus().connections"

# Current: X, Available: Y
# If Current near Available, connections exhausted

# 2. Kill idle connections (MongoDB)
kubectl exec -it mongodb-0 -n samplemind-production -- \
  mongosh -u admin -p password --eval "
    db.currentOp({'secs_running': {$gte: 60}}).inprog.forEach(
      function(op) { db.killOp(op.opid) }
    )
  "

# 3. Scale up connection pool (temporary)
kubectl set env deployment/backend \
  MONGODB_MAX_POOL_SIZE=100 \
  -n samplemind-production

# 4. Restart application
kubectl rollout restart deployment/backend -n samplemind-production

# 5. Investigate connection leaks
kubectl logs deployment/backend -n samplemind-production | \
  grep -i "connection" | tail -100

# 6. Check for connection leak in code
# Look for missing conn.close() or improper context managers
```

**Prevention:**
- Set connection timeouts
- Use connection pooling properly
- Monitor connection metrics
- Regular code reviews for connection handling

### Scenario 3: High Error Rate (> 5%)

**Symptoms:**
- Error rate alert firing
- Specific endpoint(s) failing
- User reports of errors

**Runbook:**

```bash
# 1. Identify failing endpoints
kubectl logs deployment/backend -n samplemind-production --since=15m | \
  grep ERROR | cut -d'"' -f4 | sort | uniq -c | sort -rn | head -10

# 2. Check recent deployments
kubectl rollout history deployment/backend -n samplemind-production

# If recent deployment, rollback:
kubectl rollout undo deployment/backend -n samplemind-production

# 3. Check for external service failures
# Test AI APIs
curl -X POST https://api.openai.com/v1/chat/completions \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-3.5-turbo","messages":[{"role":"user","content":"test"}]}'

# 4. Check database health
kubectl exec -it mongodb-0 -n samplemind-production -- \
  mongosh -u admin -p password --eval "db.serverStatus()" | grep "ok"

# 5. Investigate specific errors
kubectl logs deployment/backend -n samplemind-production --since=15m | \
  grep "ERROR" | head -20

# 6. If external API issue, enable circuit breaker
kubectl set env deployment/backend \
  ENABLE_AI_FALLBACK=true \
  -n samplemind-production
```

**Prevention:**
- Implement circuit breakers for external APIs
- Add request validation
- Increase test coverage
- Set up error tracking (Sentry)

### Scenario 4: Performance Degradation

**Symptoms:**
- Response times > 1s
- Timeouts increasing
- CPU/Memory high

**Runbook:**

```bash
# 1. Check resource usage
kubectl top pods -n samplemind-production
kubectl top nodes

# 2. Scale up if needed
kubectl scale deployment backend --replicas=8 -n samplemind-production

# 3. Check for slow queries
kubectl exec -it mongodb-0 -n samplemind-production -- \
  mongosh -u admin -p password --eval "
    db.setProfilingLevel(2);
    db.system.profile.find({millis:{$gt:100}}).sort({ts:-1}).limit(10);
  "

# 4. Check cache hit rate
kubectl exec -it redis-0 -n samplemind-production -- \
  redis-cli -a password INFO stats | grep keyspace_hits

# Low hit rate? Warm cache:
# (Run cache warming script if available)

# 5. Check for memory leaks
kubectl top pods -n samplemind-production --sort-by=memory

# If pod memory constantly growing:
kubectl delete pod <high-memory-pod> -n samplemind-production

# 6. Enable query caching
kubectl set env deployment/backend \
  ENABLE_QUERY_CACHE=true \
  -n samplemind-production

# 7. Check for infinite loops or blocking operations
kubectl exec -it deployment/backend -n samplemind-production -- \
  python -c "
    import sys
    import traceback
    # Print stack trace of running process
  "
```

**Prevention:**
- Set up performance baselines
- Regular performance testing
- Monitor query performance
- Optimize N+1 queries
- Implement caching strategically

### Scenario 5: Celery Queue Backup

**Symptoms:**
- Queue depth > 1000
- Processing delays
- Tasks timing out

**Runbook:**

```bash
# 1. Check queue depth
kubectl exec -it redis-0 -n samplemind-production -- \
  redis-cli -a password LLEN celery

# 2. Check worker status
kubectl logs deployment/celery-worker -n samplemind-production --tail=50

# 3. Scale up workers
kubectl scale deployment celery-worker --replicas=5 -n samplemind-production

# 4. Check for stuck tasks
kubectl exec -it deployment/celery-worker -n samplemind-production -- \
  celery -A src.samplemind.core.tasks.celery_app inspect active

# 5. Revoke stuck tasks
kubectl exec -it deployment/celery-worker -n samplemind-production -- \
  celery -A src.samplemind.core.tasks.celery_app control revoke <task-id>

# 6. If queue growing uncontrollably, pause queue
kubectl exec -it redis-0 -n samplemind-production -- \
  redis-cli -a password RENAME celery celery_paused

# Fix issue, then restore:
kubectl exec -it redis-0 -n samplemind-production -- \
  redis-cli -a password RENAME celery_paused celery

# 7. Monitor queue drain
watch -n 10 'kubectl exec -it redis-0 -n samplemind-production -- redis-cli -a password LLEN celery'
```

**Prevention:**
- Set task timeouts
- Implement task retries with exponential backoff
- Monitor queue depth proactively
- Scale workers based on queue depth

### Scenario 6: Security Incident

**Symptoms:**
- Unauthorized access detected
- DDoS attack
- Data breach suspected
- Unusual traffic patterns

**CRITICAL: Security incidents require immediate escalation**

**Runbook:**

```bash
# 1. IMMEDIATELY notify security team
# PagerDuty: Page security-lead
# Slack: @security-team in #incident-response

# 2. Preserve evidence - DO NOT delete logs
# Copy logs before taking any action
kubectl logs deployment/backend -n samplemind-production > incident-logs-$(date +%Y%m%d_%H%M%S).txt

# 3. If active breach, isolate affected systems
kubectl apply -f network-policies/lockdown.yaml

# Or completely isolate
kubectl delete svc backend-service -n samplemind-production

# 4. Review recent access logs
kubectl logs deployment/backend -n samplemind-production | \
  grep -i "auth\|login\|access" | tail -500

# 5. Check for unauthorized changes
kubectl get events -n samplemind-production --sort-by='.lastTimestamp'

# 6. If DDoS, enable rate limiting
kubectl apply -f ingress-rate-limit-strict.yaml

# 7. Block malicious IPs
kubectl apply -f network-policies/block-ips.yaml

# 8. Force password reset for affected accounts (if applicable)
# Via admin API or direct database update

# 9. Wait for security team guidance before proceeding
```

**Prevention:**
- Regular security audits
- Penetration testing
- Keep all systems patched
- Monitor for unusual patterns
- Implement WAF rules
- Use rate limiting
- Enable audit logging

---

## 🔄 Recovery Procedures

### Application Recovery

**Full Application Restore:**

```bash
# 1. Restore from last known good state
kubectl apply -f backups/last-known-good/

# 2. Restore database
mongorestore --uri="$MONGODB_URL" --drop ./backup/latest/

# 3. Restore Redis
kubectl cp ./backup/redis/dump.rdb redis-0:/data/dump.rdb -n samplemind-production
kubectl delete pod redis-0 -n samplemind-production

# 4. Clear caches
kubectl exec -it redis-0 -n samplemind-production -- \
  redis-cli -a password FLUSHALL

# 5. Restart all services
kubectl rollout restart deployment --all -n samplemind-production

# 6. Verify health
./scripts/health_check.sh
```

### Data Recovery

**Recover Deleted Data:**

```bash
# 1. Check if in backup
mongodump --uri="$MONGODB_URL" \
  --collection=audio_files \
  --query='{"_id": ObjectId("...")}'

# 2. Restore specific collection
mongorestore --uri="$MONGODB_URL" \
  --collection=audio_files \
  --drop \
  ./backup/audio_files.bson

# 3. Verify restoration
mongosh "$MONGODB_URL" --eval '
  db.audio_files.findOne({_id: ObjectId("...")})
'
```

### Point-in-Time Recovery

```bash
# 1. Identify recovery point
# Example: Restore to 2 hours ago

# 2. Find appropriate backup
aws s3 ls s3://samplemind-backups/mongodb/ | grep "$(date -d '2 hours ago' +%Y%m%d)"

# 3. Download backup
aws s3 cp s3://samplemind-backups/mongodb/backup_YYYYMMDD_HHMMSS/ ./restore/ --recursive

# 4. Restore
mongorestore --uri="$MONGODB_URL" --dir=./restore/ --drop

# 5. Verify data
```

---

## 📊 Post-Incident Review (PIR)

### PIR Schedule

Conduct PIR within 48 hours of resolution:
- SEV1: Within 24 hours
- SEV2: Within 48 hours
- SEV3: Optional, if valuable learnings

### PIR Meeting Agenda

**Duration:** 60 minutes  
**Attendees:** IC, responders, engineering leads, affected teams

**Agenda:**
1. **Incident Overview** (5 min)
   - What happened
   - Timeline
   - Impact

2. **Timeline Review** (15 min)
   - Detection to resolution
   - Key decision points
   - Parallel activities

3. **What Went Well** (10 min)
   - Effective actions
   - Good decisions
   - Helpful tools/processes

4. **What Didn't Go Well** (15 min)
   - Challenges faced
   - Delays encountered
   - Communication issues

5. **Root Cause Analysis** (10 min)
   - Technical root cause
   - Contributing factors
   - Why did protections fail?

6. **Action Items** (5 min)
   - Prevention measures
   - Tooling improvements
   - Process updates
   - Owners and deadlines

### PIR Document Template

```markdown
# Post-Incident Review: [Incident Title]

**Date:** [Incident date]
**Severity:** [SEV1/SEV2/SEV3]
**Duration:** [Start] - [End]
**IC:** [Name]

## Summary
[One paragraph overview]

## Impact
- Users affected: [Number]
- Duration: [Time]
- Features impacted: [List]
- Revenue impact: [Estimate]

## Timeline
| Time (UTC) | Event |
|------------|-------|
| HH:MM | [Event description] |
| HH:MM | [Event description] |

## Root Cause
[Technical explanation of what caused the incident]

## Contributing Factors
- [Factor 1]
- [Factor 2]

## Resolution
[How the incident was resolved]

## What Went Well
- [Thing 1]
- [Thing 2]

## What Didn't Go Well
- [Challenge 1]
- [Challenge 2]

## Action Items
| Action | Owner | Due Date | Status |
|--------|-------|----------|--------|
| [Action 1] | [Name] | [Date] | Open |
| [Action 2] | [Name] | [Date] | Open |

## Lessons Learned
- [Lesson 1]
- [Lesson 2]
```

### Action Item Tracking

**Create GitHub Issues:**
```bash
gh issue create \
  --title "PIR Action: [Description]" \
  --label "post-incident-review,priority:high" \
  --body "From PIR: [Link to PIR doc]
  
  Action: [Detailed description]
  Context: [Why this matters]
  
  Acceptance Criteria:
  - [ ] [Criterion 1]
  - [ ] [Criterion 2]"
```

### Follow-up

- Review action items in weekly engineering meeting
- Track completion in project board
- Schedule re-review if actions not completed within 30 days

---

## 📞 Important Contacts

### Emergency Contacts

| Role | Name | Phone | Email | PagerDuty |
|------|------|-------|-------|-----------|
| On-Call Engineer | Rotating | - | oncall@samplemind.ai | @oncall |
| Engineering Lead | [Name] | +1-555-0101 | eng-lead@samplemind.ai | @eng-lead |
| DevOps Lead | [Name] | +1-555-0102 | devops@samplemind.ai | @devops-lead |
| DBA | [Name] | +1-555-0103 | dba@samplemind.ai | @dba |
| Security Lead | [Name] | +1-555-0104 | security@samplemind.ai | @security-lead |
| CTO | [Name] | +1-555-0105 | cto@samplemind.ai | @cto |

### External Contacts

| Service | Contact | URL |
|---------|---------|-----|
| AWS Support | Enterprise Support | https://console.aws.amazon.com/support |
| MongoDB Atlas | Support Portal | https://support.mongodb.com |
| Let's Encrypt | Community Forum | https://community.letsencrypt.org |

---

## 📚 Related Documentation

- [`DEPLOYMENT_GUIDE.md`](DEPLOYMENT_GUIDE.md:1) - Deployment procedures
- [`OPERATIONS_MANUAL.md`](OPERATIONS_MANUAL.md:1) - Day-to-day operations
- [`monitoring/ALERTING_GUIDE.md`](../monitoring/ALERTING_GUIDE.md:1) - Alert runbooks
- [`docs/ARCHITECTURE.md`](ARCHITECTURE.md:1) - System architecture

---

## 📝 Document History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2025-10-06 | Initial release | DevOps Team |

---

**Document Owner:** Engineering Leadership  
**Review Schedule:** Quarterly (or after major incidents)  
**Last Reviewed:** October 6, 2025

**Remember: Stay calm, communicate clearly, and focus on resolution first, investigation second.**