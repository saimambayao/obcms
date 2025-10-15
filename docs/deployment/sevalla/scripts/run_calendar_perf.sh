#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")"/.. && pwd)"
cd "$REPO_ROOT"

if [ -d "venv" ]; then
  # shellcheck disable=SC1091
  source venv/bin/activate
fi

export DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE:-obc_management.settings}
export PYTHONPATH="${PYTHONPATH:-}:${REPO_ROOT}/src"

METRICS_DIR="${REPO_ROOT}/var/perf_reports"
mkdir -p "$METRICS_DIR"
TIMESTAMP="$(date +"%Y%m%dT%H%M%S")"
export PERF_METRICS_FILE="${METRICS_DIR}/perf_${TIMESTAMP}.json"

echo "Writing metrics to ${PERF_METRICS_FILE}" >&2

pytest -m performance --disable-warnings "$@"

echo "Performance metrics available at ${PERF_METRICS_FILE}" >&2
