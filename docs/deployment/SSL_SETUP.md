# SSL Certificate and Domain Configuration (Pilot Staging)

## 1. DNS Configuration
Create an `A` record for `staging.bmms.gov.ph` pointing to the staging server's public IP.
Propagate DNS before requesting certificates.

## 2. Obtain Let's Encrypt Certificate
```bash
sudo certbot certonly --nginx -d staging.bmms.gov.ph --non-interactive --agree-tos \
  --email support@bmms.gov.ph
```

Certificates are stored under `/etc/letsencrypt/live/staging.bmms.gov.ph/`.

## 3. Nginx Reverse Proxy (example)
```
server {
    listen 80;
    server_name staging.bmms.gov.ph;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name staging.bmms.gov.ph;

    ssl_certificate     /etc/letsencrypt/live/staging.bmms.gov.ph/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/staging.bmms.gov.ph/privkey.pem;
    include             /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam         /etc/letsencrypt/ssl-dhparams.pem;

    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto https;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

## 4. Renewal Automation
```
0 2 * * * /usr/bin/certbot renew --quiet --post-hook "systemctl reload nginx"
```

## 5. Django Settings
Ensure `.env` enables HTTPS settings:
```
SECURE_SSL_REDIRECT=1
SESSION_COOKIE_SECURE=1
CSRF_COOKIE_SECURE=1
SECURE_HSTS_SECONDS=31536000
```

## 6. Validation Checklist
- [ ] Visiting `http://staging.bmms.gov.ph` redirects to HTTPS
- [ ] Certificate trusted by browsers (no warnings)
- [ ] Mixed content audits pass (Chrome DevTools security tab)

Maintaining valid TLS is mandatory before pilot users access the staging environment.
