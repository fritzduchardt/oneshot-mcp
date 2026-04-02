import logging
import os

from mcp.server.fastmcp import FastMCP

from .tools import register_tools

log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
logging.getLogger("mcp.server.lowlevel.server").setLevel(logging.ERROR)
logging.getLogger("mcp.server.streamable_http").setLevel(logging.ERROR)
logging.getLogger("mcp.server.streamable_http_manager").setLevel(logging.ERROR)

server_host = os.environ.get('HOST', '0.0.0.0')
server_port = int(os.environ.get('PORT', '9000'))
mcp = FastMCP(name='StatelessServer', stateless_http=False, host=server_host, port=server_port, log_level="ERROR")

register_tools(mcp)

if __name__ == '__main__':
    mcp.run(transport='streamable-http')
