# RBAC Audit Logging - Code Examples

## Implementation Overview

This document provides practical code examples demonstrating the RBAC audit logging implementation.

## Modified Decorator Code

### Location: `src/common/decorators/rbac.py`

#### IP Address Extraction

```python
def _get_client_ip(request):
    """
    Extract client IP address from request.

    Args:
        request: Django request object

    Returns:
        Client IP address string
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        # Take the first IP if behind proxy
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', 'unknown')
    return ip
```

#### Permission Denied Logging (in `require_permission` decorator)

```python
# Check permission using RBACService
if not RBACService.has_permission(request, permission_code, organization):
    # Get user info for audit logging
    user_id = request.user.id if hasattr(request.user, 'id') else 'unknown'
    username = request.user.username if hasattr(request.user, 'username') else 'anonymous'
    org_name = organization.name if organization else 'None'
    org_id = organization.id if organization else 'None'
    client_ip = _get_client_ip(request)

    # Security audit log - WARNING level for failed access attempts
    security_logger.warning(
        f"403 Forbidden - User '{username}' (ID: {user_id}) denied access to "
        f"permission '{permission_code}' in Organization '{org_name}' (ID: {org_id}) "
        f"from IP {client_ip}",
        extra={
            'user_id': user_id,
            'username': username,
            'permission_code': permission_code,
            'organization_id': org_id,
            'organization_name': org_name,
            'client_ip': client_ip,
            'event_type': 'permission_denied',
            'severity': 'warning',
        }
    )

    messages.error(
        request,
        f"You do not have permission to access this resource."
    )
    raise PermissionDenied(
        f"User lacks required permission: {permission_code}"
    )
```

#### Feature Access Denied Logging (in `require_feature_access` decorator)

```python
# Check feature access using RBACService
if not RBACService.has_feature_access(request.user, feature_code, organization):
    # Get user info for audit logging
    user_id = request.user.id if hasattr(request.user, 'id') else 'unknown'
    username = request.user.username if hasattr(request.user, 'username') else 'anonymous'
    org_name = organization.name if organization else 'None'
    org_id = organization.id if organization else 'None'
    client_ip = _get_client_ip(request)

    # Security audit log - WARNING level for failed access attempts
    security_logger.warning(
        f"403 Forbidden - User '{username}' (ID: {user_id}) denied access to "
        f"feature '{feature_code}' in Organization '{org_name}' (ID: {org_id}) "
        f"from IP {client_ip}",
        extra={
            'user_id': user_id,
            'username': username,
            'feature_code': feature_code,
            'organization_id': org_id,
            'organization_name': org_name,
            'client_ip': client_ip,
            'event_type': 'feature_access_denied',
            'severity': 'warning',
        }
    )

    feature_name = feature_code.split('.')[-1].replace('_', ' ').title()
    messages.error(
        request,
        f"You do not have access to the {feature_name} module."
    )
    raise PermissionDenied(
        f"User lacks access to feature: {feature_code}"
    )
```

## Logging Configuration

### Location: `src/obc_management/settings/base.py`

```python
# Logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
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
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": BASE_DIR / "logs" / "django.log",
            "formatter": "verbose",
        },
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "rbac_security": {
            "level": "WARNING",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": BASE_DIR / "logs" / "rbac_security.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 10,  # Keep 10 backup files (~100MB total)
            "formatter": "security_audit",
        },
    },
    "root": {
        "handlers": ["console", "file"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
        "obc_management": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
        "rbac.access_denied": {
            "handlers": ["rbac_security", "console"],
            "level": "WARNING",
            "propagate": False,
        },
    },
}
```

## Example Log Outputs

### Scenario 1: Permission Denied

**Request**: User 'john.doe' tries to edit a community without permission

**View Code**:
```python
@login_required
@require_permission('communities.edit_obc_community', organization_param='org_id')
def edit_community(request, org_id):
    # View logic
    pass
```

**Log Output**:
```
WARNING 2025-10-13 14:30:45 - 403 Forbidden - User 'john.doe' (ID: 123) denied access to permission 'communities.edit_obc_community' in Organization 'OOBC' (ID: 1) from IP 192.168.1.100 | User: john.doe (ID: 123) | Organization: OOBC (ID: 1) | IP: 192.168.1.100 | Event: permission_denied
```

### Scenario 2: Feature Access Denied

**Request**: User 'jane.smith' tries to access MANA module without access

**View Code**:
```python
@login_required
@require_feature_access('mana.regional_overview')
def mana_dashboard(request):
    # View logic
    pass
```

**Log Output**:
```
WARNING 2025-10-13 15:45:20 - 403 Forbidden - User 'jane.smith' (ID: 456) denied access to feature 'mana.regional_overview' in Organization 'None' (ID: None) from IP 10.0.0.50 | User: jane.smith (ID: 456) | Organization: None (ID: None) | IP: 10.0.0.50 | Event: feature_access_denied
```

### Scenario 3: RBAC Management Access Denied

**Request**: User 'test.user' tries to access RBAC user management

**View Code**:
```python
@login_required
@require_permission('rbac.manage_users')
def rbac_users_list(request):
    # View logic
    pass
```

**Log Output**:
```
WARNING 2025-10-13 16:20:15 - 403 Forbidden - User 'test.user' (ID: 789) denied access to permission 'rbac.manage_users' in Organization 'None' (ID: None) from IP 172.16.0.100 | User: test.user (ID: 789) | Organization: None (ID: None) | IP: 172.16.0.100 | Event: permission_denied
```

### Scenario 4: Multi-Organization Context

**Request**: MOA user tries to access another MOA's data

**View Code**:
```python
@login_required
@require_permission('communities.view_obc_community', organization_param='org_id')
def view_community(request, org_id):
    # View logic
    pass
```

**Log Output**:
```
WARNING 2025-10-13 17:10:30 - 403 Forbidden - User 'moa.user' (ID: 234) denied access to permission 'communities.view_obc_community' in Organization 'MOA Health' (ID: 5) from IP 192.168.2.50 | User: moa.user (ID: 234) | Organization: MOA Health (ID: 5) | IP: 192.168.2.50 | Event: permission_denied
```

### Scenario 5: Behind Proxy (X-Forwarded-For)

**Request**: User accessing through load balancer/proxy

**Log Output**:
```
WARNING 2025-10-13 18:25:10 - 403 Forbidden - User 'proxy.user' (ID: 567) denied access to permission 'admin.manage_users' in Organization 'OOBC' (ID: 1) from IP 203.0.113.45 | User: proxy.user (ID: 567) | Organization: OOBC (ID: 1) | IP: 203.0.113.45 | Event: permission_denied
```

**Note**: IP `203.0.113.45` was extracted from `X-Forwarded-For` header (first IP in the chain)

## Testing Examples

### Unit Test Example

```python
import logging
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from logging.handlers import MemoryHandler

class RBACSecurityLoggingTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.User = get_user_model()
        self.user = self.User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

        # Capture logs
        self.logger = logging.getLogger('rbac.access_denied')
        self.log_handler = MemoryHandler(capacity=100)
        self.logger.addHandler(self.log_handler)

    def test_permission_denied_logging(self):
        """Test that permission denied events are logged"""
        self.client.force_login(self.user)

        # Access protected resource without permission
        response = self.client.get('/rbac/users/')

        # Assert 403 response
        self.assertEqual(response.status_code, 403)

        # Check log was created
        self.log_handler.flush()
        logs = [record.getMessage() for record in self.log_handler.buffer]

        # Assertions
        self.assertTrue(any('403 Forbidden' in log for log in logs))
        self.assertTrue(any('permission_denied' in log for log in logs))
        self.assertTrue(any(self.user.username in log for log in logs))

    def test_feature_access_denied_logging(self):
        """Test that feature access denied events are logged"""
        self.client.force_login(self.user)

        # Access feature without permission
        response = self.client.get('/mana/')

        # Assert 403 response
        self.assertEqual(response.status_code, 403)

        # Check log was created
        self.log_handler.flush()
        logs = [record.getMessage() for record in self.log_handler.buffer]

        # Assertions
        self.assertTrue(any('403 Forbidden' in log for log in logs))
        self.assertTrue(any('feature_access_denied' in log for log in logs))

    def test_log_contains_ip_address(self):
        """Test that logs include client IP address"""
        self.client.force_login(self.user)

        # Set IP in request
        response = self.client.get(
            '/rbac/users/',
            REMOTE_ADDR='192.168.1.100'
        )

        self.assertEqual(response.status_code, 403)

        # Check log contains IP
        self.log_handler.flush()
        logs = [record.getMessage() for record in self.log_handler.buffer]

        self.assertTrue(any('192.168.1.100' in log for log in logs))

    def tearDown(self):
        self.logger.removeHandler(self.log_handler)
```

### Integration Test Example

```python
from django.test import TestCase, Client
from coordination.models import Organization
from common.models import User

class RBACLoggingIntegrationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.org = Organization.objects.create(
            name='Test Organization',
            organization_type='ministry'
        )
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            organization=self.org
        )

    def test_multi_organization_access_denied_logging(self):
        """Test logging when user tries to access another org's data"""
        # Create another organization
        other_org = Organization.objects.create(
            name='Other Organization',
            organization_type='ministry'
        )

        self.client.force_login(self.user)

        # Try to access other org's data
        response = self.client.get(
            f'/communities/{other_org.id}/edit/'
        )

        # Should be denied (403)
        self.assertEqual(response.status_code, 403)

        # Check log file
        with open('logs/rbac_security.log') as f:
            logs = f.read()

        # Verify log contents
        self.assertIn('403 Forbidden', logs)
        self.assertIn(self.user.username, logs)
        self.assertIn('Other Organization', logs)
        self.assertIn('permission_denied', logs)
```

## Manual Testing

### Test Permission Denied

```bash
# Start Django shell
cd src/
python manage.py shell

# Run test
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
print(f"Status Code: {response.status_code}")  # Should be 403

# Check log file
with open('logs/rbac_security.log') as f:
    print("\n--- SECURITY LOG ---")
    print(f.read())
```

### Test Feature Access Denied

```bash
# In Django shell
from django.test import Client
from common.models import User

client = Client()

# Create user without MANA access
user = User.objects.create_user(username='nomauser', password='testpass')
client.force_login(user)

# Try to access MANA
response = client.get('/mana/')

# Check log
with open('logs/rbac_security.log') as f:
    print("\n--- FEATURE ACCESS DENIED LOG ---")
    for line in f:
        if 'feature_access_denied' in line:
            print(line)
```

## Log Parsing Examples

### Extract All Failed Attempts Today

```python
from datetime import date
import re

def get_todays_failures():
    today = date.today().strftime('%Y-%m-%d')
    failures = []

    with open('logs/rbac_security.log') as f:
        for line in f:
            if today in line and '403 Forbidden' in line:
                # Parse log entry
                match = re.search(
                    r"User '(\w+)' \(ID: (\d+)\) denied access to (\w+) '([\w.]+)'",
                    line
                )
                if match:
                    failures.append({
                        'username': match.group(1),
                        'user_id': match.group(2),
                        'access_type': match.group(3),
                        'code': match.group(4),
                        'timestamp': line.split()[1] + ' ' + line.split()[2]
                    })

    return failures

# Usage
failures = get_todays_failures()
for fail in failures:
    print(f"{fail['timestamp']}: {fail['username']} tried to access {fail['code']}")
```

### Detect Suspicious Activity

```python
from collections import defaultdict
from datetime import datetime, timedelta

def detect_brute_force():
    """Detect multiple failed attempts from same IP"""
    attempts = defaultdict(list)

    with open('logs/rbac_security.log') as f:
        for line in f:
            if '403 Forbidden' in line:
                # Extract IP and timestamp
                ip = line.split('IP ')[-1].split()[0]
                timestamp_str = ' '.join(line.split()[1:3])
                timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')

                attempts[ip].append(timestamp)

    # Check for suspicious patterns
    suspicious = []
    for ip, timestamps in attempts.items():
        # Sort timestamps
        timestamps.sort()

        # Check for >5 attempts in 10 minutes
        for i in range(len(timestamps)):
            window_end = timestamps[i] + timedelta(minutes=10)
            count = sum(1 for t in timestamps if timestamps[i] <= t <= window_end)

            if count > 5:
                suspicious.append({
                    'ip': ip,
                    'attempts': count,
                    'start_time': timestamps[i],
                    'end_time': window_end
                })
                break

    return suspicious

# Usage
suspicious_ips = detect_brute_force()
for item in suspicious_ips:
    print(f"ALERT: {item['attempts']} failures from {item['ip']} "
          f"between {item['start_time']} and {item['end_time']}")
```

## Security Monitoring Dashboard

### Daily Report Script

```python
from collections import Counter
from datetime import date
import re

def generate_daily_report():
    """Generate daily security report"""
    today = date.today().strftime('%Y-%m-%d')

    users = []
    permissions = []
    orgs = []
    ips = []

    with open('logs/rbac_security.log') as f:
        for line in f:
            if today in line and '403 Forbidden' in line:
                # Extract data
                user_match = re.search(r"User '(\w+)'", line)
                perm_match = re.search(r"permission '([\w.]+)'", line)
                org_match = re.search(r"Organization '([\w\s]+)' \(ID:", line)
                ip_match = re.search(r"IP ([\d.]+)", line)

                if user_match:
                    users.append(user_match.group(1))
                if perm_match:
                    permissions.append(perm_match.group(1))
                if org_match:
                    orgs.append(org_match.group(1))
                if ip_match:
                    ips.append(ip_match.group(1))

    # Generate report
    print(f"\n=== RBAC Security Report for {today} ===\n")

    print("Top Users with Failed Access:")
    for user, count in Counter(users).most_common(5):
        print(f"  {user}: {count} attempts")

    print("\nMost Denied Permissions:")
    for perm, count in Counter(permissions).most_common(5):
        print(f"  {perm}: {count} denials")

    print("\nOrganizations with Most Denials:")
    for org, count in Counter(orgs).most_common(5):
        print(f"  {org}: {count} denials")

    print("\nTop IP Addresses:")
    for ip, count in Counter(ips).most_common(5):
        print(f"  {ip}: {count} attempts")

# Run report
generate_daily_report()
```

## Related Documentation

- [Full RBAC Audit Logging Guide](RBAC_AUDIT_LOGGING.md)
- [Quick Reference](RBAC_AUDIT_LOGGING_QUICK_REFERENCE.md)
- [RBAC Implementation](../rbac/MOA_RBAC_IMPLEMENTATION.md)

---

**Note**: All examples assume Django development server running from `src/` directory with logging configured as shown above.
