# SGPT Terminal (Your Personal ShellGPT)

A friendly, safety‑aware inspired by EC‑Council’s SGPT. Use it to generate commands and script.

## Highlights
note = """\n> ⚠️ **Note:** If you use `--backend ollama --model llama3`, responses may take longer because it runs locally (CPU-only if no GPU).  
--> **For faster results, it’s recommended to use **OpenAI’s `gpt-4o-mini`** when available.\n"""
--> **Two backends:** OpenAI (cloud) or **Ollama** (local/offline).
--> **Modes:** `default`, `bash`, `powershell`,
--> **Safe by default:** Prints commands and rationale — execution only happens if you pass `--exec`.  

---

## 🚀 Quick Install (Linux)

```bash
git clone https://github.com/alishahid74/sgpt-terminal.git
cd sgpt-terminal
bash install.sh

### Configure API (choose one)

installs into ~/.local/share/sgpt-terminal
creates a venv
installs dependencies
places a launcher sgpt in ~/.local/bin
Make sure ~/.local/bin is on your PATH.

**OpenAI (cloud)**  
```bash
get your API key here is the linked. https://platform.openai.com/docs/overview
echo 'OPENAI_API_KEY=sk-...yourkey...' > ~/.config/sgpt-terminal/.env
```

**Ollama (local)**  
1. Install and run Ollama (https://ollama.com).  
2. Pull a model, e.g. `ollama pull llama3`.  
3. No API key needed—change backend via `--backend ollama`.

---

## Usage

```bash
sgpt -m bash "find open TCP ports with nmap" --exec
sgpt -m powershell "get top 5 processes by memory with comments" --exec
sgpt -m bash --file artifacts.txt "craft a grep to extract IOC list" --exec
```

### Switch backend/model
```bash
sgpt -b openai --model gpt-4o-mini -m bash "list listening sockets"
sgpt -b ollama --model llama3 -m bash "awk to extract 2nd column"
```

### Minimal output
```bash
sgpt -m bash "one-liner to hash all files under /evidence" --exec
```

---

## Uninstall
```bash
~/.local/share/sgpt-terminal/uninstall.sh
```

---

## Notes & Ethics
- For **red‑team techniques**, only operate on systems you own or have **explicit written authorization** to test.
- The assistant will refuse guidance that facilitates illegal or unethical activity.
- Commands are **not executed**—always review before running.


## 🛠 Manual Repair / Reinstall

If you ever see an error like `ModuleNotFoundError: No module named 'sgpt_terminal'`,  
you can rebuild the venv and launcher manually with this script:

```bash
# 0) Paths
APP="$HOME/.local/share/sgpt-terminal"
SRC="$HOME/Downloads/sgpt-terminal"   # adjust if your source folder is elsewhere

# 1) Ensure venv + deps
python3 -m venv "$APP/.venv"
source "$APP/.venv/bin/activate"
pip install --upgrade pip
pip install -r "$SRC/requirements.txt" 2>/dev/null || true

# 2) Install your package into the venv (editable install)
# If this fails (no pyproject/setup), we’ll fall back to copying files.
if ! pip install -e "$SRC"; then
  echo "[i] No packaging metadata; copying package files instead."
  mkdir -p "$APP/sgpt_terminal"
  rsync -a --delete "$SRC/sgpt_terminal/" "$APP/sgpt_terminal/"
fi

# 3) Make sure the launcher can see the package even if copied
LAUNCHER="$HOME/.local/bin/sgpt"
mkdir -p "$(dirname "$LAUNCHER")"
cat > "$LAUNCHER" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
APP_DIR="${HOME}/.local/share/sgpt-terminal"
source "${APP_DIR}/.venv/bin/activate"
export PYTHONPATH="${APP_DIR}:${PYTHONPATH:-}"
exec python -m sgpt_terminal.cli "$@"
EOF
chmod +x "$LAUNCHER"

# 4) Sanity check
python -c "import sys; print('python:',sys.executable)"
python -c "import sgpt_terminal, sgpt_terminal.cli; print('ok')"
deactivate

echo "[+] Repair complete. Try: sgpt -m bash \\"echo SGPT is alive\\""

MIT License.
