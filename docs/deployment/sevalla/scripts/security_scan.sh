#!/bin/bash
# Security vulnerability scanning script
# Scans Python dependencies for known CVEs using pip-audit

set -e

echo "============================================"
echo "OBCMS Security Vulnerability Scan"
echo "============================================"
echo ""

# Check if pip-audit is installed
if ! command -v pip-audit &> /dev/null; then
    echo "❌ pip-audit not found. Installing..."
    pip install pip-audit
fi

echo "📦 Scanning dependencies for known vulnerabilities..."
echo ""

# Run pip-audit with JSON output for parsing
if pip-audit --requirement requirements/base.txt --format json > /tmp/pip-audit-results.json 2>&1; then
    echo "✅ No vulnerabilities found!"
    exit 0
else
    echo "⚠️  Vulnerabilities detected!"
    echo ""

    # Display human-readable output
    pip-audit --requirement requirements/base.txt

    echo ""
    echo "============================================"
    echo "Remediation Steps:"
    echo "1. Review vulnerabilities above"
    echo "2. Update affected packages: pip install --upgrade <package>"
    echo "3. Re-run this scan to verify fixes"
    echo "4. Update requirements/base.txt with new versions"
    echo "============================================"

    exit 1
fi
