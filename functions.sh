#!/bin/bash

OS_MCP_SCRIPT_DIR="$(dirname -- "${BASH_SOURCE[0]:-${0}}")"

activate_oneshot_mcp_env() {
  source "$OS_MCP_SCRIPT_DIR"/.venv/bin/activate
}

os_mcp() {
  activate_oneshot_mcp_env
  PYTHONPATH=$OS_MCP_SCRIPT_DIR python3 -m src.oneshot-mcp.cli "$@"
}
