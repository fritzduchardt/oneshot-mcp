from .rag_tools import register_rag_tools
from .stats_tools import register_stats_tools


def register_tools(mcp) -> None:
    register_rag_tools(mcp)
    register_stats_tools(mcp)
