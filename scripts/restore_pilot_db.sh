#!/usr/bin/env bash
set -euo pipefail

# Restore BMMS Pilot Database from a backup file.
# Usage: ./scripts/restore_pilot_db.sh /path/to/backup.sql

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 /path/to/backup.sql" >&2
  exit 1
fi

BACKUP_FILE="$1"
if [[ ! -f "${BACKUP_FILE}" ]]; then
  echo "Backup file not found: ${BACKUP_FILE}" >&2
  exit 1
fi

if [[ -z "${DATABASE_URL:-}" ]]; then
  echo "DATABASE_URL is not set. Aborting restore." >&2
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

createdb --host="${HOST}" --port="${PORT}" --username="${USER}" --if-not-exists "${DBNAME}" || true

pg_restore --clean --if-exists --no-owner \
  --host="${HOST}" \
  --port="${PORT}" \
  --username="${USER}" \
  --dbname="${DBNAME}" \
  "${BACKUP_FILE}"

unset PGPASSWORD

echo "Restore complete for ${DBNAME} from ${BACKUP_FILE}"
