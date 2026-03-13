import logging
import os

from .server import mcp
from .stats import mongo
from . import stats_tools


log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)

@mcp.tool()
def insert_stats(collection: str, payload: str) -> str:
    """Insert Private Stats

    Args:
        collection: collection name
        payload: json payload with a list of objects, e.g. [{"owner":"alice","key":"k1","value":"v1","category":"finance","description":"monthly report", "created_at":"2026-12-03 14:05:30}]"
    """

    if not mongo.insert_stats(collection, payload):
        return "Failure"
    return 'OK'


@mcp.tool()
def list_stats(collection: str, field: str) -> list[str]:
    """List Private Stats single field unique

    Returns:
        list of unique stat field sorted ascending
    """
    return mongo.list_distinct(collection, field)


@mcp.tool()
def read_stats(collection: str, filter: str) -> list[dict]:
    """Read Private Stats

    Args:
        collection: collection name
        filter: mongodb filter query in json format, e.g. {owner":"alice","key":"k1","value":"v1"}
    """
    return mongo.read_stats(collection, filter)


if __name__ == '__main__':
    mcp.run(transport='streamable-http')
