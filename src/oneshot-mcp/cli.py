import asyncio
import csv
import io
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import typer
from weaviate.collections.classes.internal import Object

from .finance.twelvedata import historical_data
from .knowledge.wikipedia import wikipedia as wp
from .news.rapid import news_search
from .rag import weaviate_utils
from .social.ts import trump as t
from .stats.stats import insert_stats, list_categories
from .weather.weatherapi import weatherapi

log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)

app = typer.Typer(help='The Oneshot MCP client', context_settings={'help_option_names': {'-h', '--help'}})
social = typer.Typer(help='Social Media')
finance = typer.Typer(help='Financial Data')
news = typer.Typer(help='News')
weather = typer.Typer(help='Weather')
knowledge = typer.Typer(help='Knowledge')
weaviate = typer.Typer(help='Weaviate Agentic activity')
stats = typer.Typer(help='Stats')

app.add_typer(social, name='social')
app.add_typer(finance, name='finance')
app.add_typer(news, name='news')
app.add_typer(weather, name='weather')
app.add_typer(knowledge, name='knowledge')
app.add_typer(weaviate, name='weaviate')
app.add_typer(stats, name='stats')


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
        collection: str,
        weaviate_host: str = 'localhost',
        weaviate_port: int = 8099,
        weaviate_grpc_port: int = 50051,
        rendered_templates_dir_paths: list[str] = typer.Option([], '--file-paths', help='Paths to files to index'),
):
    for path in rendered_templates_dir_paths:
        if not Path(path).exists():
            logging.error(f'Path does not exist: {path}')
            return

    asyncio.run(weaviate_utils.reindex_collection(
        rendered_templates_dir_paths, collection, weaviate_host, weaviate_port, weaviate_grpc_port
    ))


@weaviate.command()
def call(
        collection: str,
        prompt: list[str] = typer.Argument([], help='search prompt'),
        weaviate_host: str = 'localhost',
        weaviate_port: int = 8099,
        weaviate_grpc_host: str = 'localhost',
        weaviate_grpc_port: int = 50051,
        limit: int = 1,
        certainty: float = 0.7,
):
    prompt_str = ''
    if prompt:
        prompt_str = ' '.join(prompt)
    resp: list[Object[Any, Any]] = asyncio.run(
        weaviate_utils.call_weaviate(
            collection, prompt_str, limit, certainty, weaviate_host, weaviate_port, weaviate_grpc_host, weaviate_grpc_port
        )
    )
    for i, obj in enumerate(resp):
        path = obj.properties['path']
        logging.info(f'{i + 1}: path: {path}')


@stats.command()
def insert(
        row: Optional[list[str]] = typer.Option(None, "--row", "-r", help="Row entry to add")
):
    data:List[Dict[str,str]] = []
    for r in row:
        reader = csv.reader(io.StringIO(r))
        row_data = next(reader)
        data.append({
            "owner": row_data[0],
            "key": row_data[1],
            "value": row_data[2],
            "category": row_data[3],
            "description": row_data[4],
            "created_at": row_data[5]
        })
    insert_stats(data)
    logging.info('Stats inserted successfully')


@stats.command()
def categories():
    categories_list = list_categories()
    print(categories_list)


if __name__ == '__main__':
    app()
