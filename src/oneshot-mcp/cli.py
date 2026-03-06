import asyncio
import logging
import os

import typer

from .finance.twelvedata import historical_data
from .knowledge.wikipedia import wikipedia as wp
from .news.rapid import news_search
from .rag import weaviate_utils
from .social.ts import trump as t
from .weather.weatherapi import weatherapi

log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

app = typer.Typer(help="The Oneshot MCP client", context_settings={"help_option_names": {"-h", "--help"}})
social = typer.Typer(help="Social Media")
finance = typer.Typer(help="Financial Data")
news = typer.Typer(help="News")
weather = typer.Typer(help="Weather")
knowledge = typer.Typer(help="Knowledge")
weaviate = typer.Typer(help="Weaviate Agentic activity")

app.add_typer(social, name="social")
app.add_typer(finance, name="finance")
app.add_typer(news, name="news")
app.add_typer(weather, name="weather")
app.add_typer(knowledge, name="knowledge")
app.add_typer(weaviate, name="weaviate")


@social.command()
def trump(
    start_date: str,
    end_date: str,
):
    tweets = t.shoot(start_date, end_date)
    print(tweets)


@news.command()
def world(
    query: str,
    limit: int,
    country: str,
    time_published: str,
):
    news_result = news_search.shoot(query, limit, country, time_published)
    print(news_result)


@finance.command()
def hd(
    symbol: str,
    start_date: str,
    end_date: str,
    interval: str,
):
    data = historical_data.shoot(symbol, start_date, end_date, interval)
    print(data)


@weather.command()
def forcast(
    city: str,
    days: int,
):
    data = weatherapi.shoot(city, days)
    print(data)


@knowledge.command()
def wikipedia(
    title: str,
):
    data = wp.shoot(title)
    print(data)


@weaviate.command()
def reindex(
    path: str,
    collection: str,
    weaviate_host: str,
    weaviate_port: int,
    weaviate_grpc_port: int,
):
    asyncio.run(weaviate_utils.reindex_collection(path, collection, weaviate_host, weaviate_port, weaviate_grpc_port))


if __name__ == "__main__":
    app()
