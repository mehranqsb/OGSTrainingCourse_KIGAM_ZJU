#!/usr/bin/env bash
set -Eeuo pipefail

# OpenGeoSys course installer for Ubuntu 24.04 x86-64 and Python 3.13.
# Usage: ./install_ogstools_ubuntu.sh [online|offline]

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV="$SCRIPT_DIR/.venv_ogs"
WHEELS="$SCRIPT_DIR/wheelhouse_ubuntu"
DEBS="$SCRIPT_DIR/python_debs"
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

[[ "$(uname -s)" == "Linux" ]] || fail "This installer must run on Linux."
[[ "$(uname -m)" == "x86_64" ]] || fail "This bundle requires x86-64 Ubuntu."
# shellcheck disable=SC1091
source /etc/os-release
[[ "${ID:-}" == "ubuntu" && "${VERSION_ID:-}" == "24.04" ]] || \
    fail "This bundle requires Ubuntu 24.04."

if [[ "$INSTALL_MODE" == "offline" ]]; then
    compgen -G "$DEBS/*.deb" >/dev/null || fail "No Ubuntu Python packages found in $DEBS."
    compgen -G "$WHEELS/*.whl" >/dev/null || fail "No Python wheels found in $WHEELS."
    sudo dpkg -i "$DEBS"/*.deb
    sudo dpkg --configure -a
else
    if ! command -v python3.13 >/dev/null 2>&1; then
        sudo apt-get update
        sudo apt-get install -y software-properties-common
        sudo add-apt-repository -y ppa:deadsnakes/ppa
        sudo apt-get update
        sudo apt-get install -y python3.13 python3.13-venv
    fi
fi

command -v python3.13 >/dev/null 2>&1 || fail "python3.13 was not installed."

if [[ ! -x "$VENV/bin/python" ]]; then
    python3.13 -m venv "$VENV"
fi
PY="$VENV/bin/python"

if [[ "$INSTALL_MODE" == "offline" ]]; then
    "$PY" -m pip install --no-index --find-links "$WHEELS" \
        "ogs==$OGS_VERSION" "ogstools[all]==$OGSTOOLS_VERSION" \
        notebook jupyterlab
else
    "$PY" -m pip install --upgrade \
        "ogs==$OGS_VERSION" "ogstools[all]==$OGSTOOLS_VERSION" \
        notebook jupyterlab
fi

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
