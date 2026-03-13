from .finance_tools import register_finance_tools
from .knowledge_tools import register_knowledge_tools
from .news_tools import register_news_tools
from .rag_tools import register_rag_tools
from .social_tools import register_social_tools
from .weather_tools import register_weather_tools
from .stats_tools import register_stats_tools


def register_tools(mcp) -> None:
    register_social_tools(mcp)
    register_finance_tools(mcp)
    register_news_tools(mcp)
    register_weather_tools(mcp)
    register_knowledge_tools(mcp)
    register_rag_tools(mcp)
    register_stats_tools(mcp)
