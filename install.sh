#!/usr/bin/env bash
set -euo pipefail

PREFIX="${HOME}/.local"
APP_DIR="${HOME}/.local/share/sgpt-terminal"
CONF_DIR="${HOME}/.config/sgpt-terminal"
BIN_DIR="${PREFIX}/bin"

echo "[+] Installing SGPT Terminal to ${APP_DIR}"
mkdir -p "${APP_DIR}" "${CONF_DIR}" "${BIN_DIR}"

# Copy project files
SRC_DIR="$(pwd)"
rsync -a --exclude 'sgpt-terminal.zip' --exclude '.venv' --exclude '__pycache__' "${SRC_DIR}/" "${APP_DIR}/"

cd "${APP_DIR}"
echo "[+] Creating virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

echo "[+] Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create launcher script
LAUNCHER="${BIN_DIR}/sgpt"
cat > "${LAUNCHER}" << 'EOF'
#!/usr/bin/env bash
set -euo pipefail
APP_DIR="${HOME}/.local/share/sgpt-terminal"
source "${APP_DIR}/.venv/bin/activate"
exec python -m sgpt_terminal.cli "$@"
EOF
chmod +x "${LAUNCHER}"

# Create uninstall script
cat > "${APP_DIR}/uninstall.sh" << 'EOF'
#!/usr/bin/env bash
set -euo pipefail
APP_DIR="${HOME}/.local/share/sgpt-terminal"
BIN="${HOME}/.local/bin/sgpt"
echo "[+] Removing ${BIN} (if exists)"
rm -f "${BIN}"
echo "[+] Removing ${APP_DIR}"
rm -rf "${APP_DIR}"
echo "[+] Done."
EOF
chmod +x "${APP_DIR}/uninstall.sh"

# Create example env if not present
if [[ ! -f "${CONF_DIR}/.env" ]]; then
  cat > "${CONF_DIR}/.env" << 'EOF'
# Choose one backend. Defaults to OpenAI if both are present.
# For OpenAI (cloud):
OPENAI_API_KEY=

# For Ollama (local):
# No key needed. Ensure ollama is running and you have pulled a model (e.g., 'ollama pull llama3').
EOF
  echo "[+] Wrote ${CONF_DIR}/.env (edit it to add your OPENAI_API_KEY if using OpenAI backend)."
fi

echo "[+] Installation complete! Ensure ${HOME}/.local/bin is on your PATH."
echo "    Try:  sgpt -m bash 'list open TCP ports with nmap'"
