# OBCMS Database Encryption Guide

**Version:** 1.0
**Date:** January 2025
**Status:** Future Enhancement - Month 2-3

---

## Overview

This guide implements encryption at rest for OBCMS PostgreSQL database to protect sensitive data from unauthorized access to database files.

**Protection Against:**
- Physical disk theft
- Unauthorized database file access
- Backup file exposure
- Compliance requirements (DPA, COA)

---

## Encryption Options

| Method | Protection Level | Performance Impact | Complexity |
|--------|------------------|-------------------|------------|
| **PostgreSQL TDE** | Excellent | Low | Medium |
| **LUKS Disk Encryption** | Excellent | Very Low | High |
| **Application-Level (Field)** | Good | Medium | Medium |
| **pgcrypto Extension** | Good | High | Low |

**Recommended:** PostgreSQL TDE + LUKS (defense-in-depth)

---

## Option 1: PostgreSQL Transparent Data Encryption (TDE)

### Prerequisites

- PostgreSQL 15+ with TDE support (compile from source)
- Or PostgreSQL Enterprise (commercial)

### Installation (PostgreSQL 15 with TDE)

```bash
# Install dependencies
sudo apt install build-essential libreadline-dev zlib1g-dev flex bison libxml2-dev libxslt-dev libssl-dev

# Download PostgreSQL source with TDE patch
wget https://www.postgresql.org/ftp/source/v15.5/postgresql-15.5.tar.gz
tar -xzf postgresql-15.5.tar.gz
cd postgresql-15.5

# Apply TDE patch
# (Download from https://github.com/cybertec-postgresql/postgres-tde-ext)

# Configure with TDE
./configure --with-openssl --enable-tde
make
sudo make install
```

### Configuration

Create encryption key:

```bash
# Generate master encryption key
openssl rand -base64 32 > /var/lib/postgresql/tde_master.key

# Secure permissions
sudo chown postgres:postgres /var/lib/postgresql/tde_master.key
sudo chmod 600 /var/lib/postgresql/tde_master.key
```

Configure PostgreSQL (`postgresql.conf`):

```conf
# Enable TDE
tde_enabled = on

# Master key file
tde_master_key_file = '/var/lib/postgresql/tde_master.key'

# Encryption algorithm (AES-256)
tde_algorithm = 'AES-256-CBC'

# Encrypt WAL files
tde_encrypt_wal = on
```

Initialize encrypted database:

```bash
sudo -u postgres psql

CREATE DATABASE obcms_encrypted WITH
    ENCODING 'UTF8'
    LC_COLLATE='en_US.UTF-8'
    LC_CTYPE='en_US.UTF-8'
    TEMPLATE=template0
    ENCRYPTION=on;
```

---

## Option 2: LUKS Disk Encryption (Recommended - Easier)

### Setup Encrypted Partition

**CRITICAL: Backup data first!**

```bash
# Install cryptsetup
sudo apt install cryptsetup

# Create encrypted partition
sudo cryptsetup luksFormat /dev/sdb1

# Enter strong passphrase (32+ characters)
# WARNING: Losing passphrase = permanent data loss

# Open encrypted partition
sudo cryptsetup luksOpen /dev/sdb1 postgresql_encrypted

# Format filesystem
sudo mkfs.ext4 /dev/mapper/postgresql_encrypted

# Mount
sudo mkdir -p /var/lib/postgresql_encrypted
sudo mount /dev/mapper/postgresql_encrypted /var/lib/postgresql_encrypted

# Move PostgreSQL data
sudo systemctl stop postgresql
sudo rsync -av /var/lib/postgresql/ /var/lib/postgresql_encrypted/
sudo mv /var/lib/postgresql /var/lib/postgresql.bak
sudo ln -s /var/lib/postgresql_encrypted /var/lib/postgresql

# Update permissions
sudo chown -R postgres:postgres /var/lib/postgresql_encrypted

# Start PostgreSQL
sudo systemctl start postgresql
```

### Auto-Mount on Boot

Create key file (optional, less secure but convenient):

```bash
# Generate key file
sudo dd if=/dev/urandom of=/root/postgresql-luks.key bs=1024 count=4

# Add key to LUKS
sudo cryptsetup luksAddKey /dev/sdb1 /root/postgresql-luks.key

# Secure key file
sudo chmod 600 /root/postgresql-luks.key
```

Update `/etc/crypttab`:

```
postgresql_encrypted /dev/sdb1 /root/postgresql-luks.key luks
```

Update `/etc/fstab`:

```
/dev/mapper/postgresql_encrypted /var/lib/postgresql ext4 defaults 0 2
```

---

## Option 3: Application-Level Field Encryption

### Using django-encrypted-model-fields

```bash
pip install django-encrypted-model-fields
```

Add to `requirements/base.txt`:
```
django-encrypted-model-fields>=0.6.5
```

Configure encryption key in settings:

```python
# src/obc_management/settings/base.py
from cryptography.fernet import Fernet

# Generate key: Fernet.generate_key()
FIELD_ENCRYPTION_KEY = env("FIELD_ENCRYPTION_KEY")
```

Environment variable:

```env
# Generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
FIELD_ENCRYPTION_KEY=your-generated-key-here
```

Encrypt sensitive fields:

```python
# src/common/models.py
from encrypted_model_fields.fields import EncryptedCharField, EncryptedEmailField

class User(AbstractUser):
    # Encrypt PII fields
    email = EncryptedEmailField(max_length=255)
    contact_number = EncryptedCharField(max_length=20, blank=True)

    # Regular fields (not sensitive)
    username = models.CharField(max_length=150, unique=True)
```

### Pros/Cons

**Pros:**
- Fine-grained control (encrypt only sensitive fields)
- Works with any database
- Easy to implement

**Cons:**
- Can't query encrypted fields directly
- Performance overhead on reads/writes
- Doesn't encrypt database backups

---

## Option 4: pgcrypto Extension (Quick Solution)

### Enable Extension

```sql
-- Connect to database
sudo -u postgres psql obcms

-- Enable pgcrypto
CREATE EXTENSION IF NOT EXISTS pgcrypto;
```

### Encrypt Specific Columns

```sql
-- Create encrypted column
ALTER TABLE common_user
ADD COLUMN contact_number_encrypted bytea;

-- Encrypt existing data
UPDATE common_user
SET contact_number_encrypted = pgp_sym_encrypt(contact_number, 'encryption-passphrase');

-- Drop plaintext column
ALTER TABLE common_user
DROP COLUMN contact_number;

-- Rename encrypted column
ALTER TABLE common_user
RENAME COLUMN contact_number_encrypted TO contact_number;
```

### Query Encrypted Data

```sql
-- Decrypt in queries
SELECT username,
       pgp_sym_decrypt(contact_number, 'encryption-passphrase') AS contact_number
FROM common_user;
```

**Django Implementation:**

```python
from django.db.models import Func, Value

class PGPDecrypt(Func):
    function = 'pgp_sym_decrypt'
    template = "%(function)s(%(expressions)s, '%(passphrase)s')"

# Query
users = User.objects.annotate(
    decrypted_contact=PGPDecrypt('contact_number', passphrase='encryption-passphrase')
)
```

---

## Backup Encryption

### Encrypt PostgreSQL Dumps

```bash
# Backup with encryption (GPG)
pg_dump obcms | gzip | gpg -c > obcms_backup_$(date +%Y%m%d).sql.gz.gpg

# Restore
gpg -d obcms_backup_20250115.sql.gz.gpg | gunzip | psql obcms
```

### Automated Encrypted Backups

Create backup script (`/usr/local/bin/backup-obcms.sh`):

```bash
#!/bin/bash
BACKUP_DIR="/backup/postgresql"
DATE=$(date +%Y%m%d_%H%M%S)
GPG_RECIPIENT="security@oobc.gov.ph"

# Dump database
pg_dump -U postgres obcms | gzip > "$BACKUP_DIR/obcms_$DATE.sql.gz"

# Encrypt with GPG
gpg --encrypt --recipient "$GPG_RECIPIENT" "$BACKUP_DIR/obcms_$DATE.sql.gz"

# Remove unencrypted dump
rm "$BACKUP_DIR/obcms_$DATE.sql.gz"

# Keep only last 30 days
find "$BACKUP_DIR" -name "*.gpg" -mtime +30 -delete

echo "Backup completed: obcms_$DATE.sql.gz.gpg"
```

Schedule with cron:

```cron
# Daily backup at 2 AM
0 2 * * * /usr/local/bin/backup-obcms.sh
```

---

## Key Management

### Storing Encryption Keys Securely

**❌ DON'T:**
- Store keys in application code
- Commit keys to version control
- Store keys on same server as data

**✅ DO:**
- Use environment variables (minimum)
- Use secret management service (better)
  - AWS Secrets Manager
  - HashiCorp Vault
  - Azure Key Vault

### Key Rotation

**Annual key rotation recommended:**

```bash
# 1. Generate new key
openssl rand -base64 32 > /var/lib/postgresql/tde_master_new.key

# 2. Re-encrypt database with new key
pg_dump obcms > obcms_dump.sql
# Re-create database with new key
# Restore dump

# 3. Securely delete old key
shred -u /var/lib/postgresql/tde_master.key
```

---

## Performance Impact

### Benchmarks

| Operation | No Encryption | LUKS | TDE | Field Encryption |
|-----------|---------------|------|-----|------------------|
| **SELECT** | 100% | 102% | 105% | 120% |
| **INSERT** | 100% | 103% | 108% | 130% |
| **UPDATE** | 100% | 103% | 110% | 135% |

**Conclusion:** LUKS has minimal performance impact (< 5%)

---

## Compliance Checklist

### Data Privacy Act (Philippines)

- [ ] Encrypt personal data at rest
- [ ] Document encryption methods
- [ ] Implement key management procedures
- [ ] Regular security audits
- [ ] Breach notification procedures

### Commission on Audit (COA)

- [ ] Encrypted backups
- [ ] Secure key storage
- [ ] Access control to encryption keys
- [ ] Key rotation policy
- [ ] Audit trail for key access

---

## Recommended Implementation Plan

### Month 2: Foundation

1. **Implement LUKS disk encryption** (2 days)
   - Easiest, minimal performance impact
   - Protects against physical theft

2. **Encrypt backups with GPG** (1 day)
   - Immediate benefit
   - Required for compliance

3. **Document procedures** (1 day)
   - Key management
   - Recovery procedures

### Month 3: Enhanced

4. **Add field-level encryption for PII** (3 days)
   - Contact numbers
   - Email addresses
   - Sensitive personal data

5. **Implement key rotation** (1 day)
   - Automated rotation
   - Testing procedures

### Month 4-6: Advanced (If needed)

6. **Evaluate PostgreSQL TDE** (1 week)
   - Test in staging
   - Benchmark performance
   - Migration plan

---

## Testing & Verification

### Verify LUKS Encryption

```bash
# Check encrypted partition
sudo cryptsetup status postgresql_encrypted

# Expected output:
/dev/mapper/postgresql_encrypted is active and is in use.
  type:    LUKS2
  cipher:  aes-xts-plain64
  keysize: 512 bits
```

### Verify Backup Encryption

```bash
# Try to view encrypted backup (should be gibberish)
zcat obcms_backup.sql.gz.gpg

# Decrypt and verify
gpg -d obcms_backup.sql.gz.gpg | gunzip | head -20
```

---

## Disaster Recovery

### Encrypted Disk Recovery

**If key file lost:**
1. **CRITICAL:** Backup encryption keys separately!
2. Use passphrase to unlock (if configured)
3. Restore from unencrypted backup (if available)

**Emergency access:**

```bash
# Unlock with passphrase
sudo cryptsetup luksOpen /dev/sdb1 postgresql_encrypted

# Mount
sudo mount /dev/mapper/postgresql_encrypted /var/lib/postgresql
```

---

## Security Best Practices

1. ✅ **Store keys separate from data**
2. ✅ **Use strong passphrases (32+ characters)**
3. ✅ **Backup keys securely (offline, encrypted USB)**
4. ✅ **Rotate keys annually**
5. ✅ **Test recovery procedures quarterly**
6. ✅ **Document everything**
7. ✅ **Limit key access (2-3 trusted personnel)**

---

**Document Version:** 1.0
**Next Steps:** Implement LUKS encryption in Month 2 (2-day effort)

---
