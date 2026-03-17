import json
import logging

from mcp.types import TextContent

from ..stats import mongo


def register_stats_tools(mcp) -> None:

    @mcp.tool()
    def update_stats(collection: str, filter_json: str, update_json: str) -> str:
        """Update Private Stats

        Args:
            collection: collection name
            filter_json: json payload with mongo filter condition, e.g. {"status": "inactive"}"
            update_json: json payload with mongo update condition {"$set": {"status": "archived", "updated_at": "17.03.2026"}}
        """

        if not mongo.update_stats(collection.lower(), filter_json.lower(), update_json.lower()):
            return "Failure"
        return 'OK'

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

    @mcp.tool()
    def delete_stats(collection: str, filters: str) -> int:
        """Delete Private Stats

        Args:
            collection: collection name
            filters: mongodb filter query in json format, e.g. {owner":"alice","key":"k1","value":"v1"}
        """
        ret_val = mongo.delete_stats(collection.lower(), filters.lower())
        logging.info(f"Deleted rows: {ret_val}")
        return ret_val
