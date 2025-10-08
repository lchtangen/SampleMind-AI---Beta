"""
Unit Tests for Audit Logger
Comprehensive testing of audit logging functionality
"""

import csv
import json
import os
import tempfile
from datetime import datetime, timedelta
from unittest.mock import MagicMock, Mock, patch

import pytest
from pymongo.collection import Collection
from pymongo.database import Database

from src.samplemind.audit.audit_logger import (
    AuditEvent,
    AuditLogger,
    EventType,
    PIIRedactor,
    Severity,
    audit_event,
)


@pytest.fixture
def mock_mongo_client():
    """Mock MongoDB client"""
    with patch("src.samplemind.audit.audit_logger.MongoClient") as mock_client:
        mock_db = MagicMock(spec=Database)
        mock_collection = MagicMock(spec=Collection)
        mock_client.return_value.__getitem__.return_value = mock_db
        mock_db.__getitem__.return_value = mock_collection
        yield mock_client, mock_db, mock_collection


@pytest.fixture
def audit_logger(mock_mongo_client):
    """Create AuditLogger instance with mocked MongoDB"""
    mock_client, mock_db, mock_collection = mock_mongo_client
    logger = AuditLogger(
        mongo_uri="mongodb://localhost:27017",
        database_name="test_db",
        collection_name="test_audit",
        retention_days=30,
        enable_pii_redaction=True,
    )
    return logger


class TestAuditEvent:
    """Test AuditEvent class"""

    def test_create_audit_event(self):
        """Test creating an audit event"""
        event = AuditEvent(
            event_type=EventType.AUTHENTICATION,
            severity=Severity.INFO,
            user_id="user_123",
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            resource="/api/login",
            action="login",
            result="success",
        )

        assert event.event_type == EventType.AUTHENTICATION
        assert event.severity == Severity.INFO
        assert event.user_id == "user_123"
        assert event.ip_address == "192.168.1.1"
        assert event.result == "success"
        assert event.event_id is not None
        assert event.timestamp is not None

    def test_event_to_dict(self):
        """Test converting event to dictionary"""
        event = AuditEvent(
            event_type=EventType.AUTHENTICATION,
            severity=Severity.INFO,
            user_id="user_123",
        )

        event_dict = event.to_dict()

        assert isinstance(event_dict, dict)
        assert event_dict["event_type"] == "authentication"
        assert event_dict["severity"] == "info"
        assert event_dict["user_id"] == "user_123"
        assert "event_id" in event_dict
        assert "timestamp" in event_dict

    def test_event_to_json(self):
        """Test converting event to JSON"""
        event = AuditEvent(
            event_type=EventType.AUTHENTICATION,
            severity=Severity.INFO,
            user_id="user_123",
        )

        json_str = event.to_json()

        assert isinstance(json_str, str)
        parsed = json.loads(json_str)
        assert parsed["event_type"] == "authentication"
        assert parsed["user_id"] == "user_123"

    def test_event_with_metadata(self):
        """Test event with metadata"""
        metadata = {"login_method": "password", "failed_attempts": 0}
        event = AuditEvent(
            event_type=EventType.AUTHENTICATION,
            severity=Severity.INFO,
            user_id="user_123",
            metadata=metadata,
        )

        assert event.metadata == metadata
        event_dict = event.to_dict()
        assert event_dict["metadata"] == metadata


class TestPIIRedactor:
    """Test PII redaction functionality"""

    def test_redact_email(self):
        """Test email redaction"""
        text = "Contact me at john.doe@example.com for details"
        redacted = PIIRedactor.redact_email(text)
        assert "[EMAIL_REDACTED]" in redacted
        assert "john.doe@example.com" not in redacted

    def test_redact_phone(self):
        """Test phone number redaction"""
        text = "Call me at 555-123-4567"
        redacted = PIIRedactor.redact_phone(text)
        assert "[PHONE_REDACTED]" in redacted
        assert "555-123-4567" not in redacted

    def test_redact_ssn(self):
        """Test SSN redaction"""
        text = "SSN: 123-45-6789"
        redacted = PIIRedactor.redact_ssn(text)
        assert "[SSN_REDACTED]" in redacted
        assert "123-45-6789" not in redacted

    def test_redact_credit_card(self):
        """Test credit card redaction"""
        text = "Card: 1234-5678-9012-3456"
        redacted = PIIRedactor.redact_credit_card(text)
        assert "[CARD_REDACTED]" in redacted
        assert "1234-5678-9012-3456" not in redacted

    def test_redact_ip_partial(self):
        """Test partial IP redaction"""
        ip = "192.168.1.100"
        redacted = PIIRedactor.redact_ip_partial(ip)
        assert redacted == "192.168.xxx.xxx"
        assert "192.168" in redacted
        assert "1.100" not in redacted

    def test_redact_all_pii(self):
        """Test redacting all PII patterns"""
        text = "Email: john@example.com, Phone: 555-123-4567, SSN: 123-45-6789"
        redacted = PIIRedactor.redact_all_pii(text)
        assert "[EMAIL_REDACTED]" in redacted
        assert "[PHONE_REDACTED]" in redacted
        assert "[SSN_REDACTED]" in redacted
        assert "john@example.com" not in redacted

    def test_redact_dict(self):
        """Test dictionary field redaction"""
        data = {
            "username": "john_doe",
            "email": "john@example.com",
            "phone": "555-123-4567",
            "age": 30,
        }
        fields_to_redact = ["email", "phone"]
        redacted = PIIRedactor.redact_dict(data, fields_to_redact)

        assert redacted["username"] == "john_doe"
        assert redacted["age"] == 30
        assert "[EMAIL_REDACTED]" in redacted["email"]
        assert "[PHONE_REDACTED]" in redacted["phone"]


class TestAuditLogger:
    """Test AuditLogger class"""

    def test_init_creates_indexes(self, audit_logger):
        """Test that initialization creates indexes"""
        # Verify create_index was called
        assert audit_logger.collection.create_index.called

    def test_log_event_success(self, audit_logger):
        """Test logging an event successfully"""
        audit_logger.collection.insert_one.return_value = Mock()

        event = AuditEvent(
            event_type=EventType.AUTHENTICATION,
            severity=Severity.INFO,
            user_id="user_123",
        )

        result = audit_logger.log_event(event)

        assert result is True
        assert audit_logger.collection.insert_one.called

    def test_log_event_with_pii_redaction(self, audit_logger):
        """Test that PII is redacted when logging"""
        audit_logger.collection.insert_one.return_value = Mock()

        event = AuditEvent(
            event_type=EventType.AUTHENTICATION,
            severity=Severity.INFO,
            user_id="user_123",
            ip_address="192.168.1.100",
            user_agent="Mozilla/5.0 with email@example.com",
            metadata={"email": "user@example.com"},
        )

        audit_logger.log_event(event)

        # Verify insert_one was called
        call_args = audit_logger.collection.insert_one.call_args
        logged_data = call_args[0][0]

        # Check IP was partially redacted
        assert "xxx" in logged_data["ip_address"]
        # Check email in metadata was redacted
        assert "[EMAIL_REDACTED]" in logged_data["metadata"]["email"]

    def test_log_event_error_handling(self, audit_logger):
        """Test error handling when logging fails"""
        audit_logger.collection.insert_one.side_effect = Exception("Database error")

        event = AuditEvent(
            event_type=EventType.AUTHENTICATION,
            severity=Severity.INFO,
            user_id="user_123",
        )

        result = audit_logger.log_event(event)

        assert result is False

    def test_log_authentication_success(self, audit_logger):
        """Test logging successful authentication"""
        audit_logger.collection.insert_one.return_value = Mock()

        result = audit_logger.log_authentication(
            user_id="user_123",
            success=True,
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            session_id="session_abc",
        )

        assert result is True
        call_args = audit_logger.collection.insert_one.call_args[0][0]
        assert call_args["event_type"] == "authentication"
        assert call_args["result"] == "success"
        assert call_args["severity"] == "info"

    def test_log_authentication_failure(self, audit_logger):
        """Test logging failed authentication"""
        audit_logger.collection.insert_one.return_value = Mock()

        result = audit_logger.log_authentication(
            user_id="user_123",
            success=False,
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
        )

        assert result is True
        call_args = audit_logger.collection.insert_one.call_args[0][0]
        assert call_args["result"] == "failure"
        assert call_args["severity"] == "warning"

    def test_log_authorization(self, audit_logger):
        """Test logging authorization decision"""
        audit_logger.collection.insert_one.return_value = Mock()

        result = audit_logger.log_authorization(
            user_id="user_123",
            resource="/api/admin",
            action="access",
            result="denied",
            ip_address="192.168.1.1",
        )

        assert result is True
        call_args = audit_logger.collection.insert_one.call_args[0][0]
        assert call_args["event_type"] == "authorization"
        assert call_args["result"] == "denied"
        assert call_args["severity"] == "warning"

    def test_log_api_key_usage(self, audit_logger):
        """Test logging API key usage"""
        audit_logger.collection.insert_one.return_value = Mock()

        result = audit_logger.log_api_key_usage(
            key_prefix="sk_test_",
            endpoint="/api/v1/analyze",
            ip_address="192.168.1.1",
            result="success",
        )

        assert result is True
        call_args = audit_logger.collection.insert_one.call_args[0][0]
        assert call_args["event_type"] == "api_key_usage"
        assert call_args["metadata"]["key_prefix"] == "sk_test_"

    def test_log_file_operation(self, audit_logger):
        """Test logging file operations"""
        audit_logger.collection.insert_one.return_value = Mock()

        result = audit_logger.log_file_operation(
            user_id="user_123",
            file_id="file_abc",
            operation="upload",
            result="success",
            ip_address="192.168.1.1",
        )

        assert result is True
        call_args = audit_logger.collection.insert_one.call_args[0][0]
        assert call_args["event_type"] == "file_operation"
        assert call_args["action"] == "upload"

    def test_log_config_change(self, audit_logger):
        """Test logging configuration changes"""
        audit_logger.collection.insert_one.return_value = Mock()

        result = audit_logger.log_config_change(
            user_id="admin_123",
            setting="max_upload_size",
            old_value="100MB",
            new_value="200MB",
            ip_address="192.168.1.1",
        )

        assert result is True
        call_args = audit_logger.collection.insert_one.call_args[0][0]
        assert call_args["event_type"] == "config_change"
        assert call_args["metadata"]["old_value"] == "100MB"
        assert call_args["metadata"]["new_value"] == "200MB"

    def test_log_rate_limit_violation(self, audit_logger):
        """Test logging rate limit violations"""
        audit_logger.collection.insert_one.return_value = Mock()

        result = audit_logger.log_rate_limit_violation(
            ip_address="192.168.1.1",
            endpoint="/api/v1/analyze",
            limit_exceeded="10 requests per minute",
            user_id="user_123",
        )

        assert result is True
        call_args = audit_logger.collection.insert_one.call_args[0][0]
        assert call_args["event_type"] == "rate_limit_violation"
        assert call_args["severity"] == "warning"

    def test_log_security_incident(self, audit_logger):
        """Test logging security incidents"""
        audit_logger.collection.insert_one.return_value = Mock()

        result = audit_logger.log_security_incident(
            incident_type="sql_injection",
            severity=Severity.CRITICAL,
            details="Detected SQL injection attempt in query parameter",
            user_id="user_123",
            ip_address="192.168.1.1",
        )

        assert result is True
        call_args = audit_logger.collection.insert_one.call_args[0][0]
        assert call_args["event_type"] == "security_incident"
        assert call_args["severity"] == "critical"

    def test_log_password_change(self, audit_logger):
        """Test logging password changes"""
        audit_logger.collection.insert_one.return_value = Mock()

        result = audit_logger.log_password_change(
            user_id="user_123",
            ip_address="192.168.1.1",
            success=True,
        )

        assert result is True
        call_args = audit_logger.collection.insert_one.call_args[0][0]
        assert call_args["event_type"] == "password_change"
        assert call_args["severity"] == "warning"

    def test_log_account_lockout(self, audit_logger):
        """Test logging account lockouts"""
        audit_logger.collection.insert_one.return_value = Mock()

        result = audit_logger.log_account_lockout(
            user_id="user_123", reason="Too many failed login attempts", ip_address="192.168.1.1"
        )

        assert result is True
        call_args = audit_logger.collection.insert_one.call_args[0][0]
        assert call_args["event_type"] == "account_lockout"
        assert call_args["severity"] == "error"

    def test_log_privilege_escalation(self, audit_logger):
        """Test logging privilege escalation attempts"""
        audit_logger.collection.insert_one.return_value = Mock()

        result = audit_logger.log_privilege_escalation(
            user_id="user_123",
            from_role="user",
            to_role="admin",
            ip_address="192.168.1.1",
        )

        assert result is True
        call_args = audit_logger.collection.insert_one.call_args[0][0]
        assert call_args["event_type"] == "privilege_escalation"
        assert call_args["severity"] == "critical"

    def test_search_events_basic(self, audit_logger):
        """Test basic event searching"""
        mock_results = [
            {
                "_id": "123",
                "event_type": "authentication",
                "user_id": "user_123",
                "timestamp": "2025-01-06T12:00:00Z",
            }
        ]
        audit_logger.collection.find.return_value.sort.return_value.limit.return_value = (
            mock_results
        )

        results = audit_logger.search_events(
            event_type=EventType.AUTHENTICATION, user_id="user_123", limit=10
        )

        assert len(results) == 1
        assert "_id" not in results[0]  # _id should be removed
        assert results[0]["event_type"] == "authentication"

    def test_search_events_with_time_range(self, audit_logger):
        """Test searching events with time range"""
        audit_logger.collection.find.return_value.sort.return_value.limit.return_value = []

        start_time = datetime.utcnow() - timedelta(days=7)
        end_time = datetime.utcnow()

        audit_logger.search_events(start_time=start_time, end_time=end_time)

        # Verify find was called with timestamp filter
        call_args = audit_logger.collection.find.call_args[0][0]
        assert "timestamp" in call_args

    def test_search_events_error_handling(self, audit_logger):
        """Test search error handling"""
        audit_logger.collection.find.side_effect = Exception("Database error")

        results = audit_logger.search_events()

        assert results == []

    def test_export_to_csv(self, audit_logger):
        """Test exporting audit logs to CSV"""
        mock_events = [
            {
                "event_id": "evt_1",
                "timestamp": "2025-01-06T12:00:00Z",
                "event_type": "authentication",
                "severity": "info",
                "user_id": "user_123",
                "ip_address": "192.168.1.1",
                "resource": "/api/login",
                "action": "login",
                "result": "success",
                "session_id": "session_abc",
                "request_id": "req_xyz",
            }
        ]
        audit_logger.collection.find.return_value.sort.return_value.limit.return_value = (
            mock_events
        )

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".csv") as f:
            filepath = f.name

        try:
            result = audit_logger.export_to_csv(filepath)
            assert result is True

            # Verify CSV file was created and has content
            with open(filepath, "r") as csvfile:
                reader = csv.DictReader(csvfile)
                rows = list(reader)
                assert len(rows) == 1
                assert rows[0]["event_id"] == "evt_1"
                assert rows[0]["event_type"] == "authentication"
        finally:
            os.unlink(filepath)

    def test_export_to_csv_no_events(self, audit_logger):
        """Test exporting to CSV with no events"""
        audit_logger.collection.find.return_value.sort.return_value.limit.return_value = []

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".csv") as f:
            filepath = f.name

        try:
            result = audit_logger.export_to_csv(filepath)
            assert result is False
        finally:
            if os.path.exists(filepath):
                os.unlink(filepath)

    def test_export_to_json(self, audit_logger):
        """Test exporting audit logs to JSON"""
        mock_events = [
            {
                "event_id": "evt_1",
                "timestamp": "2025-01-06T12:00:00Z",
                "event_type": "authentication",
                "severity": "info",
                "user_id": "user_123",
            }
        ]
        audit_logger.collection.find.return_value.sort.return_value.limit.return_value = (
            mock_events
        )

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            filepath = f.name

        try:
            result = audit_logger.export_to_json(filepath)
            assert result is True

            # Verify JSON file was created and has content
            with open(filepath, "r") as jsonfile:
                data = json.load(jsonfile)
                assert len(data) == 1
                assert data[0]["event_id"] == "evt_1"
        finally:
            os.unlink(filepath)

    def test_get_statistics(self, audit_logger):
        """Test getting audit log statistics"""
        audit_logger.collection.count_documents.return_value = 100

        stats = audit_logger.get_statistics()

        assert "total_events" in stats
        assert "events_by_type" in stats
        assert "events_by_severity" in stats
        assert "auth_failures" in stats
        assert "rate_limit_violations" in stats
        assert "security_incidents" in stats

    def test_get_statistics_with_time_range(self, audit_logger):
        """Test statistics with time range"""
        audit_logger.collection.count_documents.return_value = 50

        start_time = datetime.utcnow() - timedelta(days=7)
        end_time = datetime.utcnow()

        stats = audit_logger.get_statistics(start_time=start_time, end_time=end_time)

        assert stats["time_range"]["start"] is not None
        assert stats["time_range"]["end"] is not None

    def test_audit_context_success(self, audit_logger):
        """Test audit context manager with successful operation"""
        audit_logger.collection.insert_one.return_value = Mock()

        with audit_logger.audit_context(
            EventType.FILE_OPERATION,
            user_id="user_123",
            resource="file.mp3",
            action="upload",
        ):
            # Simulate successful operation
            pass

        # Verify event was logged
        assert audit_logger.collection.insert_one.called
        call_args = audit_logger.collection.insert_one.call_args[0][0]
        assert call_args["result"] == "success"
        assert call_args["severity"] == "info"

    def test_audit_context_failure(self, audit_logger):
        """Test audit context manager with failed operation"""
        audit_logger.collection.insert_one.return_value = Mock()

        with pytest.raises(ValueError):
            with audit_logger.audit_context(
                EventType.FILE_OPERATION,
                user_id="user_123",
                resource="file.mp3",
                action="upload",
            ):
                raise ValueError("Upload failed")

        # Verify error was logged
        call_args = audit_logger.collection.insert_one.call_args[0][0]
        assert call_args["result"] == "failure"
        assert call_args["severity"] == "error"
        assert call_args["metadata"]["error"] == "Upload failed"

    def test_close_connection(self, audit_logger):
        """Test closing MongoDB connection"""
        audit_logger.close()
        # Client should be closed
        # Note: In actual implementation, check if close was called


class TestAuditDecorator:
    """Test audit_event decorator"""

    @patch("src.samplemind.audit.audit_logger.logging.getLogger")
    def test_decorator_success(self, mock_logger):
        """Test decorator with successful function execution"""

        @audit_event(EventType.FILE_OPERATION, action="upload")
        def upload_file(user_id, file_data, ip_address=None):
            return {"status": "success", "file_id": "file_123"}

        result = upload_file("user_123", "data", ip_address="192.168.1.1")

        assert result["status"] == "success"
        # Verify logging was called
        assert mock_logger.return_value.info.called

    @patch("src.samplemind.audit.audit_logger.logging.getLogger")
    def test_decorator_failure(self, mock_logger):
        """Test decorator with failed function execution"""

        @audit_event(EventType.FILE_OPERATION, action="upload")
        def upload_file(user_id, file_data, ip_address=None):
            raise ValueError("Upload failed")

        with pytest.raises(ValueError):
            upload_file("user_123", "data", ip_address="192.168.1.1")

        # Verify error was logged
        assert mock_logger.return_value.info.called


class TestEventTypeEnum:
    """Test EventType enumeration"""

    def test_all_event_types_defined(self):
        """Test that all required event types are defined"""
        required_types = [
            "AUTHENTICATION",
            "AUTHORIZATION",
            "API_KEY_USAGE",
            "FILE_OPERATION",
            "CONFIG_CHANGE",
            "RATE_LIMIT_VIOLATION",
            "SECURITY_INCIDENT",
            "PASSWORD_CHANGE",
            "ACCOUNT_LOCKOUT",
            "PRIVILEGE_ESCALATION",
        ]

        for event_type in required_types:
            assert hasattr(EventType, event_type)

    def test_event_type_values(self):
        """Test event type string values"""
        assert EventType.AUTHENTICATION.value == "authentication"
        assert EventType.AUTHORIZATION.value == "authorization"
        assert EventType.SECURITY_INCIDENT.value == "security_incident"


class TestSeverityEnum:
    """Test Severity enumeration"""

    def test_all_severity_levels_defined(self):
        """Test that all severity levels are defined"""
        required_levels = ["INFO", "WARNING", "ERROR", "CRITICAL"]

        for level in required_levels:
            assert hasattr(Severity, level)

    def test_severity_values(self):
        """Test severity string values"""
        assert Severity.INFO.value == "info"
        assert Severity.WARNING.value == "warning"
        assert Severity.ERROR.value == "error"
        assert Severity.CRITICAL.value == "critical"


class TestIntegration:
    """Integration tests for audit logger"""

    def test_complete_audit_flow(self, audit_logger):
        """Test complete audit logging flow"""
        audit_logger.collection.insert_one.return_value = Mock()
        audit_logger.collection.find.return_value.sort.return_value.limit.return_value = []

        # Log various events
        audit_logger.log_authentication("user_123", True, "192.168.1.1", "Mozilla/5.0")
        audit_logger.log_authorization("user_123", "/api/admin", "access", "denied")
        audit_logger.log_file_operation("user_123", "file_abc", "upload")
        audit_logger.log_security_incident(
            "brute_force", Severity.CRITICAL, "Multiple failed login attempts"
        )

        # Search events
        results = audit_logger.search_events(user_id="user_123")

        # Verify multiple events were logged
        assert audit_logger.collection.insert_one.call_count == 4

    def test_pii_redaction_end_to_end(self, audit_logger):
        """Test end-to-end PII redaction"""
        audit_logger.collection.insert_one.return_value = Mock()

        # Log event with PII
        audit_logger.log_authentication(
            user_id="john.doe@example.com",
            success=True,
            ip_address="192.168.1.100",
            user_agent="Mozilla/5.0",
            metadata={"email": "john@example.com", "phone": "555-123-4567"},
        )

        call_args = audit_logger.collection.insert_one.call_args[0][0]

        # Verify PII was redacted
        assert "xxx" in call_args["ip_address"]
        assert "[EMAIL_REDACTED]" in call_args["metadata"]["email"]
        assert "[PHONE_REDACTED]" in call_args["metadata"]["phone"]