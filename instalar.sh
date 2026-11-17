#!/usr/bin/env bash
# Interrompe a instalação ao encontrar erro de comando ou variável ausente.
set -euo pipefail

# Aceita a opção de incluir dados de demonstração e rejeita argumentos desconhecidos.
demo=()
case "${1:-}" in
    '') ;;
    --demo) demo=(--demo) ;;
    *) echo 'Uso: bash instalar.sh [--demo]' >&2; exit 2 ;;
esac
if (( $# > 1 )); then
    echo 'Uso: bash instalar.sh [--demo]' >&2
    exit 2
fi

cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
# Cria um ambiente Python separado para as dependências deste projeto.
if [[ ! -x .venv/bin/python ]]; then
    if ! command -v python3 >/dev/null || ! python3 -c 'import sys; sys.exit(sys.version_info < (3, 10))'; then
        echo 'Instale Python 3.10 ou superior com suporte a venv.' >&2
        exit 1
    fi
    python3 -m venv .venv
fi
python="$PWD/.venv/bin/python"
"$python" -c 'import sys; sys.exit(sys.version_info < (3, 10))'
"$python" -m pip install -r requirements.txt

# Prepara a configuração e aguarda o preenchimento dos dados do MySQL.
if [[ ! -e .env ]]; then
    "$python" - <<'PY'
import os
from pathlib import Path
from secrets import token_hex

# Restringe os arquivos novos ao usuário atual e prepara a chave das sessões.
os.umask(0o077)
template = Path(".env.example").read_text(encoding="utf-8")
lines = template.splitlines()
with Path(".env").open("x", encoding="utf-8") as env_file:
    for line in lines:
        if line.startswith("SECRET_KEY="):
            line = f"SECRET_KEY={token_hex(32)}"
        env_file.write(line + "\n")
PY
    echo 'Preencha e salve o .env com os dados de um esquema MySQL já criado.'
    read -r -p 'Pressione Enter após salvar o .env. '
fi

# Cria as tabelas, aplica os exemplos se solicitado e mostra como iniciar o servidor.
cd backend
"$python" -m flask --app run init-db "${demo[@]}"
echo 'Instalação concluída.'
if (( ${#demo[@]} == 0 )); then
    echo 'Para cadastrar o primeiro administrador, execute dentro de backend:'
    echo '../.venv/bin/python -m flask --app run create-admin'
fi
echo 'Para iniciar o sistema, execute dentro de backend:'
echo '../.venv/bin/python run.py'
