# OBCMS Penetration Testing Checklist & Procedures

**Version:** 1.0
**Date:** January 2025
**Status:** Pre-Production Testing Guide

---

## Overview

This comprehensive checklist guides penetration testing of OBCMS before production deployment.

**Testing Objectives:**
1. Identify security vulnerabilities
2. Validate security controls
3. Assess compliance readiness
4. Provide remediation guidance

---

## Pre-Test Preparation

### Scope Definition

**In-Scope:**
- [ ] Web application (all modules)
- [ ] REST API endpoints
- [ ] Authentication/authorization
- [ ] File upload functionality
- [ ] Admin panel
- [ ] Database queries

**Out-of-Scope:**
- [ ] Physical security
- [ ] Social engineering
- [ ] Denial of Service (intentional)
- [ ] Third-party services (Cloudflare, AWS)

### Test Environment

- [ ] **Use staging environment** (NOT production)
- [ ] **Backup database** before testing
- [ ] **Notify team** of testing schedule
- [ ] **Obtain written authorization**

### Tools Required

**Automated Scanners:**
- [ ] OWASP ZAP
- [ ] Burp Suite Community/Pro
- [ ] Nikto
- [ ] SQLMap

**Manual Testing:**
- [ ] Firefox/Chrome with DevTools
- [ ] Postman/Insomnia (API testing)
- [ ] cURL

---

## 1. Authentication & Session Management

### 1.1 Login Mechanism

- [ ] **Test weak passwords** (should be rejected)
  ```
  Passwords to test:
  - "password"
  - "12345678"
  - "admin123"
  Expected: Validation error (12-char minimum)
  ```

- [ ] **Test SQL injection in login**
  ```
  Username: admin' OR '1'='1
  Password: anything
  Expected: Login fails, no SQL error exposed
  ```

- [ ] **Test XSS in login form**
  ```
  Username: <script>alert('XSS')</script>
  Expected: Input sanitized, no script execution
  ```

- [ ] **Test account lockout** (django-axes)
  ```
  Attempt 6 failed logins
  Expected: Account locked after 5 attempts
  ```

- [ ] **Test lockout bypass**
  ```
  Try different IP after lockout
  Expected: Still locked (tracks username + IP)
  ```

### 1.2 Session Security

- [ ] **Check session cookie flags**
  ```
  Expected flags:
  - HttpOnly: Yes
  - Secure: Yes (HTTPS)
  - SameSite: Strict
  ```

- [ ] **Test session fixation**
  ```
  1. Get session ID
  2. Login
  3. Check if session ID changed
  Expected: New session ID after login
  ```

- [ ] **Test concurrent sessions**
  ```
  Login on 2 browsers with same account
  Expected: Both sessions valid (allowed)
  ```

- [ ] **Test session timeout**
  ```
  Idle for > 30 minutes
  Expected: Auto-logout
  ```

### 1.3 Password Reset

- [ ] **Test password reset flow**
- [ ] **Check reset token expiration** (24 hours)
- [ ] **Test reset token reuse** (should be single-use)
- [ ] **Test reset token guessing** (should be cryptographically random)

### 1.4 JWT Token Security

- [ ] **Check JWT token format** (Header.Payload.Signature)
- [ ] **Verify JWT signature** (cannot be tampered)
- [ ] **Test expired JWT** (should be rejected)
- [ ] **Test JWT without signature** (should be rejected)
- [ ] **Test token blacklisting** (logout should invalidate token)

---

## 2. Authorization & Access Control

### 2.1 Vertical Privilege Escalation

- [ ] **Test regular user accessing admin panel**
  ```
  Login as regular user
  Access: /admin/
  Expected: 403 Forbidden or redirect
  ```

- [ ] **Test API endpoint authorization**
  ```
  GET /api/users/  (as non-admin)
  Expected: 403 Forbidden
  ```

- [ ] **Test direct object reference**
  ```
  Access other user's profile: /api/users/99/
  Expected: 403 or 404 (not own ID)
  ```

### 2.2 Horizontal Privilege Escalation

- [ ] **Test MANA user accessing other regions**
  ```
  Login as Region IX MANA user
  Try accessing Region XII data
  Expected: Blocked by MANAAccessControlMiddleware
  ```

- [ ] **Test OBC data isolation**
  ```
  User A tries to edit User B's community data
  Expected: Permission denied
  ```

### 2.3 IDOR (Insecure Direct Object Reference)

- [ ] **Test sequential ID guessing**
  ```
  /communities/barangay/1/
  /communities/barangay/2/
  /communities/barangay/999/
  Expected: Only authorized data visible
  ```

- [ ] **Test UUID guessing** (if using UUIDs)

---

## 3. Input Validation & Injection Attacks

### 3.1 SQL Injection

- [ ] **Test in search fields**
  ```
  Search: ' OR 1=1--
  Expected: Escaped by Django ORM, no error
  ```

- [ ] **Test in API parameters**
  ```
  GET /api/communities/?region_id=1' OR '1'='1
  Expected: Parameterized query, no injection
  ```

- [ ] **Test in filters**
  ```
  ?created_at__gte=2025-01-01'; DROP TABLE--
  Expected: Invalid date format error, no SQL
  ```

- [ ] **Run SQLMap automated scan**
  ```bash
  sqlmap -u "http://staging.obcms.gov.ph/api/communities/?search=test" \
         --cookie="sessionid=..." \
         --level=5 --risk=3
  Expected: No injection points found
  ```

### 3.2 Cross-Site Scripting (XSS)

- [ ] **Test reflected XSS in search**
  ```
  Search: <script>alert(document.cookie)</script>
  Expected: Input escaped in output
  ```

- [ ] **Test stored XSS in profiles**
  ```
  Organization name: <img src=x onerror=alert('XSS')>
  Expected: Sanitized on save or display
  ```

- [ ] **Test DOM-based XSS**
  ```
  Check JavaScript that manipulates DOM
  Expected: Uses .textContent, not .innerHTML
  ```

- [ ] **Test in file uploads**
  ```
  Upload HTML file with <script> tags
  Expected: Content-type validated, won't execute
  ```

### 3.3 Command Injection

- [ ] **Test in any file processing**
  ```
  Filename: test; rm -rf /
  Expected: Filename sanitized, no shell execution
  ```

- [ ] **Test in report generation** (if any shell commands)

### 3.4 XML External Entity (XXE)

- [ ] **Test in document uploads** (if accepting XML)
  ```xml
  <!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
  <root>&xxe;</root>
  Expected: XML parsing disabled or validated
  ```

---

## 4. File Upload Security

### 4.1 File Type Validation

- [ ] **Test executable upload**
  ```
  Upload: malware.exe
  Expected: Rejected (not in whitelist)
  ```

- [ ] **Test PHP/Python shell disguised as image**
  ```
  Rename shell.php to shell.jpg
  Expected: Content-type verification detects mismatch
  ```

- [ ] **Test double extension**
  ```
  Upload: image.jpg.php
  Expected: Only .php extension checked, rejected
  ```

### 4.2 File Size Limits

- [ ] **Test oversized file**
  ```
  Upload 100MB file
  Expected: Rejected (max 5-10MB)
  ```

- [ ] **Test zip bomb**
  ```
  Upload compressed file that expands to 10GB
  Expected: Size limit prevents extraction
  ```

### 4.3 Malware Detection

- [ ] **Test EICAR test file** (if ClamAV enabled)
  ```
  Upload EICAR standard test file
  Expected: Detected as malware, upload blocked
  ```

### 4.4 Path Traversal

- [ ] **Test malicious filename**
  ```
  Filename: ../../../../../../etc/passwd
  Expected: Sanitized to "etcpasswd"
  ```

---

## 5. API Security

### 5.1 Rate Limiting

- [ ] **Test authentication endpoint throttling**
  ```bash
  for i in {1..10}; do
    curl -X POST https://staging.obcms.gov.ph/api/token/ \
         -d "username=test&password=wrong"
  done
  Expected: 429 Too Many Requests after 5 attempts
  ```

- [ ] **Test API rate limiting**
  ```bash
  for i in {1..150}; do
    curl https://staging.obcms.gov.ph/api/communities/
  done
  Expected: 429 after 100 requests (anon)
  ```

### 5.2 API Authentication

- [ ] **Test API without authentication**
  ```
  GET /api/communities/
  Expected: 401 Unauthorized
  ```

- [ ] **Test with invalid JWT**
  ```
  Authorization: Bearer invalid.token.here
  Expected: 401 Unauthorized
  ```

### 5.3 Mass Assignment

- [ ] **Test creating user with is_staff=True**
  ```json
  POST /api/users/
  {
    "username": "hacker",
    "password": "test123456789",
    "is_staff": true
  }
  Expected: is_staff ignored (not in serializer)
  ```

---

## 6. CSRF & CORS

### 6.1 CSRF Protection

- [ ] **Test POST without CSRF token**
  ```
  POST /communities/create/
  (no csrfmiddlewaretoken)
  Expected: 403 Forbidden
  ```

- [ ] **Test CSRF token from different session**
  ```
  Use token from User A session in User B request
  Expected: Invalid CSRF token error
  ```

### 6.2 CORS Configuration

- [ ] **Test cross-origin request from unauthorized domain**
  ```
  Origin: https://evil.com
  Expected: CORS error, request blocked
  ```

- [ ] **Test CORS from allowed domain**
  ```
  Origin: https://obcms.gov.ph
  Expected: Access-Control-Allow-Origin header present
  ```

---

## 7. Security Headers

### 7.1 Check Security Headers

```bash
curl -I https://staging.obcms.gov.ph
```

**Expected Headers:**

- [ ] `Strict-Transport-Security: max-age=31536000; includeSubDomains; preload`
- [ ] `X-Frame-Options: DENY`
- [ ] `X-Content-Type-Options: nosniff`
- [ ] `Content-Security-Policy: default-src 'self'; ...`
- [ ] `X-XSS-Protection: 1; mode=block` (legacy browsers)

### 7.2 Test Clickjacking Protection

```html
<!-- Try embedding OBCMS in iframe -->
<iframe src="https://staging.obcms.gov.ph"></iframe>
```

**Expected:** Blocked by `X-Frame-Options: DENY`

---

## 8. Business Logic Flaws

### 8.1 Workflow Bypass

- [ ] **Test skipping required steps**
  ```
  Submit assessment without workshop attendance
  Expected: Validation error
  ```

- [ ] **Test modifying submitted data**
  ```
  Edit assessment after submission
  Expected: Only draft assessments editable
  ```

### 8.2 Data Validation

- [ ] **Test negative numbers** (where not allowed)
- [ ] **Test invalid date ranges**
- [ ] **Test duplicate submissions**

---

## 9. Information Disclosure

### 9.1 Error Messages

- [ ] **Trigger 404 error**
  ```
  GET /nonexistent/page/
  Expected: Generic 404, no stack trace
  ```

- [ ] **Trigger 500 error**
  ```
  Expected: Generic error page, no DEBUG info
  ```

- [ ] **Test SQL error disclosure**
  ```
  Invalid query parameter
  Expected: No database error details exposed
  ```

### 9.2 Directory Listing

- [ ] **Test media directory access**
  ```
  GET /media/
  Expected: 403 Forbidden or 404
  ```

- [ ] **Test static directory**
  ```
  GET /static/
  Expected: No directory listing
  ```

### 9.3 Sensitive Data in URLs

- [ ] **Check for passwords in GET parameters**
- [ ] **Check for API keys in URLs**
- [ ] **Check browser history for sensitive data**

---

## 10. SSL/TLS Configuration

### 10.1 SSL Labs Test

```
https://www.ssllabs.com/ssltest/analyze.html?d=staging.obcms.gov.ph
```

**Expected Grade:** A or A+

### 10.2 Check for Weak Ciphers

```bash
nmap --script ssl-enum-ciphers -p 443 staging.obcms.gov.ph
```

**Expected:** Only strong ciphers (TLS 1.2+, AES-256)

---

## 11. Automated Security Scans

### 11.1 OWASP ZAP Scan

```bash
# Start ZAP daemon
zap.sh -daemon -port 8080

# Spider the site
curl "http://localhost:8080/JSON/spider/action/scan/?url=https://staging.obcms.gov.ph"

# Active scan
curl "http://localhost:8080/JSON/ascan/action/scan/?url=https://staging.obcms.gov.ph"

# Generate report
curl "http://localhost:8080/OTHER/core/other/htmlreport/" > zap_report.html
```

### 11.2 Nikto Web Scanner

```bash
nikto -h https://staging.obcms.gov.ph -o nikto_report.html
```

### 11.3 Django Security Check

```bash
cd src
python manage.py check --deploy
```

**Expected:** No warnings (or only dev-related warnings)

---

## Test Report Template

```markdown
# OBCMS Penetration Test Report

**Date:** [Date]
**Tester:** [Name]
**Scope:** [URLs tested]

## Executive Summary
- Total vulnerabilities found: X
- Critical: 0
- High: 0
- Medium: X
- Low: X

## Findings

### Finding 1: [Title]
**Severity:** Medium
**CVSS Score:** 5.3
**Description:** [Details]
**Steps to Reproduce:**
1. [Step 1]
2. [Step 2]

**Evidence:** [Screenshot/logs]
**Recommendation:** [Fix]
**Remediation Effort:** [Hours/days]

## Conclusion
[Overall security posture assessment]
```

---

## Remediation Priorities

### CRITICAL (Fix immediately)
- SQL injection
- Authentication bypass
- Arbitrary code execution

### HIGH (Fix before production)
- XSS vulnerabilities
- CSRF bypass
- Privilege escalation

### MEDIUM (Fix within 30 days)
- Information disclosure
- Missing security headers

### LOW (Fix when convenient)
- Verbose error messages (non-production)
- Weak SSL ciphers (if grade still A)

---

## Recommended Testing Schedule

### Before Production Launch
- [ ] Full penetration test (40 hours)
- [ ] Remediate all findings
- [ ] Re-test to verify fixes

### Quarterly
- [ ] Automated scans (OWASP ZAP)
- [ ] Manual testing of new features
- [ ] Review security logs

### Annually
- [ ] External penetration test (vendor)
- [ ] Security architecture review
- [ ] Compliance audit

---

## External Penetration Testing Vendors

### Philippines-Based
- **Cyber Aegis** - Manila
- **WhiteHat Security Philippines**
- **Tru5t Security**

### International
- **Offensive Security** - OSCP certified
- **Trustwave SpiderLabs**
- **Rapid7**

**Budget:** $3,000 - $10,000 for comprehensive test

---

**Document Version:** 1.0
**Next Steps:** Schedule pen test for Month 3 (before production launch)

---
