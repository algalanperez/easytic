#!/usr/bin/env bash
# Instala agente-contable como servicio systemd.
# Ejecutar como root o con sudo desde el directorio agente-contable/.
set -euo pipefail

INSTALL_DIR="$(cd "$(dirname "$0")" && pwd)"
SERVICE_NAME="agente-contable"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

# ── Detectar usuario y Python ──────────────────────────────────────────────────
TARGET_USER="${SUDO_USER:-$(logname 2>/dev/null || echo "$USER")}"

# Prefiere python del venv si existe, si no el del sistema
if [[ -x "${INSTALL_DIR}/.venv/bin/python3" ]]; then
    PYTHON="${INSTALL_DIR}/.venv/bin/python3"
elif [[ -x "${INSTALL_DIR}/../.venv/bin/python3" ]]; then
    PYTHON="${INSTALL_DIR}/../.venv/bin/python3"
else
    PYTHON="$(command -v python3)"
fi

# ── Verificar .env ─────────────────────────────────────────────────────────────
if [[ ! -f "${INSTALL_DIR}/.env" ]]; then
    echo "ERROR: no se encontró ${INSTALL_DIR}/.env"
    echo "       Copia .env.example a .env y rellena los valores antes de instalar."
    exit 1
fi

echo "Instalando servicio systemd:"
echo "  Usuario:       ${TARGET_USER}"
echo "  Directorio:    ${INSTALL_DIR}"
echo "  Python:        ${PYTHON}"
echo "  Servicio:      ${SERVICE_FILE}"
echo

# ── Generar unit file ─────────────────────────────────────────────────────────
sed \
    -e "s|__USER__|${TARGET_USER}|g" \
    -e "s|__INSTALL_DIR__|${INSTALL_DIR}|g" \
    -e "s|__PYTHON__|${PYTHON}|g" \
    "${INSTALL_DIR}/agente-contable.service" \
    > "${SERVICE_FILE}"

chmod 644 "${SERVICE_FILE}"

# ── Activar e iniciar ──────────────────────────────────────────────────────────
systemctl daemon-reload
systemctl enable "${SERVICE_NAME}"
systemctl restart "${SERVICE_NAME}"

echo "Servicio instalado y arrancado."
echo
echo "Comandos útiles:"
echo "  sudo systemctl status  ${SERVICE_NAME}"
echo "  sudo journalctl -u ${SERVICE_NAME} -f"
echo "  sudo systemctl stop    ${SERVICE_NAME}"
echo "  sudo systemctl restart ${SERVICE_NAME}"
