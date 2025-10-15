#!/usr/bin/env python3
"""
Security Monitoring and Alerting Script

This script provides automated security monitoring for OBCMS:
- Periodic vulnerability scanning
- Configuration drift detection
- Security compliance checks
- Alert generation for security issues

Usage:
    python scripts/security_monitor.py --check
    python scripts/security_monitor.py --monitor
"""

import json
import logging
import smtplib
import sys
import time
from datetime import datetime, timedelta
from email.mime.text import MimeText
from pathlib import Path

# Import our security scanner
sys.path.append(str(Path(__file__).parent))
from security_scan import SecurityScanner

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("security_monitor.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class SecurityMonitor:
    """Security monitoring and alerting system."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.scanner = SecurityScanner(project_root)
        self.alert_threshold = {
            "high_severity": 0,  # Any high severity issue triggers alert
            "medium_severity": 5,  # 5+ medium issues trigger alert
            "total_findings": 20   # 20+ total issues trigger alert
        }

    def check_security_status(self) -> dict:
        """Perform comprehensive security check."""
        logger.info("🔍 Running security monitoring check...")

        # Run quick security scan
        results = self.scanner.run_quick_scan()

        # Add monitoring metadata
        results["monitoring"] = {
            "check_timestamp": datetime.now().isoformat(),
            "monitor_version": "1.0.0",
            "alert_triggered": self._should_alert(results["summary"])
        }

        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"security_monitor_{timestamp}.json"

        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        logger.info(f"📄 Security monitor report saved: {report_file}")
        return results

    def _should_alert(self, summary: dict) -> bool:
        """Determine if security alert should be triggered."""
        if summary["high_severity"] > self.alert_threshold["high_severity"]:
            return True
        if summary["medium_severity"] > self.alert_threshold["medium_severity"]:
            return True
        if summary["total_findings"] > self.alert_threshold["total_findings"]:
            return True
        return False

    def send_alert(self, results: dict, recipients: list = None):
        """Send security alert notification."""
        if not recipients:
            logger.warning("No alert recipients configured")
            return

        summary = results["summary"]

        subject = f"🚨 OBCMS Security Alert - {summary['high_severity']} High, {summary['medium_severity']} Medium Issues"

        body = f"""
OBCMS Security Monitoring Alert

Scan Date: {results['monitoring']['check_timestamp']}
Total Issues: {summary['total_findings']}
High Severity: {summary['high_severity']} ⚠️
Medium Severity: {summary['medium_severity']} ⚡
Low Severity: {summary['low_severity']} ℹ️

High Severity Issues Requiring Immediate Attention:
"""

        # Add high severity findings
        for scan_type, scan_data in results["scans"].items():
            high_issues = [f for f in scan_data["findings"] if f.get("severity") == "high"]
            if high_issues:
                body += f"\n{scan_type.upper()}:\n"
                for issue in high_issues[:5]:  # Limit to first 5 issues
                    body += f"  • {issue.get('description', 'Unknown issue')}\n"
                    body += f"    File: {issue.get('file_path', 'Unknown')}\n"
                    body += f"    Line: {issue.get('line_number', 'Unknown')}\n\n"

        body += f"""
Full report available in the security monitoring logs.

Please review and address these issues promptly.

Automated Security Monitor
OBCMS Development Team
"""

        # TODO: Configure email settings properly
        logger.warning("Email alerting not configured - see security_monitor.py")
        logger.info(f"ALERT: {subject}")
        logger.info(f"Would send to: {recipients}")
        logger.info(f"Body:\n{body}")

    def monitor_loop(self, interval_minutes: int = 60):
        """Run continuous security monitoring."""
        logger.info(f"🔄 Starting continuous security monitoring (interval: {interval_minutes} minutes)")

        while True:
            try:
                results = self.check_security_status()

                if results["monitoring"]["alert_triggered"]:
                    logger.error("🚨 Security alert triggered!")
                    self.send_alert(results)
                else:
                    logger.info("✅ Security check passed - no alerts needed")

                # Cleanup old reports (keep last 10)
                self._cleanup_old_reports()

                logger.info(f"⏰ Next check in {interval_minutes} minutes...")
                time.sleep(interval_minutes * 60)

            except KeyboardInterrupt:
                logger.info("🛑 Security monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"❌ Monitoring error: {e}")
                time.sleep(300)  # Wait 5 minutes before retrying

    def _cleanup_old_reports(self, keep_count: int = 10):
        """Clean up old security monitoring reports."""
        reports = list(self.project_root.glob("security_monitor_*.json"))
        reports.sort(key=lambda x: x.stat().st_mtime, reverse=True)

        for old_report in reports[keep_count:]:
            try:
                old_report.unlink()
                logger.debug(f"Cleaned up old report: {old_report}")
            except Exception as e:
                logger.warning(f"Failed to clean up {old_report}: {e}")

    def check_configuration_drift(self) -> dict:
        """Check for configuration security drift."""
        logger.info("🔍 Checking configuration security drift...")

        findings = []

        # Check Django settings files
        settings_files = [
            self.project_root / "src" / "obc_management" / "settings" / "base.py",
            self.project_root / "src" / "obc_management" / "settings" / "production.py"
        ]

        for settings_file in settings_files:
            if not settings_file.exists():
                continue

            try:
                with open(settings_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Security configuration checks
                if "SECURE_SSL_REDIRECT = False" in content and "production" in str(settings_file):
                    findings.append({
                        "type": "configuration_drift",
                        "severity": "high",
                        "file_path": str(settings_file.relative_to(self.project_root)),
                        "description": "SSL redirect disabled in production",
                        "recommendation": "Enable SECURE_SSL_REDIRECT=True in production"
                    })

                if "SESSION_COOKIE_SECURE = False" in content and "production" in str(settings_file):
                    findings.append({
                        "type": "configuration_drift",
                        "severity": "high",
                        "file_path": str(settings_file.relative_to(self.project_root)),
                        "description": "Insecure session cookies in production",
                        "recommendation": "Enable SESSION_COOKIE_SECURE=True in production"
                    })

            except Exception as e:
                logger.warning(f"Could not check {settings_file}: {e}")

        return {
            "check_type": "configuration_drift",
            "findings_count": len(findings),
            "findings": findings
        }


def main():
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(description="OBCMS Security Monitoring")
    parser.add_argument("--check", action="store_true", help="Run one-time security check")
    parser.add_argument("--monitor", action="store_true", help="Run continuous monitoring")
    parser.add_argument("--interval", type=int, default=60, help="Monitoring interval in minutes")
    parser.add_argument("--config-drift", action="store_true", help="Check configuration drift")

    args = parser.parse_args()

    project_root = Path(__file__).parent.parent
    monitor = SecurityMonitor(project_root)

    if args.check:
        results = monitor.check_security_status()

        if results["monitoring"]["alert_triggered"]:
            logger.error("🚨 Security issues found requiring attention!")
            sys.exit(1)
        else:
            logger.info("✅ No critical security issues found")
            sys.exit(0)

    elif args.config_drift:
        results = monitor.check_configuration_drift()
        logger.info(f"Configuration drift check completed: {results['findings_count']} issues found")

        if results["findings_count"] > 0:
            for finding in results["findings"]:
                logger.warning(f"⚠️ {finding['description']} in {finding['file_path']}")

    elif args.monitor:
        logger.info("🔄 Starting continuous security monitoring...")
        monitor.monitor_loop(args.interval)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()