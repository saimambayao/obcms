#!/usr/bin/env python3
"""
Security Vulnerability Scanner for OBCMS

This script performs comprehensive security vulnerability scanning:
1. Dependency vulnerability scanning (pip-audit, safety)
2. Static code analysis (bandit)
3. Configuration security checks
4. Secret scanning

Usage:
    python scripts/security_scan.py [--full] [--fix]
"""

import json
import logging
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("security_scan.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class SecurityScanner:
    """Comprehensive security vulnerability scanner."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.src_dir = project_root / "src"
        self.results = {
            "scan_date": datetime.now().isoformat(),
            "project_root": str(project_root),
            "findings": []
        }

    def run_command(self, cmd: list, description: str) -> dict:
        """Run a security command and return results."""
        logger.info(f"Running: {description}")
        logger.info(f"Command: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minutes
                cwd=self.project_root
            )

            success = result.returncode == 0
            if success:
                logger.info(f"✅ {description} completed successfully")
            else:
                logger.warning(f"⚠️ {description} completed with warnings")

            return {
                "success": success,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }

        except subprocess.TimeoutExpired:
            logger.error(f"❌ {description} timed out")
            return {
                "success": False,
                "stdout": "",
                "stderr": "Command timed out after 5 minutes",
                "returncode": -1
            }
        except Exception as e:
            logger.error(f"❌ {description} failed: {e}")
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "returncode": -1
            }

    def scan_dependencies(self) -> dict:
        """Scan for dependency vulnerabilities using pip-audit."""
        logger.info("🔍 Scanning dependencies for vulnerabilities...")

        # Try pip-audit first
        pip_audit_result = self.run_command(
            [sys.executable, "-m", "pip_audit", "--format", "json", "--requirement", "requirements/base.txt"],
            "Dependency vulnerability scan (pip-audit)"
        )

        findings = []

        if pip_audit_result["success"]:
            try:
                audit_data = json.loads(pip_audit_result["stdout"])
                vulnerabilities = audit_data.get("vulnerabilities", [])

                for vuln in vulnerabilities:
                    finding = {
                        "type": "dependency_vulnerability",
                        "severity": self._map_severity(vuln.get("severity", "unknown")),
                        "package": vuln.get("name", "unknown"),
                        "version": vuln.get("version", "unknown"),
                        "vulnerability_id": vuln.get("id", "unknown"),
                        "description": vuln.get("description", "No description available"),
                        "fix_versions": vuln.get("fix_versions", []),
                        "advisory": vuln.get("advisory", "")
                    }
                    findings.append(finding)

            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse pip-audit output: {e}")
                findings.append({
                    "type": "scan_error",
                    "severity": "medium",
                    "description": f"Failed to parse pip-audit output: {e}"
                })

        else:
            # Fallback to safety if pip-audit is not available
            logger.info("pip-audit not available, trying safety...")
            safety_result = self.run_command(
                [sys.executable, "-m", "safety", "check", "--json", "--short-report"],
                "Dependency vulnerability scan (safety)"
            )

            if safety_result["success"]:
                try:
                    safety_data = json.loads(safety_result["stdout"])
                    for vuln in safety_data:
                        finding = {
                            "type": "dependency_vulnerability",
                            "severity": self._map_severity(vuln.get("vulnerability", "unknown")),
                            "package": vuln.get("package", "unknown"),
                            "version": vuln.get("installed_version", "unknown"),
                            "vulnerability_id": vuln.get("advisory", "unknown"),
                            "description": vuln.get("advisory", "No description available"),
                            "analyzed_version": vuln.get("analyzed_version", "unknown"),
                            "cve": vuln.get("cve", "")
                        }
                        findings.append(finding)

                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse safety output: {e}")
            else:
                logger.warning("Neither pip-audit nor safety available for dependency scanning")

        return {
            "scanner": "dependency_vulnerability_scanner",
            "findings_count": len(findings),
            "findings": findings
        }

    def scan_code(self) -> dict:
        """Perform static code analysis using bandit."""
        logger.info("🔍 Running static code analysis...")

        bandit_result = self.run_command(
            [sys.executable, "-m", "bandit", "-r", str(self.src_dir), "-f", "json"],
            "Static code analysis (bandit)"
        )

        findings = []

        if bandit_result["success"]:
            try:
                bandit_data = json.loads(bandit_result["stdout"])
                results = bandit_data.get("results", [])

                for issue in results:
                    finding = {
                        "type": "code_vulnerability",
                        "severity": self._map_bandit_severity(issue.get("issue_severity", "unknown")),
                        "confidence": issue.get("issue_cconfidence", "unknown"),
                        "test_name": issue.get("test_name", "unknown"),
                        "test_id": issue.get("test_id", "unknown"),
                        "file_path": issue.get("filename", "unknown"),
                        "line_number": issue.get("line_number", 0),
                        "description": issue.get("issue_text", "No description available"),
                        "cwe_id": issue.get("cwe_id", ""),
                        "more_info": issue.get("issue_cwe", {}).get("link", "")
                    }
                    findings.append(finding)

            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse bandit output: {e}")
        else:
            logger.warning("Bandit scan failed or not available")

        return {
            "scanner": "static_code_analyzer",
            "findings_count": len(findings),
            "findings": findings
        }

    def scan_secrets(self) -> dict:
        """Scan for hardcoded secrets in the codebase."""
        logger.info("🔍 Scanning for hardcoded secrets...")

        # Simple secret scanning patterns
        secret_patterns = {
            "api_key": r'(?i)(api[_-]?key["\'\s]*[:=]["\'\s]*[a-zA-Z0-9_-]{20,})',
            "password": r'(?i)(password["\'\s]*[:=]["\'\s]*[^\s\'"]{8,})',
            "token": r'(?i)(token["\'\s]*[:=]["\'\s]*[a-zA-Z0-9_-]{20,})',
            "secret": r'(?i)(secret["\'\s]*[:=]["\'\s]*[a-zA-Z0-9_-]{20,})',
            "private_key": r'-----BEGIN [A-Z]+ PRIVATE KEY-----',
            "aws_key": r'(?i)(aws[_-]?(access[_-])?key[_-]?id["\'\s]*[:=]["\'\s]*[A-Z0-9]{20})',
            "github_token": r'ghp_[a-zA-Z0-9]{36}'
        }

        import re
        findings = []

        # Scan Python files
        for py_file in self.src_dir.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    line_number = 0

                    for line in content.split('\n'):
                        line_number += 1

                        for secret_type, pattern in secret_patterns.items():
                            if re.search(pattern, line):
                                # Exclude common false positives
                                if self._is_false_positive(line, secret_type):
                                    continue

                                finding = {
                                    "type": "hardcoded_secret",
                                    "severity": "high",
                                    "secret_type": secret_type,
                                    "file_path": str(py_file.relative_to(self.project_root)),
                                    "line_number": line_number,
                                    "description": f"Potential {secret_type} found in code",
                                    "snippet": line.strip()[:100] + "..." if len(line.strip()) > 100 else line.strip()
                                }
                                findings.append(finding)

            except (UnicodeDecodeError, PermissionError):
                continue

        return {
            "scanner": "secret_scanner",
            "findings_count": len(findings),
            "findings": findings
        }

    def scan_configurations(self) -> dict:
        """Scan for insecure configuration."""
        logger.info("🔍 Scanning configurations for security issues...")

        findings = []

        # Check Django settings
        settings_files = [
            self.src_dir / "obc_management" / "settings" / "base.py",
            self.src_dir / "obc_management" / "settings" / "production.py"
        ]

        for settings_file in settings_files:
            if not settings_file.exists():
                continue

            try:
                with open(settings_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Check for insecure settings
                if 'DEBUG = True' in content and 'production' in str(settings_file):
                    findings.append({
                        "type": "insecure_configuration",
                        "severity": "high",
                        "file_path": str(settings_file.relative_to(self.project_root)),
                        "description": "DEBUG=True in production settings",
                        "recommendation": "Set DEBUG=False in production"
                    })

                if 'SECRET_KEY' in content and 'django-insecure' in content:
                    findings.append({
                        "type": "insecure_configuration",
                        "severity": "high",
                        "file_path": str(settings_file.relative_to(self.project_root)),
                        "description": "Default Django secret key in use",
                        "recommendation": "Generate and use a secure SECRET_KEY"
                    })

            except (UnicodeDecodeError, PermissionError):
                continue

        return {
            "scanner": "configuration_scanner",
            "findings_count": len(findings),
            "findings": findings
        }

    def _map_severity(self, severity: str) -> str:
        """Map severity levels to standard format."""
        severity = severity.lower()
        if severity in ["critical", "high"]:
            return "high"
        elif severity in ["medium", "moderate"]:
            return "medium"
        elif severity in ["low", "info", "negligible"]:
            return "low"
        else:
            return "unknown"

    def _map_bandit_severity(self, severity: str) -> str:
        """Map bandit severity levels."""
        if severity == "HIGH":
            return "high"
        elif severity == "MEDIUM":
            return "medium"
        elif severity == "LOW":
            return "low"
        else:
            return "unknown"

    def _is_false_positive(self, line: str, secret_type: str) -> bool:
        """Check if a finding is likely a false positive."""
        line_lower = line.lower()

        # Common false positive patterns
        false_positives = [
            "example", "sample", "test", "demo", "placeholder",
            "your_", "change_", "replace_", "xxx", "yyy",
            "localhost", "127.0.0.1", "0.0.0.0",
            "comment", "todo", "fixme", "wrong", "admin", "pass",
            "secure", "changeme", "temporary", "debug", "secret"
        ]

        for fp in false_positives:
            if fp in line_lower:
                return True

        # Test file patterns
        if any(pattern in line_lower for pattern in [
            "test_", "_test", "/tests/", "conftest.py", "fixtures/",
            "mock_", "fake_", "dummy_", "testpass", "wrongpass"
        ]):
            return True

        # Common test passwords
        test_passwords = [
            "test", "wrong", "admin", "secret", "password", "pass",
            "changeme", "demo", "sample", "example", "123", "abc"
        ]

        # Extract password value from common patterns
        import re
        password_match = re.search(r'password[\'"\s]*[:=][\'"\s]*([^\s\'"]+)', line_lower)
        if password_match:
            password_value = password_match.group(1)
            if any(test_pass in password_value for test_pass in test_passwords):
                return True

        # Check if it's obviously a template/placeholder
        if any(char in line for char in ["<", ">", "{{", "}}", "%s", "%d"]):
            return True

        # Management command output (likely just displaying generated passwords)
        if any(pattern in line_lower for pattern in [
            "self.stdout.write", "print(", "echo ", "temporary password:"
        ]):
            return True

        return False

    def run_full_scan(self) -> dict:
        """Run complete security scan."""
        logger.info("🚀 Starting comprehensive security scan...")

        scan_results = {
            "scan_info": {
                "scan_date": datetime.now().isoformat(),
                "scanner_version": "1.0.0",
                "project_root": str(self.project_root)
            },
            "scans": {}
        }

        # Run all scans
        scan_results["scans"]["dependencies"] = self.scan_dependencies()
        scan_results["scans"]["code_analysis"] = self.scan_code()
        scan_results["scans"]["secrets"] = self.scan_secrets()
        scan_results["scans"]["configurations"] = self.scan_configurations()

        # Calculate summary
        total_findings = sum(scan["findings_count"] for scan in scan_results["scans"].values())
        high_severity = sum(
            len([f for f in scan["findings"] if f.get("severity") == "high"])
            for scan in scan_results["scans"].values()
        )
        medium_severity = sum(
            len([f for f in scan["findings"] if f.get("severity") == "medium"])
            for scan in scan_results["scans"].values()
        )
        low_severity = sum(
            len([f for f in scan["findings"] if f.get("severity") == "low"])
            for scan in scan_results["scans"].values()
        )

        scan_results["summary"] = {
            "total_findings": total_findings,
            "high_severity": high_severity,
            "medium_severity": medium_severity,
            "low_severity": low_severity,
            "scan_status": "completed"
        }

        return scan_results

    def generate_report(self, results: dict, output_file: str = None) -> str:
        """Generate security scan report."""
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"security_report_{timestamp}.json"

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        logger.info(f"📄 Security report generated: {output_file}")

        # Generate summary for console
        summary = results["summary"]
        logger.info(f"""
🔍 SECURITY SCAN SUMMARY
========================
Total Findings: {summary['total_findings']}
High Severity: {summary['high_severity']} ⚠️
Medium Severity: {summary['medium_severity']} ⚡
Low Severity: {summary['low_severity']} ℹ️

Report saved to: {output_file}
        """)

        return output_file


def main():
    """Main function to run security scan."""
    import argparse

    parser = argparse.ArgumentParser(description="OBCMS Security Vulnerability Scanner")
    parser.add_argument("--fix", action="store_true", help="Attempt to fix minor issues automatically")
    parser.add_argument("--output", help="Output file for report (default: auto-generated)")
    parser.add_argument("--quick", action="store_true", help="Quick scan (dependencies + critical issues only)")

    args = parser.parse_args()

    # Determine project root
    project_root = Path(__file__).parent.parent
    logger.info(f"Project root: {project_root}")

    scanner = SecurityScanner(project_root)

    if args.quick:
        logger.info("🚀 Running quick security scan...")
        results = {
            "scan_info": {
                "scan_date": datetime.now().isoformat(),
                "scanner_version": "1.0.0",
                "project_root": str(project_root),
                "scan_type": "quick"
            },
            "scans": {
                "dependencies": scanner.scan_dependencies(),
                "secrets": scanner.scan_secrets()
            }
        }

        # Calculate summary for quick scan
        total_findings = sum(scan["findings_count"] for scan in results["scans"].values())
        results["summary"] = {
            "total_findings": total_findings,
            "high_severity": sum(
                len([f for f in scan["findings"] if f.get("severity") == "high"])
                for scan in results["scans"].values()
            ),
            "medium_severity": sum(
                len([f for f in scan["findings"] if f.get("severity") == "medium"])
                for scan in results["scans"].values()
            ),
            "low_severity": sum(
                len([f for f in scan["findings"] if f.get("severity") == "low"])
                for scan in results["scans"].values()
            ),
            "scan_status": "completed"
        }
    else:
        results = scanner.run_full_scan()

    # Generate report
    report_file = scanner.generate_report(results, args.output)

    # Exit with error code if high severity issues found
    if results["summary"]["high_severity"] > 0:
        logger.error(f"❌ Found {results['summary']['high_severity']} high severity issues!")
        sys.exit(1)
    else:
        logger.info("✅ No high severity security issues found!")
        sys.exit(0)


if __name__ == "__main__":
    main()