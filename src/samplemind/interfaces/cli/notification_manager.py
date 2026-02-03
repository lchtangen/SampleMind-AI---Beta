"""
Desktop Notification Manager for SampleMind AI

Provides cross-platform desktop notifications for:
- Analysis completion
- Batch processing updates
- Error alerts
- User confirmations

Uses plyer for cross-platform support (Windows, macOS, Linux).
Falls back to terminal notifications if desktop unavailable.
"""

import logging
from typing import Optional, Literal
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)

try:
    from plyer import notification
    PLYER_AVAILABLE = True
except ImportError:
    PLYER_AVAILABLE = False
    logger.debug("plyer not available, desktop notifications disabled")


class NotificationType(Enum):
    """Notification types with priority levels"""
    INFO = ("info", 2000)
    SUCCESS = ("success", 2500)
    WARNING = ("warning", 3000)
    ERROR = ("error", 4000)

    @property
    def timeout_ms(self) -> int:
        """Default display duration in milliseconds"""
        return self[1]


class NotificationManager:
    """
    Manages desktop and terminal notifications for user feedback.

    Features:
    - Cross-platform desktop notifications (Windows, macOS, Linux)
    - Terminal fallback if desktop unavailable
    - Notification history tracking
    - Configurable enable/disable
    - Batch notification support
    """

    def __init__(self, enable_desktop: bool = True, enable_terminal: bool = True):
        """
        Initialize notification manager.

        Args:
            enable_desktop: Enable desktop notifications (if plyer available)
            enable_terminal: Enable terminal notifications
        """
        self.enable_desktop = enable_desktop and PLYER_AVAILABLE
        self.enable_terminal = enable_terminal
        self.history = []
        self.max_history = 100

        if not self.enable_desktop and enable_desktop:
            logger.warning("Desktop notifications requested but plyer not available")

        logger.info(
            f"Notification manager initialized "
            f"(desktop={self.enable_desktop}, terminal={self.enable_terminal})"
        )

    def notify(
        self,
        title: str,
        message: str,
        notification_type: NotificationType = NotificationType.INFO,
        timeout: Optional[int] = None,
        app_name: str = "SampleMind AI"
    ) -> bool:
        """
        Send a notification to the user.

        Args:
            title: Notification title (50 chars recommended)
            message: Notification message (200 chars recommended)
            notification_type: Type of notification (info, success, warning, error)
            timeout: Display duration in milliseconds (None = default for type)
            app_name: Application name for desktop notifications

        Returns:
            True if notification sent successfully
        """
        timeout = timeout or notification_type.timeout_ms

        # Record in history
        self._record_notification(title, message, notification_type)

        # Send desktop notification
        if self.enable_desktop:
            try:
                self._send_desktop_notification(
                    title, message, notification_type, timeout, app_name
                )
                logger.debug(f"Desktop notification sent: {title}")
                return True
            except Exception as e:
                logger.warning(f"Failed to send desktop notification: {e}")

        # Fallback to terminal
        if self.enable_terminal:
            self._send_terminal_notification(title, message, notification_type)
            logger.debug(f"Terminal notification sent: {title}")
            return True

        return False

    def notify_analysis_complete(
        self,
        filename: str,
        duration: float,
        success: bool = True
    ) -> None:
        """
        Notify user that audio analysis is complete.

        Args:
            filename: Name of analyzed file
            duration: Analysis duration in seconds
            success: Whether analysis succeeded
        """
        if success:
            title = "✓ Analysis Complete"
            message = f"{filename} analyzed in {duration:.2f}s"
            notif_type = NotificationType.SUCCESS
        else:
            title = "✗ Analysis Failed"
            message = f"Failed to analyze {filename}"
            notif_type = NotificationType.ERROR

        self.notify(title, message, notif_type)

    def notify_batch_progress(
        self,
        completed: int,
        total: int,
        current_file: str
    ) -> None:
        """
        Notify user of batch processing progress.

        Args:
            completed: Number of completed files
            total: Total files to process
            current_file: Currently processing file
        """
        title = f"Processing {completed}/{total}"
        message = f"Currently: {current_file}"
        self.notify(title, message, NotificationType.INFO, timeout=1500)

    def notify_batch_complete(
        self,
        total: int,
        duration: float,
        failed: int = 0
    ) -> None:
        """
        Notify user that batch processing is complete.

        Args:
            total: Total files processed
            duration: Total duration in seconds
            failed: Number of failed files
        """
        if failed == 0:
            title = "✓ Batch Complete"
            message = f"{total} files processed in {duration:.2f}s"
            notif_type = NotificationType.SUCCESS
        else:
            title = "⚠ Batch Complete"
            message = f"{total - failed}/{total} files, {failed} failed"
            notif_type = NotificationType.WARNING

        self.notify(title, message, notif_type)

    def notify_error(self, title: str, message: str) -> None:
        """
        Send error notification.

        Args:
            title: Error title
            message: Error details
        """
        self.notify(title, message, NotificationType.ERROR)

    def notify_warning(self, title: str, message: str) -> None:
        """
        Send warning notification.

        Args:
            title: Warning title
            message: Warning details
        """
        self.notify(title, message, NotificationType.WARNING)

    def notify_success(self, title: str, message: str) -> None:
        """
        Send success notification.

        Args:
            title: Success title
            message: Success details
        """
        self.notify(title, message, NotificationType.SUCCESS)

    def _send_desktop_notification(
        self,
        title: str,
        message: str,
        notification_type: NotificationType,
        timeout: int,
        app_name: str
    ) -> None:
        """Send desktop notification using plyer."""
        notification.notify(
            title=title,
            message=message,
            app_name=app_name,
            timeout=timeout,
            app_icon=None  # Can be set to app icon path
        )

    def _send_terminal_notification(
        self,
        title: str,
        message: str,
        notification_type: NotificationType
    ) -> None:
        """Send terminal notification as fallback."""
        # Use emoji indicators based on type
        emojis = {
            NotificationType.INFO: "ℹ️",
            NotificationType.SUCCESS: "✅",
            NotificationType.WARNING: "⚠️",
            NotificationType.ERROR: "❌",
        }

        emoji = emojis.get(notification_type, "•")
        timestamp = datetime.now().strftime("%H:%M:%S")

        # Format for terminal
        output = f"\n{emoji} [{timestamp}] {title}\n   {message}\n"

        # Log to appropriate level
        if notification_type == NotificationType.ERROR:
            logger.error(output)
        elif notification_type == NotificationType.WARNING:
            logger.warning(output)
        elif notification_type == NotificationType.SUCCESS:
            logger.info(output)
        else:
            logger.info(output)

    def _record_notification(
        self,
        title: str,
        message: str,
        notification_type: NotificationType
    ) -> None:
        """Record notification in history."""
        entry = {
            "timestamp": datetime.now(),
            "title": title,
            "message": message,
            "type": notification_type.name
        }

        self.history.append(entry)

        # Trim history if needed
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]

    def get_history(self, limit: int = 20) -> list:
        """
        Get notification history.

        Args:
            limit: Maximum number of entries to return

        Returns:
            List of recent notifications
        """
        return self.history[-limit:]

    def clear_history(self) -> None:
        """Clear notification history."""
        self.history.clear()
        logger.debug("Notification history cleared")

    def enable_desktop_notifications(self, enabled: bool) -> None:
        """Enable or disable desktop notifications."""
        self.enable_desktop = enabled and PLYER_AVAILABLE
        logger.info(f"Desktop notifications {'enabled' if self.enable_desktop else 'disabled'}")

    def enable_terminal_notifications(self, enabled: bool) -> None:
        """Enable or disable terminal notifications."""
        self.enable_terminal = enabled
        logger.info(f"Terminal notifications {'enabled' if self.enable_terminal else 'disabled'}")

    def get_status(self) -> dict:
        """Get notification manager status."""
        return {
            "desktop_enabled": self.enable_desktop,
            "terminal_enabled": self.enable_terminal,
            "desktop_available": PLYER_AVAILABLE,
            "history_count": len(self.history),
            "max_history": self.max_history
        }


# Global notification manager instance
_notification_manager: Optional[NotificationManager] = None


def init_notifications(enable_desktop: bool = True, enable_terminal: bool = True) -> NotificationManager:
    """Initialize global notification manager."""
    global _notification_manager
    _notification_manager = NotificationManager(enable_desktop, enable_terminal)
    return _notification_manager


def get_notifications() -> NotificationManager:
    """Get global notification manager instance."""
    global _notification_manager
    if _notification_manager is None:
        _notification_manager = NotificationManager()
    return _notification_manager


# Convenience functions
def notify(title: str, message: str, **kwargs) -> bool:
    """Send notification using default manager."""
    return get_notifications().notify(title, message, **kwargs)


def notify_success(title: str, message: str) -> None:
    """Send success notification."""
    get_notifications().notify_success(title, message)


def notify_error(title: str, message: str) -> None:
    """Send error notification."""
    get_notifications().notify_error(title, message)


def notify_warning(title: str, message: str) -> None:
    """Send warning notification."""
    get_notifications().notify_warning(title, message)
