# RBAC Audit Logging - Quick Reference

## Summary

All 403 Forbidden events are now automatically logged for security auditing. No additional code required - just use the RBAC decorators as normal.

## Modified Files

1. **`src/common/decorators/rbac.py`** - Enhanced with security logging
2. **`src/obc_management/settings/base.py`** - Added RBAC security logger configuration

## How It Works

### Decorator Usage (No Changes Required)

```python
from common.decorators.rbac import require_permission, require_feature_access

# Permission-based access control
@login_required
@require_permission('communities.edit_obc_community', organization_param='org_id')
def edit_community(request, org_id):
    # Your view code
    pass

# Feature-based access control
@login_required
@require_feature_access('mana.regional_overview')
def mana_dashboard(request):
    # Your view code
    pass
```

**When access is denied**, the decorator automatically logs:
- User details (username, ID)
- Permission/feature code
- Organization context
- Client IP address
- Timestamp

### Log File Location

- **File**: `src/logs/rbac_security.log`
- **Rotation**: Auto-rotates at 10MB
- **Retention**: 10 backup files (~100MB total)
- **Format**: Structured security audit format

## Example Log Outputs

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

## Viewing Logs

### View All 403 Events

```bash
cd src/
tail -f logs/rbac_security.log
```

### View Today's Denials

```bash
grep "$(date +%Y-%m-%d)" logs/rbac_security.log
```

### Count Denials by User

```bash
grep "403 Forbidden" logs/rbac_security.log | \
  awk -F"User: " '{print $2}' | \
  awk -F" \\(ID:" '{print $1}' | \
  sort | uniq -c | sort -rn
```

### Count Denials by Permission

```bash
grep "permission_denied" logs/rbac_security.log | \
  awk -F"permission '" '{print $2}' | \
  awk -F"'" '{print $1}' | \
  sort | uniq -c | sort -rn
```

### Find Suspicious IPs (Multiple Failed Attempts)

```bash
grep "403 Forbidden" logs/rbac_security.log | \
  awk -F"IP " '{print $2}' | \
  awk '{print $1}' | \
  sort | uniq -c | sort -rn | head -10
```

## Logger Configuration (Already Added to Settings)

```python
# src/obc_management/settings/base.py

LOGGING = {
    # ... existing configuration ...

    "formatters": {
        # ... existing formatters ...

        "security_audit": {
            "format": (
                "{levelname} {asctime} - {message} | "
                "User: {username} (ID: {user_id}) | "
                "Organization: {organization_name} (ID: {organization_id}) | "
                "IP: {client_ip} | "
                "Event: {event_type}"
            ),
            "style": "{",
        },
    },

    "handlers": {
        # ... existing handlers ...

        "rbac_security": {
            "level": "WARNING",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": BASE_DIR / "logs" / "rbac_security.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 10,  # Keep 10 backup files
            "formatter": "security_audit",
        },
    },

    "loggers": {
        # ... existing loggers ...

        "rbac.access_denied": {
            "handlers": ["rbac_security", "console"],
            "level": "WARNING",
            "propagate": False,
        },
    },
}
```

## Security Monitoring Queries

### Last 24 Hours - Top Failed Access Users

```bash
grep "403 Forbidden" logs/rbac_security.log | \
  grep "$(date +%Y-%m-%d)" | \
  awk -F"User: " '{print $2}' | \
  awk -F" \\(ID:" '{print $1}' | \
  sort | uniq -c | sort -rn | head -10
```

**Output**:
```
     15 john.doe
      8 jane.smith
      3 test.user
```

### Last 24 Hours - Top Denied Permissions

```bash
grep "permission_denied" logs/rbac_security.log | \
  grep "$(date +%Y-%m-%d)" | \
  awk -F"permission '" '{print $2}' | \
  awk -F"'" '{print $1}' | \
  sort | uniq -c | sort -rn | head -10
```

**Output**:
```
     12 mana_access
      7 communities.edit_obc_community
      4 admin.manage_users
```

### Last 24 Hours - Failed Access by Organization

```bash
grep "403 Forbidden" logs/rbac_security.log | \
  grep "$(date +%Y-%m-%d)" | \
  awk -F"Organization: " '{print $2}' | \
  awk -F" \\(ID:" '{print $1}' | \
  sort | uniq -c | sort -rn | head -10
```

**Output**:
```
     18 OOBC
      9 MOA Health
      3 None
```

### Detect Brute Force Attempts (>5 failures in 10 minutes)

```bash
# Get timestamps and IPs from last hour
grep "403 Forbidden" logs/rbac_security.log | \
  grep "$(date +%Y-%m-%d)" | \
  awk '{print $2, $NF}' | \
  sort | uniq -c | \
  awk '$1 > 5 {print "Suspicious: " $0}'
```

## Testing

### Test Permission Denied Logging

```python
# In Django shell or test
from django.test import Client
from django.contrib.auth import get_user_model

client = Client()
User = get_user_model()

# Create user without permission
user = User.objects.create_user(username='testuser', password='testpass')
client.force_login(user)

# Try to access protected resource
response = client.get('/rbac/users/')

# Check response
print(response.status_code)  # Should be 403

# Check log file
with open('logs/rbac_security.log') as f:
    logs = f.read()
    print('Permission denied logged:', '403 Forbidden' in logs)
    print('Event type logged:', 'permission_denied' in logs)
    print('User logged:', 'testuser' in logs)
```

### Test Feature Access Denied Logging

```python
# User without MANA feature access
response = client.get('/mana/')

# Check log file
with open('logs/rbac_security.log') as f:
    logs = f.read()
    print('Feature denial logged:', 'feature_access_denied' in logs)
```

## Production Configuration

For production, consider:

1. **Increase backup count**:
   ```python
   "backupCount": 30,  # 30 days of logs
   ```

2. **Switch to time-based rotation**:
   ```python
   "class": "logging.handlers.TimedRotatingFileHandler",
   "when": "midnight",  # Rotate daily
   "interval": 1,
   "backupCount": 90,  # 90 days
   ```

3. **Send to external monitoring**:
   - ELK Stack (Elasticsearch, Logstash, Kibana)
   - Splunk
   - AWS CloudWatch
   - Azure Monitor

## Log Fields Reference

| Field | Description | Example |
|-------|-------------|---------|
| `levelname` | Log severity | `WARNING` |
| `asctime` | Timestamp | `2025-10-13 14:30:45` |
| `message` | Primary log message | `403 Forbidden - User 'john.doe'...` |
| `username` | User's username | `john.doe` |
| `user_id` | User's database ID | `123` |
| `organization_name` | Organization name | `OOBC` |
| `organization_id` | Organization ID | `1` |
| `client_ip` | Client IP address | `192.168.1.100` |
| `event_type` | Event classification | `permission_denied` or `feature_access_denied` |

## Security Best Practices

1. **File Permissions**:
   ```bash
   chmod 640 logs/rbac_security.log
   chown django:security logs/rbac_security.log
   ```

2. **Never Log Sensitive Data**:
   - ✅ Username, User ID
   - ✅ Permission codes
   - ✅ IP addresses
   - ❌ Passwords
   - ❌ Session tokens
   - ❌ Personal data (email, phone)

3. **Regular Monitoring**:
   - Daily review of failed access attempts
   - Alert on unusual patterns (>10 failures/hour)
   - Weekly security audit reports

4. **Log Retention**:
   - Development: 10 files (~100MB)
   - Staging: 30 days
   - Production: 90 days (compliance)

## Troubleshooting

### Logs Not Appearing

**Check logger is configured**:
```python
import logging
logger = logging.getLogger('rbac.access_denied')
print(logger.handlers)  # Should show RotatingFileHandler
```

**Check log directory exists**:
```bash
ls -la logs/
# Should show rbac_security.log
```

**Check permissions**:
```bash
ls -la logs/rbac_security.log
# Should be writable by Django process
```

### Log File Too Large

**Reduce backup count**:
```python
"backupCount": 5,  # Instead of 10
```

**Or switch to daily rotation**:
```python
"class": "logging.handlers.TimedRotatingFileHandler",
"when": "midnight",
```

## Related Documentation

- [Full RBAC Audit Logging Guide](RBAC_AUDIT_LOGGING.md)
- [RBAC Implementation](../rbac/MOA_RBAC_IMPLEMENTATION.md)
- [Security Architecture](SECURITY_ARCHITECTURE.md)

---

**Quick Start**: Just use the RBAC decorators as normal. All 403 events are automatically logged to `src/logs/rbac_security.log` with full security context.
