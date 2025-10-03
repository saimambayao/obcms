"""
Real-time security alerting system.

Sends alerts to multiple channels:
- Slack (instant messaging)
- Email (security team)
- Logging (persistent record)

Security Events Monitored:
- Brute force attacks (10+ failed logins in 5 minutes)
- Suspicious API activity (high error rates)
- Account lockouts
- Unauthorized access attempts
- Data export operations
- Administrative actions
"""

import logging
import json
import requests
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger(__name__)


def send_security_alert(event_type, details, severity="WARNING", metadata=None):
    """
    Send security alert to configured channels.

    Args:
        event_type: Type of security event (e.g., "Brute Force Attack")
        details: Detailed description of the event
        severity: INFO, WARNING, ERROR, CRITICAL
        metadata: Additional context (dict)

    Example:
        send_security_alert(
            event_type="Brute Force Attack Detected",
            details="10+ failed logins from IP 192.168.1.100",
            severity="CRITICAL",
            metadata={"ip": "192.168.1.100", "username": "admin", "attempts": 12}
        )
    """
    severity_emoji = {
        "INFO": "ℹ️",
        "WARNING": "⚠️",
        "ERROR": "❌",
        "CRITICAL": "🚨",
    }

    emoji = severity_emoji.get(severity, "📢")

    # Format alert message
    alert_message = f"{emoji} **{severity}**: {event_type}\n\n{details}"

    if metadata:
        alert_message += f"\n\n**Metadata:**\n```json\n{json.dumps(metadata, indent=2)}\n```"

    # Always log the alert
    _log_alert(severity, event_type, details, metadata)

    # Send to Slack (if configured)
    if hasattr(settings, 'SLACK_WEBHOOK_URL') and settings.SLACK_WEBHOOK_URL:
        try:
            send_slack_alert(alert_message, severity)
        except Exception as e:
            logger.error(f"Failed to send Slack alert: {e}")

    # Send email (for ERROR and CRITICAL only)
    if severity in ["ERROR", "CRITICAL"]:
        try:
            send_email_alert(event_type, alert_message, severity)
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")


def send_slack_alert(message, severity):
    """
    Send alert to Slack channel.

    Requires SLACK_WEBHOOK_URL in settings.
    Get webhook URL from: https://api.slack.com/messaging/webhooks
    """
    if not hasattr(settings, 'SLACK_WEBHOOK_URL') or not settings.SLACK_WEBHOOK_URL:
        logger.debug("Slack webhook URL not configured, skipping Slack alert")
        return

    color_map = {
        "INFO": "#36a64f",      # Green
        "WARNING": "#ff9900",   # Orange
        "ERROR": "#ff0000",     # Red
        "CRITICAL": "#8b0000",  # Dark red
    }

    payload = {
        "text": "🔒 OBCMS Security Alert",
        "attachments": [
            {
                "color": color_map.get(severity, "#808080"),
                "text": message,
                "footer": "OBCMS Security Monitoring",
                "footer_icon": "https://obcms.gov.ph/static/img/logo.png",
                "ts": int(timezone.now().timestamp()),
            }
        ]
    }

    response = requests.post(
        settings.SLACK_WEBHOOK_URL,
        json=payload,
        timeout=5
    )
    response.raise_for_status()
    logger.info(f"Slack alert sent successfully: {severity} - {message[:50]}...")


def send_email_alert(subject, message, severity):
    """
    Send alert email to security team.

    Requires SECURITY_TEAM_EMAILS in settings.
    """
    if not hasattr(settings, 'SECURITY_TEAM_EMAILS') or not settings.SECURITY_TEAM_EMAILS:
        logger.debug("Security team emails not configured, skipping email alert")
        return

    # Format email subject with severity
    email_subject = f"[OBCMS SECURITY - {severity}] {subject}"

    # Send email
    send_mail(
        subject=email_subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=settings.SECURITY_TEAM_EMAILS,
        fail_silently=False,
    )
    logger.info(f"Email alert sent to {len(settings.SECURITY_TEAM_EMAILS)} recipients")


def _log_alert(severity, event_type, details, metadata):
    """Log alert to application logs for persistent record."""
    log_message = f"Security Alert: {event_type} | {details}"

    if metadata:
        log_message += f" | Metadata: {json.dumps(metadata)}"

    if severity == "CRITICAL":
        logger.critical(log_message)
    elif severity == "ERROR":
        logger.error(log_message)
    elif severity == "WARNING":
        logger.warning(log_message)
    else:
        logger.info(log_message)


# ============================================================================
# SPECIFIC ALERT FUNCTIONS
# ============================================================================

def alert_brute_force_attack(ip_address, username, attempt_count):
    """Alert for brute force attack detection."""
    send_security_alert(
        event_type="Brute Force Attack Detected",
        details=(
            f"**IP Address:** {ip_address}\n"
            f"**Username:** {username}\n"
            f"**Failed Attempts:** {attempt_count} in 5 minutes\n"
            f"**Action:** IP may be automatically blocked by Axes\n"
            f"**Recommendation:** Review security logs and consider manual IP ban"
        ),
        severity="CRITICAL",
        metadata={
            "ip": ip_address,
            "username": username,
            "attempts": attempt_count,
            "timestamp": timezone.now().isoformat(),
        }
    )


def alert_account_lockout(username, ip_address, lockout_duration):
    """Alert for account lockout."""
    send_security_alert(
        event_type="Account Lockout",
        details=(
            f"**Username:** {username}\n"
            f"**IP Address:** {ip_address}\n"
            f"**Lockout Duration:** {lockout_duration} minutes\n"
            f"**Action:** User cannot login until cooldown period expires"
        ),
        severity="WARNING",
        metadata={
            "username": username,
            "ip": ip_address,
            "lockout_duration": lockout_duration,
            "timestamp": timezone.now().isoformat(),
        }
    )


def alert_suspicious_api_activity(path, error_rate, time_window):
    """Alert for suspicious API activity (high error rate)."""
    send_security_alert(
        event_type="Suspicious API Activity",
        details=(
            f"**API Endpoint:** {path}\n"
            f"**Error Rate:** {error_rate}%\n"
            f"**Time Window:** {time_window} minutes\n"
            f"**Possible Causes:** Attack attempt, misconfigured client, API bug"
        ),
        severity="WARNING",
        metadata={
            "path": path,
            "error_rate": error_rate,
            "time_window": time_window,
            "timestamp": timezone.now().isoformat(),
        }
    )


def alert_mass_data_export(user, export_type, record_count):
    """Alert for large data export operations."""
    send_security_alert(
        event_type="Mass Data Export",
        details=(
            f"**User:** {user.username} (ID: {user.id})\n"
            f"**Export Type:** {export_type}\n"
            f"**Record Count:** {record_count:,}\n"
            f"**Email:** {user.email}\n"
            f"**User Type:** {user.user_type}\n"
            f"**Action:** Review if this export is authorized"
        ),
        severity="WARNING",
        metadata={
            "user_id": user.id,
            "username": user.username,
            "export_type": export_type,
            "record_count": record_count,
            "timestamp": timezone.now().isoformat(),
        }
    )


def alert_unauthorized_access(user, path, permission_required):
    """Alert for unauthorized access attempt."""
    send_security_alert(
        event_type="Unauthorized Access Attempt",
        details=(
            f"**User:** {user.username} (ID: {user.id})\n"
            f"**Path:** {path}\n"
            f"**Required Permission:** {permission_required}\n"
            f"**User Permissions:** {', '.join([p.codename for p in user.user_permissions.all()][:5])}\n"
            f"**Action:** User attempted to access unauthorized resource"
        ),
        severity="WARNING",
        metadata={
            "user_id": user.id,
            "username": user.username,
            "path": path,
            "permission_required": permission_required,
            "timestamp": timezone.now().isoformat(),
        }
    )


def alert_admin_action(admin_user, action, target):
    """Alert for critical administrative actions."""
    send_security_alert(
        event_type="Administrative Action",
        details=(
            f"**Admin:** {admin_user.username} (ID: {admin_user.id})\n"
            f"**Action:** {action}\n"
            f"**Target:** {target}\n"
            f"**Email:** {admin_user.email}"
        ),
        severity="INFO",
        metadata={
            "admin_id": admin_user.id,
            "admin_username": admin_user.username,
            "action": action,
            "target": target,
            "timestamp": timezone.now().isoformat(),
        }
    )


# ============================================================================
# CONFIGURATION CHECK
# ============================================================================

def check_alerting_configuration():
    """
    Check if alerting is properly configured.

    Returns dict with configuration status.
    """
    config_status = {
        "slack_configured": hasattr(settings, 'SLACK_WEBHOOK_URL') and bool(settings.SLACK_WEBHOOK_URL),
        "email_configured": hasattr(settings, 'SECURITY_TEAM_EMAILS') and bool(settings.SECURITY_TEAM_EMAILS),
        "logging_configured": True,  # Always available
    }

    if not config_status["slack_configured"]:
        logger.warning("Slack alerting not configured - set SLACK_WEBHOOK_URL in settings")

    if not config_status["email_configured"]:
        logger.warning("Email alerting not configured - set SECURITY_TEAM_EMAILS in settings")

    return config_status
