#!/bin/bash
# Fail2Ban Intrusion Detection System Setup for OBCMS
#
# This script installs and configures Fail2Ban to:
# - Monitor Django logs for failed logins
# - Block IPs with repeated failures
# - Integrate with Django Axes for account lockout
#
# Requirements:
# - Ubuntu/Debian system
# - Root/sudo access
# - Django logs at /var/log/obcms/django.log
#
# Usage:
#   sudo bash scripts/setup_fail2ban.sh

set -e

echo "============================================"
echo "Fail2Ban IDS Setup for OBCMS"
echo "============================================"
echo ""

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo "❌ This script must be run as root (sudo)"
   exit 1
fi

# Install Fail2Ban
echo "📦 Installing Fail2Ban..."
apt-get update
apt-get install -y fail2ban

# Create filter for Django authentication
echo "📝 Creating Django authentication filter..."
cat > /etc/fail2ban/filter.d/django-auth.conf <<'EOF'
# Fail2Ban filter for Django authentication failures
#
# Matches lines like:
# [WARNING] 2025-10-03 12:34:56 django.security Failed login attempt | Username: admin | IP: 192.168.1.100
#
[Definition]
failregex = ^.*Failed login attempt \| Username: .* \| IP: <HOST>
            ^.*Unauthorized access attempt \| .* \| IP: <HOST>
            ^.*Permission denied \| .* \| IP: <HOST>
ignoreregex =
EOF

# Create jail for Django
echo "📝 Creating Django jail configuration..."
cat > /etc/fail2ban/jail.d/django.local <<EOF
# Django authentication jail
[django-auth]
enabled = true
port = http,https
filter = django-auth
logpath = /var/log/obcms/django.log
maxretry = 5
findtime = 600
bantime = 3600
action = iptables-multiport[name=Django, port="http,https", protocol=tcp]
         sendmail-whois[name=Django, dest=security@oobc.gov.ph]

# Django brute force jail (more aggressive)
[django-bruteforce]
enabled = true
port = http,https
filter = django-auth
logpath = /var/log/obcms/django.log
maxretry = 10
findtime = 300
bantime = 86400
action = iptables-multiport[name=Django-BF, port="http,https", protocol=tcp]
EOF

# Create filter for nginx
echo "📝 Creating nginx filter (if using nginx)..."
cat > /etc/fail2ban/jail.d/nginx.local <<EOF
# Nginx jails
[nginx-http-auth]
enabled = true
port = http,https
logpath = /var/log/nginx/error.log

[nginx-limit-req]
enabled = true
port = http,https
logpath = /var/log/nginx/error.log
maxretry = 10
findtime = 600
bantime = 3600

[nginx-botsearch]
enabled = true
port = http,https
logpath = /var/log/nginx/access.log
maxretry = 20
findtime = 600
bantime = 86400
EOF

# Ensure log directory exists
echo "📁 Ensuring log directory exists..."
mkdir -p /var/log/obcms
chown -R www-data:www-data /var/log/obcms
chmod 755 /var/log/obcms

# Test configuration
echo "🧪 Testing Fail2Ban configuration..."
fail2ban-client -t

# Start Fail2Ban
echo "🚀 Starting Fail2Ban service..."
systemctl enable fail2ban
systemctl restart fail2ban

# Display status
echo ""
echo "✅ Fail2Ban installed and configured successfully!"
echo ""
echo "Active jails:"
fail2ban-client status

echo ""
echo "============================================"
echo "Fail2Ban Configuration Complete"
echo "============================================"
echo ""
echo "Useful commands:"
echo "  - View status:        sudo fail2ban-client status"
echo "  - View Django jail:   sudo fail2ban-client status django-auth"
echo "  - Unban IP:           sudo fail2ban-client set django-auth unbanip <IP>"
echo "  - View banned IPs:    sudo fail2ban-client get django-auth banip"
echo "  - View logs:          sudo tail -f /var/log/fail2ban.log"
echo ""
echo "Log locations:"
echo "  - Fail2Ban logs:      /var/log/fail2ban.log"
echo "  - Django logs:        /var/log/obcms/django.log"
echo "  - Banned IPs:         sudo iptables -L -n | grep DROP"
echo ""
echo "⚠️  Important: Ensure Django logs are writing to /var/log/obcms/django.log"
echo ""
