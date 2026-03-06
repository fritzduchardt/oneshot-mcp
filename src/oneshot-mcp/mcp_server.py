#! python3
import logging
import os

from mcp.server.fastmcp import FastMCP

from finance.twelvedata import historical_data as hd
from knowledge.wikipedia import wikipedia as wp
from news.rapid import news_search
from rag import weaviate_utils
from social.ts import trump as t
from weather.weatherapi import weatherapi

log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

mcp = FastMCP(name="StatelessServer", stateless_http=False, host="0.0.0.0")


@mcp.tool()
def trump_tweets(start_date: str, end_date: str) -> str:
    """Trump Tweets

    Args:
        start_date: start date
        end_date: end date
    """
    logging.info(f"Looking for Trump tweets from: {start_date} to {end_date}")
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
async def weaviate_reindex(collection: str) -> str:
    """Weaviate reindex

    Args:
        collection: collection to reindex
    """
    logging.info(f"Calling weaviate reindex for: {collection}")

    if collection == "ObsidianFile":
        path = os.environ.get("OS_CONFIG_PATTERN_DIR")
    elif collection == "PatternFile":
        base_dir = os.environ.get("OS_MARKDOWN_BASE_DIR")
        vault_dir = os.environ.get("OS_MARKDOWN_VAULT_DIR_1")
        path = f"{base_dir}/{vault_dir}"
    else:
        logging.error(f"Collection unknown: {collection}")
        return "Failure - Collection unknown"

    if not path:
        logging.error("Path to pattern files not provided")
        return "Failure - Path not set up"

    if await weaviate_utils.reindex_collection(path, collection):
        return "OK"
    else:
        return "Failure - failed to call weaviate"


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
