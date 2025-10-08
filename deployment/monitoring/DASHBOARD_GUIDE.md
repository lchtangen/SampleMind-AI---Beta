# Grafana Dashboard Usage Guide

Comprehensive guide for using and navigating SampleMind AI monitoring dashboards.

## Table of Contents

1. [Dashboard Overview](#dashboard-overview)
2. [System Overview Dashboard](#system-overview-dashboard)
3. [Audio Processing Dashboard](#audio-processing-dashboard)
4. [Database Performance Dashboard](#database-performance-dashboard)
5. [ML Models Dashboard](#ml-models-dashboard)
6. [Common Operations](#common-operations)
7. [Tips & Best Practices](#tips--best-practices)

## Dashboard Overview

### Available Dashboards

| Dashboard | Purpose | Key Metrics | Refresh Rate |
|-----------|---------|-------------|--------------|
| System Overview | Overall system health | Requests, Response times, Errors | 10s |
| Audio Processing | Audio task monitoring | Processing times, Queue depth | 10s |
| Database Performance | DB & cache metrics | Queries, Connections, Cache hits | 10s |
| ML Models | ML inference monitoring | Model performance, GPU usage | 10s |

### Accessing Dashboards

1. Open Grafana: http://localhost:3000
2. Login with credentials (default: admin/admin)
3. Navigate: Home → Dashboards → Browse
4. Select dashboard by name or search

### Dashboard Navigation

- **Time Range**: Top-right corner (default: Last 1 hour)
- **Refresh**: Auto-refresh every 10s (configurable)
- **Zoom**: Click and drag on any graph
- **Panel Actions**: Click panel title → View, Edit, Share
- **Full Screen**: Click panel title → View

## System Overview Dashboard

**UID**: `samplemind-system-overview`

### Purpose
Monitor overall system health, API performance, and infrastructure metrics.

### Panels

#### 1. Request Rate (req/s)

**What it shows**: HTTP requests per second by method and endpoint

**Key insights**:
- Peak traffic times
- Popular endpoints
- Traffic patterns

**Normal values**:
- Steady patterns during business hours
- Spikes during peak usage

**Action required when**:
- Unexpected spikes (potential attack)
- Sudden drops (service issue)
- Sustained high rates approaching capacity

**PromQL**:
```promql
rate(http_requests_total{job="samplemind-api"}[5m])
```

#### 2. Response Times (p50, p95, p99)

**What it shows**: Response time percentiles over time

**Key insights**:
- User experience quality
- Performance degradation
- Outlier identification

**Normal values**:
- p50: < 100ms
- p95: < 500ms (warning at 500ms)
- p99: < 1s (critical at 1s)

**Action required when**:
- p95 consistently > 500ms
- Large gap between p50 and p99 (inconsistent performance)
- Sudden spikes (investigate cause)

**PromQL**:
```promql
histogram_quantile(0.95, 
  sum(rate(http_request_duration_seconds_bucket[5m])) by (le)
)
```

#### 3. Error Rates (%)

**What it shows**: Percentage of failed requests (4xx, 5xx)

**Key insights**:
- Service health
- Client vs server issues
- Error trends

**Normal values**:
- < 0.1% is excellent
- 0.1-0.5% is acceptable
- > 0.5% requires attention

**Action required when**:
- 5xx errors > 0.5% (warning) or > 1% (critical)
- 4xx errors > 20% (potential security issue)
- Sudden error spikes

**PromQL**:
```promql
rate(http_requests_total{status=~"5.."}[5m]) / 
rate(http_requests_total[5m])
```

#### 4. CPU & Memory Usage

**What it shows**: System resource utilization

**Key insights**:
- Resource pressure
- Capacity planning
- Performance bottlenecks

**Normal values**:
- CPU: 20-60% normal load
- Memory: 40-70% normal usage

**Action required when**:
- CPU > 80% sustained (warning)
- Memory > 80% sustained (warning)
- Approaching 95% (critical)

**PromQL**:
```promql
100 * (1 - avg(rate(node_cpu_seconds_total{mode="idle"}[5m])))
```

#### 5. Network I/O

**What it shows**: Network traffic in/out by interface

**Key insights**:
- Network bandwidth usage
- Traffic patterns
- Potential bottlenecks

**Normal values**:
- Varies by workload
- Should correlate with request rate

**Action required when**:
- Approaching network capacity
- Unusual spikes without corresponding requests
- Asymmetric traffic (potential issue)

#### 6. Active Connections

**What it shows**: Current number of active HTTP connections

**Key insights**:
- Load on system
- Connection pooling effectiveness
- Resource allocation

**Normal values**:
- Proportional to request rate
- Stable during normal operations

**Action required when**:
- Continuously growing (connection leaks)
- Sudden drops (service restart/crash)
- Exceeding configured limits

## Audio Processing Dashboard

**UID**: `samplemind-audio-processing`

### Purpose
Monitor audio processing tasks, Celery workers, and queue health.

### Panels

#### 1. Processing Time by Task Type (p95)

**What it shows**: 95th percentile processing time for each audio task

**Task Types**:
- BPM Detection
- Key Detection
- Stem Separation
- Transcription
- Fingerprinting

**Normal values**:
- BPM: < 2s
- Key: < 1s
- Stems: < 30s (varies by file length)
- Transcription: < 15s per minute of audio
- Fingerprinting: < 5s

**Action required when**:
- Times consistently exceeding normal ranges
- Sudden increases (check GPU/CPU)
- Large variance (inconsistent performance)

#### 2. Queue Depth (Celery)

**What it shows**: Number of pending tasks in audio processing queue

**Key insights**:
- Worker capacity vs demand
- Processing backlog
- Need for scaling

**Normal values**:
- < 100: Excellent
- 100-500: Normal
- 500-1000: Monitor closely

**Action required when**:
- > 1000 (warning) - consider scaling
- > 5000 (critical) - immediate scaling needed
- Continuously growing - insufficient capacity

#### 3. Success/Failure Rates

**What it shows**: Successful vs failed task completions over time

**Key insights**:
- Task reliability
- Error patterns
- System health

**Normal values**:
- > 95% success rate
- < 5% failure acceptable

**Action required when**:
- Failure rate > 5%
- Sudden spike in failures
- Consistent failure pattern (investigate root cause)

#### 4. Batch Processing Metrics

**What it shows**: Tasks processed in batches

**Key insights**:
- Batch efficiency
- Throughput optimization
- Resource utilization

**Normal values**:
- Depends on configured batch sizes
- Should show consistent patterns

**Action required when**:
- Batch sizes not matching configuration
- Erratic patterns (resource constraints)

#### 5. Audio File Size Distribution

**What it shows**: Distribution of processed file sizes

**Key insights**:
- Workload characteristics
- Storage requirements
- Processing time correlation

**Use cases**:
- Capacity planning
- Performance optimization
- Cost estimation

#### 6. Processing Throughput (files/min)

**What it shows**: Number of files processed per minute

**Key insights**:
- System capacity
- Performance trends
- Scaling effectiveness

**Normal values**:
- Depends on workload and workers
- Should be stable or growing

**Action required when**:
- Declining trend (performance degradation)
- Not meeting SLA targets
- Capacity insufficient for demand

#### 7. Celery Worker Status

**What it shows**: Active workers and task counts

**Key insights**:
- Worker health
- Task distribution
- Resource allocation

**Normal values**:
- All configured workers active
- Tasks evenly distributed

**Action required when**:
- Worker count below expected
- Uneven task distribution
- No active workers (critical)

## Database Performance Dashboard

**UID**: `samplemind-database-performance`

### Purpose
Monitor MongoDB, Redis, and database-related performance metrics.

### Panels

#### 1. Query Performance - Slow Queries (p95)

**What it shows**: 95th percentile query latency by collection

**Key insights**:
- Database performance
- Query optimization needs
- Index effectiveness

**Normal values**:
- < 50ms: Excellent
- 50-100ms: Good
- 100-200ms: Acceptable

**Action required when**:
- > 200ms (warning) - review queries
- > 500ms (critical) - immediate optimization
- Specific collections slow - check indexes

#### 2. Connection Pool Utilization

**What it shows**: Percentage of database connections in use

**Key insights**:
- Connection pool sizing
- Load on database
- Potential bottlenecks

**Normal values**:
- 30-70%: Healthy
- 70-80%: Monitor

**Action required when**:
- > 80% sustained (warning)
- > 95% (critical) - exhaustion imminent
- Continuously at max (increase pool size)

#### 3. Cache Hit Rates (Redis)

**What it shows**: Percentage of cache hits vs misses

**Key insights**:
- Cache effectiveness
- TTL optimization needs
- Memory efficiency

**Normal values**:
- > 80%: Excellent
- 60-80%: Good
- < 60%: Needs optimization

**Action required when**:
- < 60% (warning)
- Declining trend (investigate)
- Sudden drops (cache flush/issues)

#### 4. Index Efficiency

**What it shows**: Ratio of index usage vs full collection scans

**Key insights**:
- Index effectiveness
- Query optimization
- Performance bottlenecks

**Normal values**:
- > 90%: Excellent
- 70-90%: Good
- < 70%: Review indexes

**Action required when**:
- < 70% (indicates missing indexes)
- Specific queries not using indexes
- Performance degradation

#### 5. MongoDB Operations/sec

**What it shows**: Database operations by type (insert, query, update, delete)

**Key insights**:
- Database load
- Operation patterns
- Capacity planning

**Normal values**:
- Varies by application
- Should follow business patterns

**Action required when**:
- Unusual spikes (investigate cause)
- Sustained high rates (capacity check)
- Imbalanced operations (potential issue)

#### 6. Vector Search Latency

**What it shows**: Performance of vector similarity searches

**Key insights**:
- ML search performance
- Index effectiveness
- Optimization needs

**Normal values**:
- p50: < 50ms
- p95: < 100ms
- p99: < 200ms

**Action required when**:
- > 500ms (investigate)
- Increasing trend (index optimization)
- High variance (resource contention)

## ML Models Dashboard

**UID**: `samplemind-ml-models`

### Purpose
Monitor ML model performance, inference times, and GPU utilization.

### Panels

#### 1. Inference Time per Model (p95)

**What it shows**: Model inference latency by model type

**Models tracked**:
- Demucs (Stem Separation)
- Whisper (Transcription)
- Key Detection
- BPM Detection
- Chromaprint (Fingerprinting)

**Normal values**:
- Varies by model and batch size
- Should be consistent for same inputs

**Action required when**:
- Increasing trends (performance degradation)
- High variance (resource contention)
- Exceeding SLA targets

#### 2. ONNX vs Original Model Usage

**What it shows**: Distribution of optimized vs original model usage

**Key insights**:
- Optimization adoption
- Performance improvements
- Migration progress

**Target**:
- > 80% ONNX usage (optimized)

**Action required when**:
- Low ONNX usage (investigate barriers)
- Performance differences
- Accuracy concerns

#### 3. Model Accuracy Metrics

**What it shows**: Accuracy measurements for each model

**Key insights**:
- Model quality
- Drift detection
- A/B testing results

**Normal values**:
- > 85% accuracy is typical
- Varies by model and use case

**Action required when**:
- Declining accuracy (model drift)
- Below baseline (retraining needed)
- Sudden drops (investigate cause)

#### 4. GPU/CPU Utilization

**What it shows**: Resource usage for ML workloads

**Key insights**:
- Hardware efficiency
- Bottleneck identification
- Capacity planning

**Normal values**:
- GPU: 70-90% during inference
- CPU: 40-60% support tasks

**Action required when**:
- GPU < 50% (underutilized)
- CPU bottleneck (consider GPU acceleration)
- > 95% sustained (scaling needed)

#### 5. Batch Size Optimization

**What it shows**: Inference performance by batch size

**Key insights**:
- Optimal batch configuration
- Throughput vs latency
- Resource efficiency

**Normal values**:
- Larger batches = higher throughput
- Smaller batches = lower latency

**Action required when**:
- Suboptimal batch sizes
- Performance not scaling
- Resource constraints

#### 6. Model Loading Time

**What it shows**: Time to load models into memory

**Key insights**:
- Cold start performance
- Model size impact
- Storage performance

**Normal values**:
- < 10s for most models
- < 30s for large models

**Action required when**:
- > 30s consistently
- Impacting worker startup
- High variance (I/O issues)

## Common Operations

### Changing Time Range

1. Click time picker (top-right)
2. Select from presets or custom range
3. Common ranges:
   - Last 5 minutes: Quick issues
   - Last 1 hour: Recent trends
   - Last 24 hours: Daily patterns
   - Last 7 days: Weekly trends

### Zooming Into Data

1. Click and drag on any graph
2. Selected region zooms in
3. Click "Zoom out" to reset
4. Use time picker for precise ranges

### Comparing Time Periods

1. Click time picker
2. Enable "Compare to"
3. Select comparison period
4. View overlaid data

### Sharing Dashboards

1. Click share icon (top-right)
2. Options:
   - Link: Share URL with time range
   - Snapshot: Static image
   - Export: JSON for import
   - Embed: iframe code

### Creating Annotations

1. Ctrl+Click on graph
2. Add description
3. Tag for filtering
4. Use for marking:
   - Deployments
   - Incidents
   - Configuration changes

### Setting Alert Thresholds

1. Edit panel
2. Alert tab
3. Configure conditions
4. Set notification channels
5. Test alert

### Downloading Data

1. Panel menu → Inspect → Data
2. Choose format (CSV, Excel, JSON)
3. Download for analysis

## Tips & Best Practices

### Performance Optimization

1. **Limit time ranges**: Shorter ranges = faster queries
2. **Use variables**: Filter data efficiently
3. **Reduce refresh rate**: For historical analysis
4. **Disable unnecessary panels**: Focus on relevant data

### Effective Monitoring

1. **Set meaningful thresholds**: Based on actual behavior
2. **Use multiple views**: System → Component → Detail
3. **Correlate metrics**: Find relationships between signals
4. **Track trends**: Not just current values

### Dashboard Customization

1. **Clone existing dashboards**: Customize without affecting originals
2. **Create custom views**: For specific use cases
3. **Use variables**: Make dashboards dynamic
4. **Add documentation**: Panel descriptions help teams

### Troubleshooting Workflow

1. **Start broad**: System Overview
2. **Narrow down**: Identify affected component
3. **Dive deep**: Component-specific dashboard
4. **Correlate**: Check related metrics
5. **Verify fix**: Monitor after changes

### Alert Fatigue Prevention

1. **Tune thresholds**: Reduce false positives
2. **Use inhibition**: Suppress redundant alerts
3. **Group related alerts**: Reduce noise
4. **Regular review**: Adjust as system evolves

### Data Retention

1. **Real-time data**: 15 days in Prometheus
2. **Long-term storage**: Use Thanos/Cortex
3. **Downsampling**: Reduce resolution over time
4. **Export critical data**: For compliance

## Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Search dashboards | `/` |
| Time range | `t` |
| Refresh | `r` |
| Toggle legend | `l` |
| Share | `s` |
| Save | `Ctrl+S` |
| Toggle fullscreen | `f` |
| Close panel | `Esc` |

## Additional Resources

- [Grafana Documentation](https://grafana.com/docs/)
- [PromQL Guide](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [Dashboard Best Practices](https://grafana.com/docs/grafana/latest/best-practices/)

## Support

For dashboard issues or questions:
- Check Grafana logs: `docker-compose logs grafana`
- Review panel queries in edit mode
- Verify data source connection
- Open issue on GitHub