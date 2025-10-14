# Environment Variable Reference (Pilot Staging)

The `.env.staging.example` file enumerates required configuration for the Phase 7 pilot
environment. Use this reference when validating values with `scripts/validate_env.py`.

## Required Keys

| Key | Description |
| --- | --- |
| `DJANGO_SETTINGS_MODULE` | Must be `obc_management.settings.staging` |
| `SECRET_KEY` | 64+ character Django secret |
| `ALLOWED_HOSTS` | Comma-separated list containing `staging.bmms.gov.ph` |
| `CSRF_TRUSTED_ORIGINS` | Must include `https://staging.bmms.gov.ph` |
| `DATABASE_URL` | PostgreSQL connection string for pilot database |
| `REDIS_URL` | Redis broker (db 1 reserved for pilot tasks) |
| `CELERY_BROKER_URL` | Alias of `REDIS_URL` or dedicated broker |
| `DEFAULT_FROM_EMAIL` | Support mailbox for pilot communications |

## Optional but Recommended
- `CELERY_RESULT_BACKEND` – separate Redis db for task results
- `BACKUP_DIRECTORY` – override default `/var/backups/bmms/pilot`
- `SENTRY_DSN` / `NEW_RELIC_LICENSE_KEY` – observability tooling
- `PILOT_SUPPORT_EMAIL` – contact address surfaced in welcome emails

## Validation
```bash
./scripts/validate_env.py .env --profile staging --require PILOT_ORGANIZATION_CODES
```

The script exits with a non-zero status if any required key is missing.

## Secrets Management
Store secrets in your platform vault (e.g., Coolify secrets, AWS SSM). Never commit `.env`
files to version control. Rotate SMTP and database credentials every 90 days.
