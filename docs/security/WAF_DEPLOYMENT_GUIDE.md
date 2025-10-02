# OBCMS Web Application Firewall (WAF) Deployment Guide

**Version:** 1.0
**Date:** January 2025
**Status:** Future Enhancement - Month 2

---

## Overview

This guide provides step-by-step instructions for deploying a Web Application Firewall (WAF) to protect OBCMS from common web attacks.

**Recommended Solution:** Cloudflare WAF (Free Plan + Pro for Production)

---

## Why WAF is Important

A WAF provides defense-in-depth by filtering malicious traffic BEFORE it reaches your application:

**Protections:**
- ✅ SQL Injection attacks
- ✅ Cross-Site Scripting (XSS)
- ✅ DDoS attacks
- ✅ Bot traffic
- ✅ Rate limiting at infrastructure level
- ✅ Geo-blocking (if needed)
- ✅ Zero-day exploit protection

**Benefits:**
- Reduces load on application servers
- Blocks attacks before they consume resources
- Real-time threat intelligence
- Easy to configure (no code changes)

---

## Option 1: Cloudflare WAF (Recommended)

### Cost:
- **Free Plan:** Basic DDoS protection, SSL, CDN
- **Pro Plan:** $20/month - Advanced WAF rules, analytics
- **Business Plan:** $200/month - Custom rules, PCI compliance

**Recommended for OBCMS:** Pro Plan ($20/month)

### 1.1 Sign Up for Cloudflare

1. Go to https://dash.cloudflare.com/sign-up
2. Create account with OOBC email
3. Verify email address

### 1.2 Add OBCMS Domain

1. Click "Add a Site"
2. Enter domain: `obcms.gov.ph`
3. Select plan: **Pro** (or Free for testing)
4. Click "Continue"

### 1.3 Update DNS Records

Cloudflare will scan existing DNS records.

**Verify these records are proxied (orange cloud icon):**

```
Type    Name              Value                   Proxy Status
A       obcms.gov.ph      <your-server-ip>        Proxied (✅)
CNAME   www               obcms.gov.ph            Proxied (✅)
CNAME   api               obcms.gov.ph            Proxied (✅)
```

**CRITICAL:** Click the orange cloud icon to enable proxy (WAF protection)

### 1.4 Update Nameservers

Cloudflare will provide nameservers:

```
brenda.ns.cloudflare.com
doug.ns.cloudflare.com
```

**At your domain registrar:**
1. Login to domain control panel
2. Find "Nameservers" or "DNS Management"
3. Replace existing nameservers with Cloudflare nameservers
4. Save changes

**Verification:**
- Wait 5-30 minutes for DNS propagation
- Cloudflare will email when activation is complete
- Check status in Cloudflare dashboard

### 1.5 Configure SSL/TLS

**In Cloudflare Dashboard:**

1. Go to **SSL/TLS** tab
2. Set SSL/TLS encryption mode: **Full (Strict)**
   - Requires valid SSL certificate on origin server
   - Use Let's Encrypt on your server

3. Enable **Always Use HTTPS**
   - Automatically redirects HTTP to HTTPS

4. Enable **Automatic HTTPS Rewrites**
   - Rewrites HTTP requests to HTTPS

5. **Edge Certificates:**
   - Enable **Always Use HTTPS**
   - Enable **HTTP Strict Transport Security (HSTS)**
   - Max Age: 12 months
   - Include subdomains: Yes
   - Preload: Yes

### 1.6 Configure WAF Rules

**Security Level:**

1. Go to **Security → Settings**
2. Set **Security Level:** High
   - Challenges suspicious visitors
   - Blocks high-risk traffic

**Managed Rules (Pro Plan):**

1. Go to **Security → WAF → Managed rules**
2. Enable **Cloudflare Managed Ruleset**
   - Protects against OWASP Top 10
   - Automatic updates
3. Enable **Cloudflare OWASP Core Ruleset**
   - Industry-standard protections

**Bot Fight Mode (Free):**

1. Go to **Security → Bots**
2. Enable **Bot Fight Mode**
   - Blocks known bad bots
   - Allows good bots (Google, Bing)

**Rate Limiting (Pro Plan):**

Create rate limiting rules:

1. Go to **Security → WAF → Rate limiting rules**
2. Click **Create rule**

**Rule 1: Login Protection**
```
Rule name: Protect Login Endpoint
If incoming requests match:
  - URI Path equals /api/token/
  - Method equals POST
Then:
  - Block
When rate exceeds:
  - 5 requests per 1 minute
  - Per IP address
```

**Rule 2: API Protection**
```
Rule name: API Rate Limit
If incoming requests match:
  - URI Path starts with /api/
Then:
  - Block
When rate exceeds:
  - 100 requests per 1 minute
  - Per IP address
```

**Rule 3: Admin Protection**
```
Rule name: Protect Admin Panel
If incoming requests match:
  - URI Path starts with /admin/
Then:
  - Block
When rate exceeds:
  - 10 requests per 1 minute
  - Per IP address
```

### 1.7 Configure Page Rules

**Cache Static Assets:**

1. Go to **Rules → Page Rules**
2. Create rule:
   ```
   URL: obcms.gov.ph/static/*
   Settings:
     - Cache Level: Cache Everything
     - Edge Cache TTL: 1 month
   ```

**Bypass Cache for Dynamic Content:**

```
URL: obcms.gov.ph/api/*
Settings:
  - Cache Level: Bypass
```

### 1.8 IP Access Rules (Optional)

**Whitelist OOBC Office IP:**

1. Go to **Security → WAF → Tools**
2. Add IP Access Rule:
   ```
   IP Address: <oobc-office-ip>
   Action: Whitelist
   Zone: This website
   ```

**Block Known Attack IPs:**

```
IP Address: <malicious-ip>
Action: Block
Zone: This website
```

### 1.9 Firewall Rules (Pro Plan)

**Custom Firewall Rule: Block by Country (If needed):**

1. Go to **Security → WAF → Firewall rules**
2. Create rule:
   ```
   Rule name: Geo-blocking
   When incoming requests match:
     - Country is not in: Philippines, United States
     - URI Path does not start with: /static/
   Then:
     - Challenge (CAPTCHA)
   ```

**Custom Rule: Protect Sensitive Endpoints:**

```
Rule name: Protect Data Export
When incoming requests match:
  - URI Path contains: /export/
  - Request Method is: POST
Then:
  - Challenge (CAPTCHA)
```

### 1.10 Enable Analytics

**Security Analytics:**

1. Go to **Analytics & Logs → Security**
2. Review:
   - Threats mitigated
   - Top attack vectors
   - Traffic by country
   - Bot traffic

**Traffic Analytics:**

1. Go to **Analytics & Logs → Traffic**
2. Monitor:
   - Bandwidth usage
   - Requests by status code
   - Cache hit ratio

---

## Option 2: AWS WAF (Alternative)

**Use Case:** If already using AWS infrastructure

**Cost:** $5/month + $1 per million requests

### 2.1 Create AWS WAF Web ACL

1. Go to AWS Console → WAF & Shield
2. Click **Create web ACL**
3. Configure:
   - Name: `obcms-waf`
   - Resource type: CloudFront or ALB
   - Region: (your region)

### 2.2 Add Managed Rule Groups

**AWS Managed Rules (Free):**

1. Add rule group: **Core rule set**
   - Protects against common vulnerabilities
2. Add rule group: **Known bad inputs**
   - Blocks malicious patterns
3. Add rule group: **SQL database**
   - SQL injection protection
4. Add rule group: **Linux operating system**
   - OS-level command injection

### 2.3 Custom Rate-Based Rules

**Create Rate Limit Rule:**

```json
{
  "Name": "RateLimitLogin",
  "Priority": 1,
  "Statement": {
    "RateBasedStatement": {
      "Limit": 100,
      "AggregateKeyType": "IP"
    }
  },
  "Action": {
    "Block": {}
  },
  "VisibilityConfig": {
    "SampledRequestsEnabled": true,
    "CloudWatchMetricsEnabled": true,
    "MetricName": "RateLimitLogin"
  }
}
```

### 2.4 Associate with CloudFront

1. In CloudFront distribution settings
2. Add Web ACL: `obcms-waf`
3. Save and deploy

---

## Option 3: Self-Hosted WAF (ModSecurity)

**Use Case:** Maximum control, no third-party dependency

**Cost:** Free (open-source)

### 3.1 Install ModSecurity with Nginx

```bash
# Install Nginx with ModSecurity
sudo apt update
sudo apt install nginx libnginx-mod-security

# Enable ModSecurity
sudo cp /etc/nginx/modsec/modsecurity.conf-recommended \
     /etc/nginx/modsec/modsecurity.conf

# Enable detection mode
sudo sed -i 's/SecRuleEngine DetectionOnly/SecRuleEngine On/' \
     /etc/nginx/modsec/modsecurity.conf
```

### 3.2 Install OWASP Core Rule Set

```bash
cd /etc/nginx/modsec
sudo git clone https://github.com/coreruleset/coreruleset.git
sudo mv coreruleset/crs-setup.conf.example coreruleset/crs-setup.conf
sudo mv coreruleset/rules/REQUEST-900-EXCLUSION-RULES-BEFORE-CRS.conf.example \
     coreruleset/rules/REQUEST-900-EXCLUSION-RULES-BEFORE-CRS.conf
```

### 3.3 Configure Nginx

Edit `/etc/nginx/nginx.conf`:

```nginx
http {
    modsecurity on;
    modsecurity_rules_file /etc/nginx/modsec/main.conf;

    # ... other config
}
```

Create `/etc/nginx/modsec/main.conf`:

```
Include /etc/nginx/modsec/modsecurity.conf
Include /etc/nginx/modsec/coreruleset/crs-setup.conf
Include /etc/nginx/modsec/coreruleset/rules/*.conf
```

### 3.4 Restart Nginx

```bash
sudo nginx -t
sudo systemctl restart nginx
```

---

## WAF Configuration Checklist

### Cloudflare (Recommended)

- [ ] Domain added to Cloudflare
- [ ] DNS records proxied (orange cloud)
- [ ] Nameservers updated at registrar
- [ ] SSL/TLS set to Full (Strict)
- [ ] Always Use HTTPS enabled
- [ ] HSTS enabled (12 months)
- [ ] Security Level: High
- [ ] Cloudflare Managed Ruleset enabled
- [ ] OWASP Core Ruleset enabled
- [ ] Bot Fight Mode enabled
- [ ] Rate limiting rules configured
  - [ ] Login endpoint (5 req/min)
  - [ ] API endpoints (100 req/min)
  - [ ] Admin panel (10 req/min)
- [ ] Page rules for static assets
- [ ] Analytics enabled

### AWS WAF

- [ ] Web ACL created
- [ ] Core rule set added
- [ ] Known bad inputs rule added
- [ ] SQL database rule added
- [ ] Rate-based rules configured
- [ ] Associated with CloudFront/ALB
- [ ] CloudWatch alarms configured

### ModSecurity

- [ ] ModSecurity installed
- [ ] OWASP Core Rule Set installed
- [ ] SecRuleEngine enabled
- [ ] Custom rules added
- [ ] Nginx restarted
- [ ] Logs monitored

---

## Testing WAF Configuration

### Test 1: SQL Injection Protection

```bash
# Attempt SQL injection (should be blocked)
curl -X POST https://obcms.gov.ph/api/token/ \
     -d "username=admin' OR '1'='1&password=test"

# Expected: 403 Forbidden or Challenge page
```

### Test 2: XSS Protection

```bash
# Attempt XSS (should be blocked)
curl "https://obcms.gov.ph/search?q=<script>alert('xss')</script>"

# Expected: 403 Forbidden or sanitized input
```

### Test 3: Rate Limiting

```bash
# Rapid requests (should be blocked after limit)
for i in {1..20}; do
  curl -X POST https://obcms.gov.ph/api/token/ \
       -d "username=test&password=wrong"
  sleep 0.1
done

# Expected: 429 Too Many Requests after 5 attempts
```

### Test 4: DDoS Protection

```bash
# Use Apache Bench for load testing
ab -n 1000 -c 100 https://obcms.gov.ph/

# Cloudflare should handle traffic gracefully
```

---

## Monitoring WAF

### Cloudflare Analytics

**Security Events:**
- Dashboard → Analytics & Logs → Security
- View threats mitigated by type
- Top attacking countries
- Attack timeline

**Create Alerts:**
- Dashboard → Notifications
- Set up alerts for:
  - High threat level
  - DDoS attack
  - Spike in blocked requests

### AWS WAF Monitoring

**CloudWatch Metrics:**
```python
# Monitor blocked requests
Namespace: AWS/WAFV2
Metric: BlockedRequests
Dimensions: WebACL, Rule
```

**Create CloudWatch Alarm:**
```bash
aws cloudwatch put-metric-alarm \
  --alarm-name "High-WAF-Block-Rate" \
  --alarm-description "Alert on high WAF block rate" \
  --metric-name BlockedRequests \
  --namespace AWS/WAFV2 \
  --statistic Sum \
  --period 300 \
  --threshold 100 \
  --comparison-operator GreaterThanThreshold
```

---

## WAF Best Practices

### 1. Start in Detection Mode

**Before blocking traffic:**
1. Enable WAF in log-only mode
2. Monitor for false positives (2 weeks)
3. Tune rules to reduce false positives
4. Switch to blocking mode

### 2. Whitelist Legitimate Traffic

**Common false positives:**
- Admin users (whitelist by IP)
- API integrations (whitelist by User-Agent)
- Load balancer health checks

### 3. Regular Rule Updates

- **Cloudflare:** Automatic (managed rulesets)
- **AWS WAF:** Check for new managed rules monthly
- **ModSecurity:** Update OWASP CRS quarterly

### 4. Monitor and Tune

**Weekly:**
- Review blocked requests
- Check for false positives
- Adjust thresholds if needed

**Monthly:**
- Analyze attack trends
- Update custom rules
- Review rate limiting effectiveness

---

## Troubleshooting

### False Positives (Legitimate Traffic Blocked)

1. **Check WAF logs** for specific rule triggered
2. **Whitelist specific endpoint:**
   ```
   URI Path: /api/upload/
   Action: Allow
   ```
3. **Whitelist by IP:**
   ```
   IP: 203.45.67.89 (OOBC office)
   Action: Whitelist
   ```

### Performance Issues

1. **Check cache hit ratio** (should be > 80%)
2. **Optimize page rules** for static assets
3. **Enable Argo Smart Routing** (Cloudflare)

### Configuration Errors

**Cloudflare:**
- Check **SSL/TLS mode** (should be Full Strict)
- Verify **origin server has valid SSL**
- Check **DNS records are proxied**

**AWS WAF:**
- Verify **Web ACL is associated** with resource
- Check **rule priority order**
- Review **CloudWatch logs**

---

## Migration Checklist

### Pre-Migration
- [ ] Backup DNS records
- [ ] Document current setup
- [ ] Create staging environment
- [ ] Test WAF rules in staging

### Migration Day
- [ ] Low traffic period (early morning)
- [ ] Update nameservers
- [ ] Monitor for DNS propagation (30 min - 24 hrs)
- [ ] Test all endpoints
- [ ] Monitor error rates

### Post-Migration
- [ ] Verify SSL certificate
- [ ] Check all subdomains
- [ ] Test API functionality
- [ ] Monitor performance (24 hours)
- [ ] Review WAF logs for false positives

---

## Cost Comparison

| Feature | Cloudflare Free | Cloudflare Pro | AWS WAF | ModSecurity |
|---------|-----------------|----------------|---------|-------------|
| **Cost/Month** | $0 | $20 | ~$30 | $0 |
| **DDoS Protection** | Basic | Advanced | Advanced | None |
| **Managed Rules** | Limited | Full | Full | OWASP CRS |
| **Rate Limiting** | No | Yes | Yes | Manual |
| **Bot Protection** | Basic | Advanced | Manual | Manual |
| **Analytics** | 24hrs | 7 days | Full | Manual |
| **Support** | Community | Email | AWS Support | Community |

**Recommendation for OBCMS:** Cloudflare Pro ($20/month)

---

## Next Steps

1. **Month 2:**
   - [ ] Sign up for Cloudflare Pro
   - [ ] Add obcms.gov.ph domain
   - [ ] Configure DNS and SSL
   - [ ] Enable managed rulesets
   - [ ] Set up rate limiting rules

2. **Month 3:**
   - [ ] Fine-tune WAF rules
   - [ ] Configure custom firewall rules
   - [ ] Set up alerting
   - [ ] Train team on WAF management

---

**Document Version:** 1.0
**Last Updated:** January 2025
**Next Review:** March 2025

---
