#!/usr/bin/env bash
set -euo pipefail

# BMMS Pilot Database Backup Script
# Usage: ./scripts/backup_pilot_db.sh [/path/to/output]

BACKUP_DIR="${1:-${BACKUP_DIRECTORY:-/var/backups/bmms/pilot}}"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
FILENAME="bmms_pilot_${TIMESTAMP}.sql"
RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-30}"

mkdir -p "${BACKUP_DIR}"

if [[ -z "${DATABASE_URL:-}" ]]; then
  echo "DATABASE_URL is not set. Aborting backup." >&2
  exit 1
fi

export PGPASSWORD="$(python - <<'PY'
import os
from urllib.parse import urlparse
url = urlparse(os.environ['DATABASE_URL'])
print(url.password or '')
PY
)"

HOST="$(python - <<'PY'
import os
from urllib.parse import urlparse
url = urlparse(os.environ['DATABASE_URL'])
print(url.hostname or 'localhost')
PY
)"

PORT="$(python - <<'PY'
import os
from urllib.parse import urlparse
url = urlparse(os.environ['DATABASE_URL'])
print(url.port or 5432)
PY
)"

USER="$(python - <<'PY'
import os
from urllib.parse import urlparse
url = urlparse(os.environ['DATABASE_URL'])
print(url.username or '')
PY
)"

DBNAME="$(python - <<'PY'
import os
from urllib.parse import urlparse
print(urlparse(os.environ['DATABASE_URL']).path.lstrip('/') or '')
PY
)"

pg_dump --clean --if-exists --no-owner \
  --host="${HOST}" \
  --port="${PORT}" \
  --username="${USER}" \
  --format=custom \
  --file="${BACKUP_DIR}/${FILENAME}" \
  "${DBNAME}"

unset PGPASSWORD

find "${BACKUP_DIR}" -type f -mtime +"${RETENTION_DAYS}" -name 'bmms_pilot_*.sql' -delete

echo "Backup complete: ${BACKUP_DIR}/${FILENAME}"
