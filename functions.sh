#!/bin/bash

OS_MCP_SCRIPT_DIR="$(dirname -- "${BASH_SOURCE[0]:-${0}}")"

activate_oneshot_mcp_env() {
  source "$OS_MCP_SCRIPT_DIR"/.venv/bin/activate
}

os_mcp() {
  activate_oneshot_mcp_env
  PYTHONPATH=$OS_MCP_SCRIPT_DIR python3 -m src.oneshot-mcp.cli "$@"
}

os_mcp_reindex_markdown() {
  activate_oneshot_mcp_env
  PYTHONPATH=$OS_MCP_SCRIPT_DIR python3 -m src.oneshot-mcp.cli weaviate reindex "ObsidianFile" --file-paths=/home/fritz/Sync/FritzSync/private --file-paths=/home/fritz/Sync/BubaFritzShare/private
}

os_mcp_reindex_patterns() {
  activate_oneshot_mcp_env
  PYTHONPATH=$OS_MCP_SCRIPT_DIR python3 -m src.oneshot-mcp.cli weaviate reindex "PatternFile" --file-paths=/home/fritz/.config/fabric/patterns/
}
