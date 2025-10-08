"""
Audit Logging System
Comprehensive logging for security events

This module provides structured audit logging with MongoDB storage,
searchable audit trails, compliance reporting, and monitoring integration.
"""

import csv
import json
import logging
import re
from contextlib import contextmanager
from datetime import datetime, timedelta
from enum import Enum
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Union
from uuid import uuid4

from prometheus_client import Counter, Histogram
from pymongo import ASCENDING, DESCENDING, MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

# Prometheus metrics
audit_events_total = Counter(
    "audit_events_total",
    "Total number of audit events logged",
    ["event_type", "severity", "result"],
)

audit_logging_duration = Histogram(
    "audit_logging_duration_seconds",
    "Time spent logging audit events",
    ["event_type"],
)


class EventType(str, Enum):
    """Audit event types"""

    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    API_KEY_USAGE = "api_key_usage"
    FILE_OPERATION = "file_operation"
    CONFIG_CHANGE = "config_change"
    RATE_LIMIT_VIOLATION = "rate_limit_violation"
    SECURITY_INCIDENT = "security_incident"
    PASSWORD_CHANGE = "password_change"
    ACCOUNT_LOCKOUT = "account_lockout"
    PRIVILEGE_ESCALATION = "privilege_escalation"


class Severity(str, Enum):
    """Event severity levels"""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AuditEvent:
    """Represents a single audit event"""

    def __init__(
        self,
        event_type: EventType,
        severity: Severity,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        resource: Optional[str] = None,
        action: Optional[str] = None,
        result: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
        request_id: Optional[str] = None,
    ):
        self.event_id = str(uuid4())
        self.timestamp = datetime.utcnow().isoformat() + "Z"
        self.event_type = event_type
        self.severity = severity
        self.user_id = user_id
        self.ip_address = ip_address
        self.user_agent = user_agent
        self.resource = resource
        self.action = action
        self.result = result
        self.metadata = metadata or {}
        self.session_id = session_id
        self.request_id = request_id

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary"""
        return {
            "event_id": self.event_id,
            "timestamp": self.timestamp,
            "event_type": self.event_type.value,
            "severity": self.severity.value,
            "user_id": self.user_id,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "resource": self.resource,
            "action": self.action,
            "result": self.result,
            "metadata": self.metadata,
            "session_id": self.session_id,
            "request_id": self.request_id,
        }

    def to_json(self) -> str:
        """Convert event to JSON string"""
        return json.dumps(self.to_dict(), indent=2)


class PIIRedactor:
    """Handles PII redaction in audit logs"""

    # Common PII patterns
    EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")
    PHONE_PATTERN = re.compile(r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b")
    SSN_PATTERN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
    CREDIT_CARD_PATTERN = re.compile(r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b")
    IP_ADDRESS_PATTERN = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")

    @classmethod
    def redact_email(cls, text: str) -> str:
        """Redact email addresses"""
        return cls.EMAIL_PATTERN.sub("[EMAIL_REDACTED]", text)

    @classmethod
    def redact_phone(cls, text: str) -> str:
        """Redact phone numbers"""
        return cls.PHONE_PATTERN.sub("[PHONE_REDACTED]", text)

    @classmethod
    def redact_ssn(cls, text: str) -> str:
        """Redact social security numbers"""
        return cls.SSN_PATTERN.sub("[SSN_REDACTED]", text)

    @classmethod
    def redact_credit_card(cls, text: str) -> str:
        """Redact credit card numbers"""
        return cls.CREDIT_CARD_PATTERN.sub("[CARD_REDACTED]", text)

    @classmethod
    def redact_ip_partial(cls, ip: str) -> str:
        """Partially redact IP address (keep first two octets)"""
        if not ip:
            return ip
        parts = ip.split(".")
        if len(parts) == 4:
            return f"{parts[0]}.{parts[1]}.xxx.xxx"
        return ip

    @classmethod
    def redact_all_pii(cls, text: str) -> str:
        """Redact all common PII patterns"""
        text = cls.redact_email(text)
        text = cls.redact_phone(text)
        text = cls.redact_ssn(text)
        text = cls.redact_credit_card(text)
        return text

    @classmethod
    def redact_dict(cls, data: Dict[str, Any], fields_to_redact: List[str]) -> Dict[str, Any]:
        """Redact specific fields in a dictionary"""
        redacted_data = data.copy()
        for field in fields_to_redact:
            if field in redacted_data:
                if isinstance(redacted_data[field], str):
                    redacted_data[field] = cls.redact_all_pii(redacted_data[field])
                else:
                    redacted_data[field] = "[REDACTED]"
        return redacted_data


class AuditLogger:
    """
    Comprehensive audit logging system with MongoDB storage,
    searchable trails, and compliance reporting.
    """

    def __init__(
        self,
        mongo_uri: str,
        database_name: str = "samplemind",
        collection_name: str = "audit_logs",
        retention_days: int = 30,
        enable_pii_redaction: bool = True,
    ):
        """
        Initialize audit logger

        Args:
            mongo_uri: MongoDB connection URI
            database_name: Database name
            collection_name: Collection name for audit logs
            retention_days: Number of days to retain logs (TTL)
            enable_pii_redaction: Whether to enable PII redaction
        """
        self.client: MongoClient = MongoClient(mongo_uri)
        self.db: Database = self.client[database_name]
        self.collection: Collection = self.db[collection_name]
        self.retention_days = retention_days
        self.enable_pii_redaction = enable_pii_redaction
        self.logger = logging.getLogger(__name__)

        # Create indexes
        self._create_indexes()

    def _create_indexes(self):
        """Create MongoDB indexes for efficient querying"""
        try:
            # TTL index for automatic log expiration
            self.collection.create_index(
                "timestamp", expireAfterSeconds=self.retention_days * 24 * 60 * 60
            )

            # Compound indexes for common queries
            self.collection.create_index([("event_type", ASCENDING), ("timestamp", DESCENDING)])
            self.collection.create_index([("user_id", ASCENDING), ("timestamp", DESCENDING)])
            self.collection.create_index([("severity", ASCENDING), ("timestamp", DESCENDING)])
            self.collection.create_index([("ip_address", ASCENDING), ("timestamp", DESCENDING)])

            # Single field indexes
            self.collection.create_index("event_id", unique=True)
            self.collection.create_index("session_id")
            self.collection.create_index("request_id")
            self.collection.create_index("resource")
            self.collection.create_index("result")

            self.logger.info("Audit log indexes created successfully")
        except Exception as e:
            self.logger.error(f"Error creating audit log indexes: {e}")

    def _redact_sensitive_data(self, event: AuditEvent) -> AuditEvent:
        """Redact PII from event data"""
        if not self.enable_pii_redaction:
            return event

        # Redact user agent
        if event.user_agent:
            event.user_agent = PIIRedactor.redact_all_pii(event.user_agent)

        # Partially redact IP address
        if event.ip_address:
            event.ip_address = PIIRedactor.redact_ip_partial(event.ip_address)

        # Redact metadata fields
        if event.metadata:
            sensitive_fields = ["email", "phone", "ssn", "credit_card", "password"]
            event.metadata = PIIRedactor.redact_dict(event.metadata, sensitive_fields)

        return event

    def log_event(self, event: AuditEvent) -> bool:
        """
        Log an audit event to MongoDB

        Args:
            event: AuditEvent to log

        Returns:
            True if successful, False otherwise
        """
        try:
            with audit_logging_duration.labels(event_type=event.event_type.value).time():
                # Redact sensitive data
                event = self._redact_sensitive_data(event)

                # Insert into MongoDB
                self.collection.insert_one(event.to_dict())

                # Update Prometheus metrics
                audit_events_total.labels(
                    event_type=event.event_type.value,
                    severity=event.severity.value,
                    result=event.result or "unknown",
                ).inc()

                # Log to application logger
                log_level = {
                    Severity.INFO: logging.INFO,
                    Severity.WARNING: logging.WARNING,
                    Severity.ERROR: logging.ERROR,
                    Severity.CRITICAL: logging.CRITICAL,
                }.get(event.severity, logging.INFO)

                self.logger.log(log_level, f"Audit event: {event.to_json()}")

                return True

        except Exception as e:
            self.logger.error(f"Error logging audit event: {e}")
            return False

    def log_authentication(
        self,
        user_id: str,
        success: bool,
        ip_address: str,
        user_agent: str,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Log authentication attempt"""
        event = AuditEvent(
            event_type=EventType.AUTHENTICATION,
            severity=Severity.WARNING if not success else Severity.INFO,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            action="login",
            result="success" if success else "failure",
            session_id=session_id,
            metadata=metadata or {},
        )
        return self.log_event(event)

    def log_authorization(
        self,
        user_id: str,
        resource: str,
        action: str,
        result: str,
        ip_address: Optional[str] = None,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Log authorization decision"""
        event = AuditEvent(
            event_type=EventType.AUTHORIZATION,
            severity=Severity.WARNING if result == "denied" else Severity.INFO,
            user_id=user_id,
            ip_address=ip_address,
            resource=resource,
            action=action,
            result=result,
            session_id=session_id,
            metadata=metadata or {},
        )
        return self.log_event(event)

    def log_api_key_usage(
        self,
        key_prefix: str,
        endpoint: str,
        ip_address: str,
        result: str = "success",
        request_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Log API key usage"""
        event = AuditEvent(
            event_type=EventType.API_KEY_USAGE,
            severity=Severity.INFO,
            ip_address=ip_address,
            resource=endpoint,
            action="api_call",
            result=result,
            request_id=request_id,
            metadata={"key_prefix": key_prefix, **(metadata or {})},
        )
        return self.log_event(event)

    def log_file_operation(
        self,
        user_id: str,
        file_id: str,
        operation: str,
        result: str = "success",
        ip_address: Optional[str] = None,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Log file upload/download/delete operation"""
        event = AuditEvent(
            event_type=EventType.FILE_OPERATION,
            severity=Severity.INFO,
            user_id=user_id,
            ip_address=ip_address,
            resource=file_id,
            action=operation,
            result=result,
            session_id=session_id,
            metadata=metadata or {},
        )
        return self.log_event(event)

    def log_config_change(
        self,
        user_id: str,
        setting: str,
        old_value: Any,
        new_value: Any,
        ip_address: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> bool:
        """Log configuration change"""
        event = AuditEvent(
            event_type=EventType.CONFIG_CHANGE,
            severity=Severity.WARNING,
            user_id=user_id,
            ip_address=ip_address,
            resource=setting,
            action="update",
            result="success",
            session_id=session_id,
            metadata={"old_value": str(old_value), "new_value": str(new_value)},
        )
        return self.log_event(event)

    def log_rate_limit_violation(
        self,
        ip_address: str,
        endpoint: str,
        limit_exceeded: str,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Log rate limit violation"""
        event = AuditEvent(
            event_type=EventType.RATE_LIMIT_VIOLATION,
            severity=Severity.WARNING,
            user_id=user_id,
            ip_address=ip_address,
            resource=endpoint,
            action="rate_limit",
            result="denied",
            metadata={"limit_exceeded": limit_exceeded, **(metadata or {})},
        )
        return self.log_event(event)

    def log_security_incident(
        self,
        incident_type: str,
        severity: Severity,
        details: str,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Log security incident"""
        event = AuditEvent(
            event_type=EventType.SECURITY_INCIDENT,
            severity=severity,
            user_id=user_id,
            ip_address=ip_address,
            resource=incident_type,
            action="security_event",
            result="detected",
            metadata={"details": details, **(metadata or {})},
        )
        return self.log_event(event)

    def log_password_change(
        self,
        user_id: str,
        ip_address: str,
        success: bool = True,
        session_id: Optional[str] = None,
    ) -> bool:
        """Log password change"""
        event = AuditEvent(
            event_type=EventType.PASSWORD_CHANGE,
            severity=Severity.WARNING,
            user_id=user_id,
            ip_address=ip_address,
            action="password_change",
            result="success" if success else "failure",
            session_id=session_id,
        )
        return self.log_event(event)

    def log_account_lockout(
        self, user_id: str, reason: str, ip_address: Optional[str] = None
    ) -> bool:
        """Log account lockout"""
        event = AuditEvent(
            event_type=EventType.ACCOUNT_LOCKOUT,
            severity=Severity.ERROR,
            user_id=user_id,
            ip_address=ip_address,
            action="lockout",
            result="locked",
            metadata={"reason": reason},
        )
        return self.log_event(event)

    def log_privilege_escalation(
        self,
        user_id: str,
        from_role: str,
        to_role: str,
        ip_address: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> bool:
        """Log privilege escalation attempt"""
        event = AuditEvent(
            event_type=EventType.PRIVILEGE_ESCALATION,
            severity=Severity.CRITICAL,
            user_id=user_id,
            ip_address=ip_address,
            action="privilege_escalation",
            result="detected",
            session_id=session_id,
            metadata={"from_role": from_role, "to_role": to_role},
        )
        return self.log_event(event)

    def search_events(
        self,
        event_type: Optional[EventType] = None,
        user_id: Optional[str] = None,
        severity: Optional[Severity] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Search audit events with filters

        Args:
            event_type: Filter by event type
            user_id: Filter by user ID
            severity: Filter by severity
            start_time: Start of time range
            end_time: End of time range
            limit: Maximum number of results

        Returns:
            List of matching audit events
        """
        query = {}

        if event_type:
            query["event_type"] = event_type.value
        if user_id:
            query["user_id"] = user_id
        if severity:
            query["severity"] = severity.value
        if start_time or end_time:
            query["timestamp"] = {}
            if start_time:
                query["timestamp"]["$gte"] = start_time.isoformat() + "Z"
            if end_time:
                query["timestamp"]["$lte"] = end_time.isoformat() + "Z"

        try:
            results = list(
                self.collection.find(query).sort("timestamp", DESCENDING).limit(limit)
            )
            # Remove MongoDB _id field
            for result in results:
                result.pop("_id", None)
            return results
        except Exception as e:
            self.logger.error(f"Error searching audit events: {e}")
            return []

    def export_to_csv(
        self,
        filepath: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> bool:
        """
        Export audit logs to CSV for compliance reporting

        Args:
            filepath: Path to output CSV file
            start_time: Start of time range
            end_time: End of time range

        Returns:
            True if successful, False otherwise
        """
        try:
            events = self.search_events(start_time=start_time, end_time=end_time, limit=10000)

            if not events:
                self.logger.warning("No events to export")
                return False

            # CSV headers
            fieldnames = [
                "event_id",
                "timestamp",
                "event_type",
                "severity",
                "user_id",
                "ip_address",
                "resource",
                "action",
                "result",
                "session_id",
                "request_id",
            ]

            with open(filepath, "w", newline="") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

                for event in events:
                    # Extract only the fields we want for CSV
                    row = {field: event.get(field, "") for field in fieldnames}
                    writer.writerow(row)

            self.logger.info(f"Exported {len(events)} events to {filepath}")
            return True

        except Exception as e:
            self.logger.error(f"Error exporting to CSV: {e}")
            return False

    def export_to_json(
        self,
        filepath: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> bool:
        """
        Export audit logs to JSON for compliance reporting

        Args:
            filepath: Path to output JSON file
            start_time: Start of time range
            end_time: End of time range

        Returns:
            True if successful, False otherwise
        """
        try:
            events = self.search_events(start_time=start_time, end_time=end_time, limit=10000)

            if not events:
                self.logger.warning("No events to export")
                return False

            with open(filepath, "w") as jsonfile:
                json.dump(events, jsonfile, indent=2)

            self.logger.info(f"Exported {len(events)} events to {filepath}")
            return True

        except Exception as e:
            self.logger.error(f"Error exporting to JSON: {e}")
            return False

    def get_statistics(
        self, start_time: Optional[datetime] = None, end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get audit log statistics for analysis

        Args:
            start_time: Start of time range
            end_time: End of time range

        Returns:
            Dictionary with statistics
        """
        query = {}
        if start_time or end_time:
            query["timestamp"] = {}
            if start_time:
                query["timestamp"]["$gte"] = start_time.isoformat() + "Z"
            if end_time:
                query["timestamp"]["$lte"] = end_time.isoformat() + "Z"

        try:
            # Total events
            total_events = self.collection.count_documents(query)

            # Events by type
            events_by_type = {}
            for event_type in EventType:
                type_query = {**query, "event_type": event_type.value}
                events_by_type[event_type.value] = self.collection.count_documents(type_query)

            # Events by severity
            events_by_severity = {}
            for severity in Severity:
                severity_query = {**query, "severity": severity.value}
                events_by_severity[severity.value] = self.collection.count_documents(
                    severity_query
                )

            # Failed authentication attempts
            auth_failures = self.collection.count_documents(
                {**query, "event_type": EventType.AUTHENTICATION.value, "result": "failure"}
            )

            # Rate limit violations
            rate_limit_violations = self.collection.count_documents(
                {**query, "event_type": EventType.RATE_LIMIT_VIOLATION.value}
            )

            # Security incidents
            security_incidents = self.collection.count_documents(
                {**query, "event_type": EventType.SECURITY_INCIDENT.value}
            )

            return {
                "total_events": total_events,
                "events_by_type": events_by_type,
                "events_by_severity": events_by_severity,
                "auth_failures": auth_failures,
                "rate_limit_violations": rate_limit_violations,
                "security_incidents": security_incidents,
                "time_range": {
                    "start": start_time.isoformat() if start_time else None,
                    "end": end_time.isoformat() if end_time else None,
                },
            }

        except Exception as e:
            self.logger.error(f"Error getting statistics: {e}")
            return {}

    @contextmanager
    def audit_context(
        self,
        event_type: EventType,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        resource: Optional[str] = None,
        action: Optional[str] = None,
        session_id: Optional[str] = None,
    ):
        """
        Context manager for automatic audit logging

        Usage:
            with audit_logger.audit_context(
                EventType.FILE_OPERATION,
                user_id="user_123",
                resource="file.mp3",
                action="upload"
            ):
                # Perform operation
                pass
        """
        start_time = datetime.utcnow()
        success = True
        error_msg = None

        try:
            yield
        except Exception as e:
            success = False
            error_msg = str(e)
            raise
        finally:
            # Log the event
            duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000

            event = AuditEvent(
                event_type=event_type,
                severity=Severity.ERROR if not success else Severity.INFO,
                user_id=user_id,
                ip_address=ip_address,
                resource=resource,
                action=action,
                result="success" if success else "failure",
                session_id=session_id,
                metadata={
                    "duration_ms": duration_ms,
                    "error": error_msg if error_msg else None,
                },
            )
            self.log_event(event)

    def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            self.logger.info("Audit logger MongoDB connection closed")


def audit_event(
    event_type: EventType,
    severity: Severity = Severity.INFO,
    resource: Optional[str] = None,
    action: Optional[str] = None,
):
    """
    Decorator for automatic audit logging

    Usage:
        @audit_event(EventType.FILE_OPERATION, action="upload")
        def upload_file(user_id, file_data):
            # Function implementation
            pass
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Extract common parameters
            user_id = kwargs.get("user_id")
            ip_address = kwargs.get("ip_address")
            session_id = kwargs.get("session_id")

            start_time = datetime.utcnow()
            success = True
            error_msg = None

            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                error_msg = str(e)
                raise
            finally:
                # Log audit event
                duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000

                # This assumes audit_logger is available in the module scope
                # In practice, you'd pass it or use dependency injection
                event = AuditEvent(
                    event_type=event_type,
                    severity=Severity.ERROR if not success else severity,
                    user_id=user_id,
                    ip_address=ip_address,
                    resource=resource or func.__name__,
                    action=action or func.__name__,
                    result="success" if success else "failure",
                    session_id=session_id,
                    metadata={
                        "function": func.__name__,
                        "duration_ms": duration_ms,
                        "error": error_msg if error_msg else None,
                    },
                )

                # Log to application logger
                logging.getLogger(__name__).info(f"Audit event: {event.to_json()}")

        return wrapper

    return decorator