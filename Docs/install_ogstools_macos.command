#!/bin/bash
set -Eeuo pipefail

# OpenGeoSys course installer for Apple Silicon macOS 26+ and Python 3.13.
# Double-click for online installation, or run:
#   ./install_ogstools_macos.command offline
# Offline mode expects wheelhouse_macos_arm64 beside this script.

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV="$SCRIPT_DIR/.venv_ogs"
WHEELS="$SCRIPT_DIR/wheelhouse_macos_arm64"
OGS_VERSION="6.5.9"
OGSTOOLS_VERSION="0.8.2"
INSTALL_MODE="${1:-online}"

fail() {
    printf '\nERROR: %s\n' "$1" >&2
    exit 1
}

trap 'fail "Installation or verification failed near line $LINENO."' ERR

case "$INSTALL_MODE" in
    online|offline) ;;
    *) fail "Usage: $0 [online|offline]" ;;
esac

[[ "$(uname -s)" == "Darwin" ]] || fail "This installer must run on macOS."
[[ "$(uname -m)" == "arm64" ]] || fail "OGS 6.5.9 has no Intel macOS wheel; an Apple Silicon Mac is required."

MACOS_MAJOR="$(sw_vers -productVersion | cut -d. -f1)"
[[ "$MACOS_MAJOR" =~ ^[0-9]+$ ]] || fail "Could not determine the macOS version."
(( MACOS_MAJOR >= 26 )) || fail "The OGS 6.5.9 wheel requires macOS 26 or newer."

if command -v python3.13 >/dev/null 2>&1; then
    PYTHON="$(command -v python3.13)"
else
    fail "Install the Python 3.13 universal2 package from python.org first."
fi

"$PYTHON" --version
[[ "$("$PYTHON" -c 'import platform; print(platform.machine())')" == "arm64" ]] || \
    fail "Python is running as x86_64. Use native Terminal and an arm64/universal2 Python 3.13."

if [[ ! -x "$VENV/bin/python" ]]; then
    "$PYTHON" -m venv "$VENV"
fi

PY="$VENV/bin/python"

if [[ "$INSTALL_MODE" == "offline" ]]; then
    compgen -G "$WHEELS/*.whl" >/dev/null || \
        fail "No wheel files found in $WHEELS."
    "$PY" -m pip install --upgrade --no-index --find-links "$WHEELS" \
        "ogs==$OGS_VERSION" "ogstools[all]==$OGSTOOLS_VERSION" \
        notebook jupyterlab
else
    "$PY" -m pip install --upgrade \
        "ogs==$OGS_VERSION" "ogstools[all]==$OGSTOOLS_VERSION" \
        notebook jupyterlab
fi

# Register one shared kernel for all course notebooks.
"$PY" -m ipykernel install --user --name ogs-python --display-name "OGS Python"

"$PY" -c "from importlib.metadata import version; print('OGS package:', version('ogs')); print('OGSTools:', version('ogstools'))"
"$PY" -c "import ogstools as ot; assert ot.status(verbose=True)"

[[ -x "$VENV/bin/ogs" ]] || fail "The ogs executable was not found in the environment."
[[ -x "$VENV/bin/jupyter" ]] || fail "The jupyter executable was not found in the environment."
"$VENV/bin/ogs" --version
"$VENV/bin/jupyter" notebook --version

trap - ERR
printf '\nInstallation succeeded. Environment: %s\n' "$VENV"
printf 'Activate it with: source "%s/bin/activate"\n' "$VENV"
printf 'Jupyter kernel: OGS Python\n'
printf 'Start Jupyter Notebook with: "%s/bin/jupyter" notebook\n' "$VENV"
