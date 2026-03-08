#!/bin/bash

SCRIPT_DIR="$(dirname -- "${BASH_SOURCE[0]:-${0}}")"

activate_env() {
  source "$SCRIPT_DIR"/.venv/bin/activate
}

os_mcp() {
  activate_env
  PYTHONPATH=$SCRIPT_DIR python3 -m src.oneshot-mcp.cli "$@"
}
