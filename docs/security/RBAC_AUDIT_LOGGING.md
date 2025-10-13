# RBAC Audit Logging - Security Monitoring

## Overview

The RBAC system implements comprehensive audit logging for all 403 Forbidden (access denied) events. This provides security teams with detailed forensic data for monitoring unauthorized access attempts and identifying potential security threats.

## Implementation

### Location
- **Decorators**: `src/common/decorators/rbac.py`
- **Logger Name**: `rbac.access_denied`
- **Log Level**: WARNING (failed permission checks are security events)

### What Gets Logged

Every failed permission or feature access attempt logs:

1. **User Information**:
   - Username
   - User ID
   - Authentication status

2. **Access Details**:
   - Permission code or feature code
   - Organization name and ID (if applicable)
   - Event type (permission_denied or feature_access_denied)

3. **Network Information**:
   - Client IP address
   - Timestamp (automatic via logger)

4. **Security Metadata**:
   - Severity level (warning)
   - Event type classification

### Security Considerations

**What is logged**:
- User identifiers (username, ID)
- Permission/feature codes
- Organization context
- IP addresses
- Timestamps

**What is NOT logged** (to prevent sensitive data exposure):
- Passwords or credentials
- Request body data
- Session tokens
- Personal identifiable information (PII) beyond username

## Django Settings Configuration

Add the following to your `LOGGING` configuration in `src/obc_management/settings/base.py`:

```python
# RBAC Security Audit Logging
LOGGING["formatters"]["security_audit"] = {
    "format": (
        "{levelname} {asctime} - {message} | "
        "User: {username} (ID: {user_id}) | "
        "Organization: {organization_name} (ID: {organization_id}) | "
        "IP: {client_ip} | "
        "Event: {event_type}"
    ),
    "style": "{",
}

LOGGING["handlers"]["rbac_security"] = {
    "level": "WARNING",
    "class": "logging.handlers.RotatingFileHandler",
    "filename": BASE_DIR / "logs" / "rbac_security.log",
    "maxBytes": 10485760,  # 10MB
    "backupCount": 10,  # Keep 10 backup files
    "formatter": "security_audit",
}

LOGGING["loggers"]["rbac.access_denied"] = {
    "handlers": ["rbac_security", "console"],  # Log to both file and console
    "level": "WARNING",
    "propagate": False,
}
```

### Configuration Options Explained

1. **Custom Formatter** (`security_audit`):
   - Structured format for easy parsing
   - Includes all security-relevant fields
   - Suitable for SIEM integration

2. **Rotating File Handler**:
   - **File**: `logs/rbac_security.log`
   - **Max Size**: 10MB per file
   - **Backup Count**: 10 files (total ~100MB of logs)
   - **Auto-rotation**: When file reaches 10MB, rotates to `.log.1`, `.log.2`, etc.

3. **Log Level**: WARNING
   - Failed access attempts are security events
   - More severe than INFO, less than ERROR
   - Appropriate for security monitoring

4. **Propagate**: False
   - Prevents duplicate logging to root logger
   - Keeps security logs separate

## Example Log Output

### Permission Denied

```
WARNING 2025-10-13 14:30:45 - 403 Forbidden - User 'john.doe' (ID: 123) denied access to permission 'mana_access' in Organization 'OOBC' (ID: 1) from IP 192.168.1.100 | User: john.doe (ID: 123) | Organization: OOBC (ID: 1) | IP: 192.168.1.100 | Event: permission_denied
```

### Feature Access Denied

```
WARNING 2025-10-13 15:45:20 - 403 Forbidden - User 'jane.smith' (ID: 456) denied access to feature 'communities.barangay_obc' in Organization 'MOA Health' (ID: 5) from IP 10.0.0.50 | User: jane.smith (ID: 456) | Organization: MOA Health (ID: 5) | IP: 10.0.0.50 | Event: feature_access_denied
```

### No Organization Context

```
WARNING 2025-10-13 16:20:15 - 403 Forbidden - User 'test.user' (ID: 789) denied access to permission 'admin.manage_users' in Organization 'None' (ID: None) from IP 172.16.0.100 | User: test.user (ID: 789) | Organization: None (ID: None) | IP: 172.16.0.100 | Event: permission_denied
```

## Production Deployment

### Log Rotation Strategy

For production environments, consider:

1. **Larger backup count**: Increase `backupCount` to 30+ for long-term retention
2. **External log shipping**: Send logs to centralized logging (ELK, Splunk, CloudWatch)
3. **Compression**: Enable log compression to save disk space
4. **Archival**: Move old logs to cold storage after 90 days

### Enhanced Production Configuration

```python
# Production-ready configuration
LOGGING["handlers"]["rbac_security"] = {
    "level": "WARNING",
    "class": "logging.handlers.TimedRotatingFileHandler",  # Rotate by time, not size
    "filename": BASE_DIR / "logs" / "rbac_security.log",
    "when": "midnight",  # Rotate daily at midnight
    "interval": 1,
    "backupCount": 90,  # Keep 90 days of logs
    "formatter": "security_audit",
}
```

### Security Monitoring Integration

The structured `extra` fields in logs enable easy integration with:

1. **SIEM Systems** (Splunk, ELK):
   - Parse JSON-like structure
   - Create dashboards for failed access attempts
   - Set up alerts for unusual patterns

2. **Security Alerts**:
   ```python
   # Example: Alert on multiple failures from same IP
   if failed_attempts_from_ip > 10:
       send_security_alert(ip_address, user, permission_code)
   ```

3. **Forensic Analysis**:
   - Track user behavior patterns
   - Identify privilege escalation attempts
   - Audit compliance for security reviews

## Monitoring Dashboard Queries

### Failed Access by User (Last 24 Hours)

```bash
grep "403 Forbidden" logs/rbac_security.log | \
  grep "$(date +%Y-%m-%d)" | \
  awk -F"User: " '{print $2}' | \
  awk -F" \\(ID:" '{print $1}' | \
  sort | uniq -c | sort -rn
```

### Failed Access by Permission

```bash
grep "permission_denied" logs/rbac_security.log | \
  grep "$(date +%Y-%m-%d)" | \
  awk -F"permission '" '{print $2}' | \
  awk -F"'" '{print $1}' | \
  sort | uniq -c | sort -rn
```

### Failed Access by IP Address

```bash
grep "403 Forbidden" logs/rbac_security.log | \
  grep "$(date +%Y-%m-%d)" | \
  awk -F"IP " '{print $2}' | \
  awk '{print $1}' | \
  sort | uniq -c | sort -rn
```

## Compliance & Privacy

### Data Retention

- **Development**: 10 backup files (~100MB total)
- **Staging**: 30 days of logs
- **Production**: 90 days of logs (compliance requirement)

### GDPR Compliance

- No sensitive personal data logged
- Username is minimal identifier (not email/phone)
- IP addresses are functional requirement for security
- Logs can be purged on user deletion request

### Audit Trail

- All logs are immutable (append-only)
- File permissions: `0640` (owner read/write, group read)
- Owner: Django process user
- Group: Security team group

## Testing

### Manual Testing

1. **Test Permission Denial**:
   ```python
   # Try to access protected view without permission
   response = client.get('/rbac/users/', user=unauthorized_user)

   # Check log file
   with open('logs/rbac_security.log') as f:
       logs = f.read()
       assert '403 Forbidden' in logs
       assert 'permission_denied' in logs
   ```

2. **Test Feature Denial**:
   ```python
   # Try to access feature without access
   response = client.get('/mana/', user=user_without_mana_access)

   # Check log file
   with open('logs/rbac_security.log') as f:
       logs = f.read()
       assert 'feature_access_denied' in logs
   ```

### Automated Testing

```python
import logging
from django.test import TestCase, Client
from django.contrib.auth import get_user_model

class RBACSecurityLoggingTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123'
        )

        # Capture logs
        self.logger = logging.getLogger('rbac.access_denied')
        self.log_handler = logging.handlers.MemoryHandler(capacity=100)
        self.logger.addHandler(self.log_handler)

    def test_permission_denied_logging(self):
        self.client.force_login(self.user)

        # Access protected resource without permission
        response = self.client.get('/rbac/users/')

        # Assert 403 response
        self.assertEqual(response.status_code, 403)

        # Check log was created
        self.log_handler.flush()
        logs = [record.getMessage() for record in self.log_handler.buffer]

        self.assertTrue(any('403 Forbidden' in log for log in logs))
        self.assertTrue(any('permission_denied' in log for log in logs))
        self.assertTrue(any(self.user.username in log for log in logs))
```

## Troubleshooting

### Logs Not Appearing

1. **Check directory exists**:
   ```bash
   ls -la logs/
   ```

2. **Check permissions**:
   ```bash
   ls -la logs/rbac_security.log
   # Should be: -rw-r----- (0640)
   ```

3. **Check logger configuration**:
   ```python
   import logging
   logger = logging.getLogger('rbac.access_denied')
   print(logger.handlers)  # Should show file handler
   ```

### Log Files Too Large

1. **Reduce backup count**:
   ```python
   "backupCount": 5,  # Instead of 10
   ```

2. **Switch to time-based rotation**:
   ```python
   "class": "logging.handlers.TimedRotatingFileHandler",
   "when": "midnight",
   ```

3. **Enable compression** (requires custom handler):
   ```python
   from logging.handlers import RotatingFileHandler
   import gzip

   class CompressedRotatingFileHandler(RotatingFileHandler):
       def doRollover(self):
           super().doRollover()
           # Compress old log files
           for i in range(1, self.backupCount + 1):
               old_log = f"{self.baseFilename}.{i}"
               if os.path.exists(old_log):
                   with open(old_log, 'rb') as f_in:
                       with gzip.open(f"{old_log}.gz", 'wb') as f_out:
                           f_out.writelines(f_in)
                   os.remove(old_log)
   ```

## Future Enhancements

### Real-Time Alerting

```python
# Add custom handler for critical events
class SecurityAlertHandler(logging.Handler):
    def emit(self, record):
        # Send alert via Slack, email, or SMS
        if record.event_type == 'permission_denied':
            send_security_alert(
                subject=f"Access Denied: {record.username}",
                message=record.getMessage(),
                severity='warning'
            )
```

### Pattern Detection

```python
# Detect brute force attempts
from collections import defaultdict
from datetime import datetime, timedelta

failed_attempts = defaultdict(list)

def check_for_brute_force(user_id, timestamp):
    failed_attempts[user_id].append(timestamp)

    # Remove old attempts (older than 10 minutes)
    cutoff = datetime.now() - timedelta(minutes=10)
    failed_attempts[user_id] = [
        t for t in failed_attempts[user_id] if t > cutoff
    ]

    # Alert if > 5 failures in 10 minutes
    if len(failed_attempts[user_id]) > 5:
        send_security_alert(f"Brute force detected: User {user_id}")
```

### Metrics Dashboard

```python
# Export metrics to Prometheus/Grafana
from prometheus_client import Counter

rbac_denials_total = Counter(
    'rbac_access_denied_total',
    'Total RBAC access denials',
    ['permission_code', 'organization', 'event_type']
)

# In decorator, increment counter
rbac_denials_total.labels(
    permission_code=permission_code,
    organization=org_name,
    event_type='permission_denied'
).inc()
```

## Related Documentation

- [RBAC Implementation Guide](../rbac/MOA_RBAC_IMPLEMENTATION.md)
- [Security Architecture](SECURITY_ARCHITECTURE.md)
- [Audit Compliance](AUDIT_COMPLIANCE.md)
- [Django Logging Documentation](https://docs.djangoproject.com/en/4.2/topics/logging/)

---

**Security Notice**: These logs contain access control information. Ensure proper file permissions and access controls are in place. Never expose log files publicly.
