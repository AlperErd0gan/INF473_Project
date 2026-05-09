#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

BACKEND_PORT="${BACKEND_PORT:-8000}"
FRONTEND_PORT="${FRONTEND_PORT:-5173}"

# Teslimden once API key'i buraya koyarsan hocanin ekstra key girmesi gerekmez.
# Alternatif olarak terminalde export GROQ_API_KEY="..." ile de calisabilir.
EMBEDDED_GROQ_API_KEY="${EMBEDDED_GROQ_API_KEY:-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}"

BACKEND_PID=""
FRONTEND_PID=""

print_manual_runtime_instructions() {
  local os_name
  os_name="$(uname -s)"
  echo "Lutfen su araclari kurun: python3, node, npm"
  if [[ "$os_name" == "Darwin" ]]; then
    echo "macOS icin: brew install python node"
  elif [[ "$os_name" == "Linux" ]]; then
    echo "Ubuntu/Debian icin: sudo apt-get update && sudo apt-get install -y python3 python3-venv python3-pip nodejs npm"
  fi
}

collect_missing_runtime_cmds() {
  local missing=()
  local cmd
  for cmd in python3 node npm; do
    if ! command -v "$cmd" >/dev/null 2>&1; then
      missing+=("$cmd")
    fi
  done
  echo "${missing[*]}"
}

install_runtime_dependencies() {
  local missing=("$@")
  local os_name
  os_name="$(uname -s)"

  local need_python="no"
  local need_node="no"
  local cmd
  for cmd in "${missing[@]}"; do
    if [[ "$cmd" == "python3" ]]; then
      need_python="yes"
    fi
    if [[ "$cmd" == "node" || "$cmd" == "npm" ]]; then
      need_node="yes"
    fi
  done

  if [[ "$os_name" == "Darwin" ]]; then
    if ! command -v brew >/dev/null 2>&1; then
      echo "Error: Homebrew bulunamadi, otomatik kurulum yapilamiyor."
      echo "Homebrew kurup tekrar deneyin: https://brew.sh"
      exit 1
    fi
    if [[ "$need_python" == "yes" ]]; then
      brew install python
    fi
    if [[ "$need_node" == "yes" ]]; then
      brew install node
    fi
    return
  fi

  if [[ "$os_name" == "Linux" ]]; then
    if command -v apt-get >/dev/null 2>&1; then
      sudo apt-get update
      if [[ "$need_python" == "yes" ]]; then
        sudo apt-get install -y python3 python3-venv python3-pip
      fi
      if [[ "$need_node" == "yes" ]]; then
        sudo apt-get install -y nodejs npm
      fi
      return
    fi
    if command -v dnf >/dev/null 2>&1; then
      if [[ "$need_python" == "yes" ]]; then
        sudo dnf install -y python3 python3-pip
      fi
      if [[ "$need_node" == "yes" ]]; then
        sudo dnf install -y nodejs npm
      fi
      return
    fi
    if command -v yum >/dev/null 2>&1; then
      if [[ "$need_python" == "yes" ]]; then
        sudo yum install -y python3 python3-pip
      fi
      if [[ "$need_node" == "yes" ]]; then
        sudo yum install -y nodejs npm
      fi
      return
    fi
    if command -v pacman >/dev/null 2>&1; then
      if [[ "$need_python" == "yes" ]]; then
        sudo pacman -S --noconfirm python python-pip
      fi
      if [[ "$need_node" == "yes" ]]; then
        sudo pacman -S --noconfirm nodejs npm
      fi
      return
    fi
  fi

  echo "Error: Otomatik kurulum bu isletim sistemi/paket yoneticisi icin desteklenmiyor."
  print_manual_runtime_instructions
  exit 1
}

ensure_runtime_dependencies() {
  local missing_list
  missing_list="$(collect_missing_runtime_cmds)"
  if [[ -z "$missing_list" ]]; then
    return
  fi

  # shellcheck disable=SC2206
  local missing=($missing_list)
  echo "Eksik araclar bulundu: ${missing[*]}"

  if [[ ! -t 0 ]]; then
    echo "Etkilesimli olmayan oturumda otomatik kurulum sorusu sorulamiyor."
    print_manual_runtime_instructions
    exit 1
  fi

  read -r -p "Eksik araclari otomatik kurayim mi? [y/N]: " answer
  case "${answer:-}" in
    y|Y|yes|YES|Yes)
      install_runtime_dependencies "${missing[@]}"
      ;;
    *)
      echo "Kurulum kullanici tarafindan iptal edildi."
      print_manual_runtime_instructions
      exit 1
      ;;
  esac

  missing_list="$(collect_missing_runtime_cmds)"
  if [[ -n "$missing_list" ]]; then
    echo "Error: Kurulum sonrasi halen eksik araclar var: $missing_list"
    exit 1
  fi
}

ensure_supported_python_version() {
  local py_version py_major py_minor
  py_version="$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
  py_major="${py_version%%.*}"
  py_minor="${py_version##*.}"

  if [[ "$py_major" -ne 3 || "$py_minor" -lt 10 ]]; then
    echo "Error: Python $py_version tespit edildi. Bu proje Python 3.10+ gerektiriyor."
    exit 1
  fi

  echo "-> Python surumu: $py_version"
}

file_hash() {
  local file="$1"
  if command -v shasum >/dev/null 2>&1; then
    shasum -a 256 "$file" | awk '{print $1}'
  elif command -v sha256sum >/dev/null 2>&1; then
    sha256sum "$file" | awk '{print $1}'
  else
    echo "Error: sha256 araci bulunamadi (shasum/sha256sum gerekli)."
    exit 1
  fi
}

is_placeholder_key() {
  local key="${1:-}"
  [[ -z "$key" || "$key" == "your_api_key_here" || "$key" == "PASTE_YOUR_GROQ_API_KEY_HERE" ]]
}

read_env_key() {
  local env_file="$1"
  if [[ -f "$env_file" ]]; then
    local key_line
    key_line="$(grep -E '^GROQ_API_KEY=' "$env_file" | tail -n1 || true)"
    if [[ -n "$key_line" ]]; then
      local key="${key_line#GROQ_API_KEY=}"
      key="${key%\"}"
      key="${key#\"}"
      key="${key%\'}"
      key="${key#\'}"
      echo "$key"
      return
    fi
  fi
  echo ""
}

ensure_api_key() {
  local env_file="$BACKEND_DIR/.env"
  local existing_env_key

  if [[ -n "${GROQ_API_KEY:-}" ]] && ! is_placeholder_key "${GROQ_API_KEY}"; then
    echo "-> GROQ_API_KEY ortam degiskeninden kullaniliyor."
    return
  fi

  existing_env_key="$(read_env_key "$env_file")"
  if ! is_placeholder_key "$existing_env_key"; then
    export GROQ_API_KEY="$existing_env_key"
    echo "-> GROQ_API_KEY backend/.env dosyasindan kullaniliyor."
    return
  fi

  if ! is_placeholder_key "$EMBEDDED_GROQ_API_KEY"; then
    cat >"$env_file" <<EOF
GROQ_API_KEY=$EMBEDDED_GROQ_API_KEY
EOF
    export GROQ_API_KEY="$EMBEDDED_GROQ_API_KEY"
    echo "-> backend/.env olusturuldu (embedded key kullanildi)."
    return
  fi

  if [[ -t 0 ]]; then
    local entered_key
    read -r -s -p "Groq API key girin (gsk_...): " entered_key
    echo
    if ! is_placeholder_key "$entered_key"; then
      cat >"$env_file" <<EOF
GROQ_API_KEY=$entered_key
EOF
      export GROQ_API_KEY="$entered_key"
      echo "-> API key backend/.env dosyasina kaydedildi."
      return
    fi
  fi

  echo "Error: Gecerli bir GROQ_API_KEY bulunamadi."
  echo "1) Terminalde export GROQ_API_KEY=\"...\" ayarlayin, veya"
  echo "2) backend/.env dosyasina GROQ_API_KEY=... ekleyin, veya"
  echo "3) run.sh icinde EMBEDDED_GROQ_API_KEY degerini doldurun (onerilmez)."
  exit 1
}

cleanup() {
  echo
  echo "Sunucular kapatiliyor..."
  if [[ -n "$FRONTEND_PID" ]] && kill -0 "$FRONTEND_PID" 2>/dev/null; then
    kill "$FRONTEND_PID" 2>/dev/null || true
  fi
  if [[ -n "$BACKEND_PID" ]] && kill -0 "$BACKEND_PID" 2>/dev/null; then
    kill "$BACKEND_PID" 2>/dev/null || true
  fi
}

trap cleanup EXIT INT TERM

echo "GSU Transcript Agent sistemi baslatiliyor..."

ensure_runtime_dependencies
ensure_supported_python_version

ensure_api_key

echo "-> Backend bagimliliklari kontrol ediliyor..."
backend_hash_file="$BACKEND_DIR/.requirements.sha256"
backend_requirements_hash="$(file_hash "$BACKEND_DIR/requirements.txt")"

if [[ ! -d "$BACKEND_DIR/venv" ]]; then
  python3 -m venv "$BACKEND_DIR/venv"
  backend_install_required="yes"
else
  backend_install_required="no"
fi

if [[ ! -f "$backend_hash_file" ]] || [[ "$(cat "$backend_hash_file")" != "$backend_requirements_hash" ]]; then
  backend_install_required="yes"
fi

if [[ "$backend_install_required" == "yes" ]]; then
  "$BACKEND_DIR/venv/bin/pip" install -r "$BACKEND_DIR/requirements.txt"
  echo "$backend_requirements_hash" >"$backend_hash_file"
else
  echo "-> Backend bagimliliklari guncel, kurulum atlandi."
fi

echo "-> Frontend bagimliliklari kontrol ediliyor..."
frontend_hash_file="$FRONTEND_DIR/.package-lock.sha256"
if [[ -f "$FRONTEND_DIR/package-lock.json" ]]; then
  frontend_lock_hash="$(file_hash "$FRONTEND_DIR/package-lock.json")"
else
  frontend_lock_hash="no-lockfile"
fi

frontend_install_required="no"
if [[ ! -d "$FRONTEND_DIR/node_modules" ]]; then
  frontend_install_required="yes"
elif [[ ! -f "$frontend_hash_file" ]] || [[ "$(cat "$frontend_hash_file")" != "$frontend_lock_hash" ]]; then
  frontend_install_required="yes"
fi

if [[ "$frontend_install_required" == "yes" ]]; then
  if [[ -f "$FRONTEND_DIR/package-lock.json" ]]; then
    (cd "$FRONTEND_DIR" && npm ci)
  else
    (cd "$FRONTEND_DIR" && npm install)
  fi
  echo "$frontend_lock_hash" >"$frontend_hash_file"
else
  echo "-> Frontend bagimliliklari guncel, kurulum atlandi."
fi

echo "-> FastAPI backend baslatiliyor (port: $BACKEND_PORT)..."
(
  cd "$BACKEND_DIR"
  exec "$BACKEND_DIR/venv/bin/python" -m uvicorn main:app --host 127.0.0.1 --port "$BACKEND_PORT"
) &
BACKEND_PID=$!

echo "-> React frontend baslatiliyor (port: $FRONTEND_PORT)..."
(
  cd "$FRONTEND_DIR"
  exec npm run dev -- --host 127.0.0.1 --port "$FRONTEND_PORT" --strictPort
) &
FRONTEND_PID=$!

echo
echo "=========================================================="
echo "Sistem calisiyor."
echo "Backend : http://127.0.0.1:$BACKEND_PORT"
echo "Frontend: http://127.0.0.1:$FRONTEND_PORT"
echo "Durdurmak icin Ctrl+C"
echo "=========================================================="

wait "$BACKEND_PID" "$FRONTEND_PID"
