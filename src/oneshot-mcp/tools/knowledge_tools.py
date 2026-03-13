from ..knowledge.wikipedia import wikipedia as wp


def register_knowledge_tools(mcp) -> None:
    @mcp.tool()
    def wikipedia(title: str) -> str:
        """Wikipedia

        Args:
            title: page title in singular
        """
        data = wp.shoot(title)
        return data