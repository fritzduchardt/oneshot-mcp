import asyncio
import logging
import os
from pathlib import Path

import weaviate
from weaviate.classes.config import Configure, DataType, Property
from weaviate.classes.init import AdditionalConfig, Timeout
from weaviate.connect import ConnectionParams


def create_async_client():
    return weaviate.WeaviateAsyncClient(
        connection_params=ConnectionParams.from_params(
            http_host="localhost",
            http_port=8099,
            http_secure=False,
            grpc_host="localhost",
            grpc_port=50051,
            grpc_secure=False,
        ),
        additional_config=AdditionalConfig(
            timeout=Timeout(init=60, query=120, insert=240),
        ),
        skip_init_checks=False,
    )


async def reindex_collection(pattern_path: str, collection: str) -> bool:
    # noinspection PyBroadException
    try:
        async with create_async_client() as async_client:
            logging.info(f"Delete collection: {collection}")
            await async_client.collections.delete(collection)

            logging.info(f"Create collection: {collection}")
            weaviate_collection = await async_client.collections.create(
                name=f"{collection}",
                vector_config=Configure.Vectors.text2vec_openai(vectorize_collection_name=True),
                properties=[
                    Property(name="path", data_type=DataType.TEXT),
                    Property(name="content", data_type=DataType.TEXT),
                ],
            )

            request_semaphore = asyncio.Semaphore(5)
            tasks = []
            logging.info(f"Fill collection {collection}")
            for root, dirs, files in os.walk(pattern_path):
                for filename in files:
                    if not filename.endswith(".md"):
                        continue

                    file_path = f"{root}/{filename}"
                    logging.info(f"Add: {file_path}")
                    tasks.append(
                        create_bounded_insert_task(
                            request_semaphore=request_semaphore,
                            weaviate_collection=weaviate_collection,
                            file_path=file_path,
                        )
                    )

            if tasks:
                await asyncio.gather(*tasks)
            return True
    except Exception:
        logging.exception("Failed to reindex weaviate:")
        return False


async def create_bounded_insert_task(request_semaphore, weaviate_collection, file_path: str):
    async with request_semaphore:
        return await weaviate_collection.data.insert(
            properties={
                "path": file_path,
                "content": Path(file_path).read_text(),
            }
        )
