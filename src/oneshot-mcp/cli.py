import asyncio
import logging
import os
from pathlib import Path
from typing import Any

import typer
from weaviate.collections.classes.internal import Object

from .rag import weaviate_utils

log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)

app = typer.Typer(help='The Oneshot MCP client', context_settings={'help_option_names': {'-h', '--help'}})
weaviate = typer.Typer(help='Weaviate Agentic activity')
stats = typer.Typer(help='Stats')

app.add_typer(weaviate, name='weaviate')
app.add_typer(stats, name='stats')

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
        rendered_templates_dir_paths, collection, weaviate_host, weaviate_port, weaviate_host, weaviate_grpc_port
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


if __name__ == '__main__':
    app()
