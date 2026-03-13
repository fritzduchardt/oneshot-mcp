import logging
import os
from pathlib import Path

from ..rag import weaviate_utils


def register_rag_tools(mcp) -> None:
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