import json
import logging
import os
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from .finance.twelvedata import historical_data as hd
from .knowledge.wikipedia import wikipedia as wp
from .news.rapid import news_search
from .rag import weaviate_utils
from .social.ts import trump as t
from .stats.stats import insert_stats as stats_insert_stats, list_categories as stats_list_categories, read_stats as stats_read_stats
from .weather.weatherapi import weatherapi

log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)

server_host = os.environ.get('HOST', '0.0.0.0')
server_port = int(os.environ.get('PORT', '9000'))
mcp = FastMCP(name='StatelessServer', stateless_http=False, host=server_host, port=server_port)


@mcp.tool()
def trump_tweets(start_date: str, end_date: str) -> str:
    """Trump Tweets

    Args:
        start_date: start date
        end_date: end date
    """
    logging.info(f'Looking for Trump tweets from: {start_date} to {end_date}')
    tweets = t.shoot(start_date, end_date)
    return tweets


@mcp.tool()
def historical_data(symbol: str, start_date: str, end_date: str, interval: str) -> str:
    """Historical Stock Market Valuations

    Args:
        symbol: asset symbol
        start_date: start date
        end_date: end date
        interval: 1min, 5min, 15min, 30min, 45min, 1h, 2h, 4h, 8h, 1day, 1week, 1month
    """
    data = hd.shoot(symbol, start_date, end_date, interval)
    return data


@mcp.tool()
def world_news(query: str, limit: int, country: str, time_published: str) -> str:
    """World news

    Args:
        query: specific query about what happened
        limit: int of number of news items
        country: country code, e.g. US, UK, GE
        time_published: duration to the past from now in minutes, hours, days, or years, e.g. 1m, 1h, 1d, 1y.
    """
    data = news_search.shoot(query, limit, country, time_published)
    return data


@mcp.tool()
def weather_forcast(city: str, days: int) -> str:
    """Weather forcast

    Args:
        city: Pass US Zipcode, UK Postcode, Canada Postalcode, IP address, Latitude/Longitude (decimal degree) or city name
        days: Number of days of weather forecast. Value ranges from 1 to 14
    """
    data = weatherapi.shoot(city, days)
    return data


@mcp.tool()
def wikipedia(title: str) -> str:
    """Wikipedia

    Args:
        title: page title in singular
    """
    data = wp.shoot(title)
    return data


@mcp.tool()
def insert_stats(payload: str) -> str:
    """Insert Private Stats

    Args:
        payload: json payload representing a list of stat objects, e.g. [{"owner":"alice","key":"k1","value":"v1","category":"finance","description":"monthly report"}]. Optionally: "created_at", e.g.:"2026-12-03 14:05:30"
    """
    parsed = json.loads(payload)
    if not isinstance(parsed, list):
        raise ValueError('payload must be a json list of objects')
    if not stats_insert_stats(parsed):
        return "Failure"
    return 'OK'


@mcp.tool()
def list_stats_categories() -> list[str]:
    """List Private Stats categories

    Returns:
        list of unique stat categories sorted ascending
    """
    return stats_list_categories()


@mcp.tool()
def read_stats(owners: list[str], category: str, key: str | None = None) -> list[dict]:
    """Read Private Stats

    Args:
        owners: owner filter
        category: category filter
        key: key filter
    """
    return stats_read_stats(owners, category, key)


@mcp.tool()
async def weaviate_reindex(collection: str) -> str:
    """Weaviate reindex

    Args:
        collection: collection to reindex. Allowed values: PatternFile, ObsidianFile
    """
    logging.info(f'Calling weaviate reindex for: {collection}')
    paths: list[str] = []
    if collection == 'PatternFile':
        path = os.environ.get('OS_CONFIG_PATTERN_DIR')
        paths.append(path)
    elif collection == 'ObsidianFile':
        base_dir = os.environ.get('OS_MARKDOWN_BASE_DIR')
        paths.append(f'{base_dir}/{os.environ.get("OS_MARKDOWN_VAULT_DIR_1")}')
        paths.append(f'{base_dir}/{os.environ.get("OS_MARKDOWN_VAULT_DIR_2")}')
    else:
        logging.error(f'Collection unknown: {collection}')
        return 'Failure - Collection unknown'

    if not paths:
        logging.error(f'Path to collection: {collection} not provided')
        return 'Failure - Path not set up'

    for path in paths:
        if not Path(path).exists():
            logging.error(f'Path to collection: {collection} incorrect: {path}')
            return f'Failure - {collection} path incorrect'

    if await weaviate_utils.reindex_collection(
        paths,
        collection,
        os.getenv('WEAVIATE_HOST', 'localhost'),
        os.getenv('WEAVIATE_PORT', 80),
        os.getenv('WEAVIATE_GRPC_HOST', 'localhost'),
        os.getenv('WEAVIATE_GRPC_PORT', 50051),
    ):
        return 'OK'
    return 'Failure - failed to call weaviate'


if __name__ == '__main__':
    mcp.run(transport='streamable-http')