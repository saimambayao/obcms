#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_PATH="${PROJECT_ROOT}/venv"
PYTHON_BIN="${PYTHON_BIN:-python3.12}"

if ! command -v "${PYTHON_BIN}" >/dev/null 2>&1; then
    echo "[bootstrap] Required interpreter '${PYTHON_BIN}' not found on PATH." >&2
    echo "[bootstrap] Install Python 3.12 or adjust PYTHON_BIN before retrying." >&2
    exit 1
fi

create_venv() {
    echo "[bootstrap] Creating virtual environment with ${PYTHON_BIN} at ${VENV_PATH}"
    "${PYTHON_BIN}" -m venv "${VENV_PATH}"
}

if [[ -d "${VENV_PATH}" ]]; then
    ACTIVE_PYTHON="${VENV_PATH}/bin/python"
    if [[ ! -x "${ACTIVE_PYTHON}" ]]; then
        echo "[bootstrap] Existing virtual environment is invalid. Rebuilding..."
        rm -rf "${VENV_PATH}"
        create_venv
    else
        CURRENT_VERSION="$("${ACTIVE_PYTHON}" -c 'import sys; print("%d.%d" % (sys.version_info.major, sys.version_info.minor))')"
        if [[ "${CURRENT_VERSION}" != "3.12" ]]; then
            echo "[bootstrap] Virtual environment is using Python ${CURRENT_VERSION}. Recreating with 3.12..."
            rm -rf "${VENV_PATH}"
            create_venv
        else
            echo "[bootstrap] Existing virtual environment already uses Python 3.12."
        fi
    fi
else
    create_venv
fi

# Upgrade pip and install dependencies
source "${VENV_PATH}/bin/activate"
python -m pip install --upgrade pip
pip install -r "${PROJECT_ROOT}/requirements/development.txt"

deactivate

cat <<MSG
[bootstrap] Virtual environment ready at ${VENV_PATH}
[bootstrap] Activate with: source venv/bin/activate
MSG
