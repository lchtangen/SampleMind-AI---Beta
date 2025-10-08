# Audit Logging System

Comprehensive audit logging system for security event tracking and compliance.

## Features

- **Structured JSON Logging**: All events are logged in a consistent JSON format
- **MongoDB Storage**: Persistent storage with automatic TTL-based retention
- **Searchable Audit Trail**: Query events by type, user, severity, and time range
- **Compliance Reporting**: Export logs to CSV or JSON for audits
- **PII Redaction**: Automatic redaction of sensitive information
- **Prometheus Metrics**: Real-time monitoring of audit events
- **Context Manager**: Automatic logging with exception handling
- **Decorator Support**: Easy function-level audit logging

## Installation

Ensure MongoDB and Prometheus client are installed:

```bash
pip install pymongo prometheus-client
```

## Usage

### Basic Usage

```python
from samplemind.audit import AuditLogger, EventType, Severity

# Initialize logger
audit_logger = AuditLogger(
    mongo_uri="mongodb://localhost:27017",
    database_name="samplemind",
    collection_name="audit_logs",
    retention_days=30,
    enable_pii_redaction=True
)

# Log authentication attempt
audit_logger.log_authentication(
    user_id="user_123",
    success=True,
    ip_address="192.168.1.1",
    user_agent="Mozilla/5.0",
    session_id="session_abc"
)

# Log authorization decision
audit_logger.log_authorization(
    user_id="user_123",
    resource="/api/admin",
    action="access",
    result="denied",
    ip_address="192.168.1.1"
)

# Log file operation
audit_logger.log_file_operation(
    user_id="user_123",
    file_id="file_abc",
    operation="upload",
    result="success"
)
```

### Context Manager

Automatically log operations with exception handling:

```python
with audit_logger.audit_context(
    EventType.FILE_OPERATION,
    user_id="user_123",
    resource="audio.mp3",
    action="upload"
):
    # Your operation here
    upload_file(audio_data)
    # Success/failure automatically logged
```

### Decorator

Add audit logging to functions:

```python
from samplemind.audit import audit_event

@audit_event(EventType.FILE_OPERATION, action="upload")
def upload_file(user_id, file_data, ip_address=None):
    # Function implementation
    return {"status": "success"}

# Automatically logs on function entry/exit
upload_file("user_123", data, ip_address="192.168.1.1")
```

### Searching Events

```python
from datetime import datetime, timedelta

# Search by event type
events = audit_logger.search_events(
    event_type=EventType.AUTHENTICATION,
    limit=100
)

# Search by user and time range
start_time = datetime.utcnow() - timedelta(days=7)
events = audit_logger.search_events(
    user_id="user_123",
    start_time=start_time,
    limit=50
)

# Search by severity
events = audit_logger.search_events(
    severity=Severity.CRITICAL,
    limit=10
)
```

### Compliance Reporting

Export logs for audits:

```python
from datetime import datetime, timedelta

# Export to CSV
start_time = datetime.utcnow() - timedelta(days=30)
audit_logger.export_to_csv(
    filepath="audit_report.csv",
    start_time=start_time
)

# Export to JSON
audit_logger.export_to_json(
    filepath="audit_report.json",
    start_time=start_time
)
```

### Statistics

Get audit log statistics:

```python
stats = audit_logger.get_statistics(
    start_time=datetime.utcnow() - timedelta(days=7)
)

print(f"Total events: {stats['total_events']}")
print(f"Auth failures: {stats['auth_failures']}")
print(f"Security incidents: {stats['security_incidents']}")
```

## Event Types

- `AUTHENTICATION`: Login/logout attempts
- `AUTHORIZATION`: Permission checks
- `API_KEY_USAGE`: API key usage tracking
- `FILE_OPERATION`: File uploads/downloads
- `CONFIG_CHANGE`: Configuration modifications
- `RATE_LIMIT_VIOLATION`: Rate limit exceeded
- `SECURITY_INCIDENT`: Security events
- `PASSWORD_CHANGE`: Password modifications
- `ACCOUNT_LOCKOUT`: Account lockouts
- `PRIVILEGE_ESCALATION`: Role/permission changes

## Severity Levels

- `INFO`: Normal operations
- `WARNING`: Potentially concerning events
- `ERROR`: Error conditions
- `CRITICAL`: Critical security incidents

## PII Redaction

The audit logger automatically redacts:

- Email addresses
- Phone numbers
- Social Security Numbers (SSN)
- Credit card numbers
- IP addresses (partial redaction)

Redaction can be disabled by setting `enable_pii_redaction=False`.

## Log Format

Each event is stored in the following JSON structure:

```json
{
  "event_id": "uuid",
  "timestamp": "2025-01-06T12:00:00Z",
  "event_type": "authentication",
  "severity": "info",
  "user_id": "user_123",
  "ip_address": "192.168.xxx.xxx",
  "user_agent": "Mozilla/5.0...",
  "resource": "/api/login",
  "action": "login",
  "result": "success",
  "metadata": {},
  "session_id": "session_abc",
  "request_id": "req_xyz"
}
```

## Monitoring

Prometheus metrics are automatically exported:

- `audit_events_total`: Total events by type, severity, and result
- `audit_logging_duration_seconds`: Time spent logging events

## Indexes

The following MongoDB indexes are automatically created:

- TTL index on `timestamp` for automatic retention
- Compound indexes for common queries
- Single field indexes on important fields

## Best Practices

1. **Always log security-sensitive operations**
2. **Use appropriate severity levels**
3. **Include sufficient context in metadata**
4. **Enable PII redaction in production**
5. **Monitor audit event metrics**
6. **Regularly review security incidents**
7. **Export logs for compliance audits**

## Testing

Run unit tests:

```bash
pytest tests/unit/test_audit_logger.py -v
```

## Performance

- Asynchronous logging recommended for high-throughput
- MongoDB indexes ensure fast queries
- TTL indexes automatically clean old logs
- PII redaction adds minimal overhead (~1-2ms)

## Security

- All sensitive data is redacted by default
- MongoDB connection should use authentication
- Consider encrypting audit logs at rest
- Restrict access to audit logs
- Regular security reviews recommended