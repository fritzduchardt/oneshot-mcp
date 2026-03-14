import json
import logging

from mcp.types import TextContent

from ..stats import mongo


def register_stats_tools(mcp) -> None:

    @mcp.tool()
    def insert_stats(collection: str, payload: str) -> str:
        """Insert Private Stats

        Args:
            collection: collection name
            payload: json payload with a list of objects, e.g. [{"owner":"alice","key":"k1","value":"v1","category":"finance","description":"monthly report", "created_at":"2026-12-03 14:05:30}]"
        """

        if not mongo.insert_stats(collection.lower(), payload.lower()):
            return "Failure"
        return 'OK'


    @mcp.tool()
    def read_stats(collection: str, filters: str) -> TextContent:
        """Read Private Stats

        Args:
            collection: collection name
            filters: mongodb filter query in json format, e.g. {owner":"alice","key":"k1","value":"v1"}
        """
        ret_val = mongo.read_stats(collection.lower(), filters.lower())
        logging.info(f"Stats results: {ret_val}")
        return TextContent(type="text", text=json.dumps(ret_val))
