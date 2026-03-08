import asyncio
import logging
import os
from pathlib import Path

import weaviate
from weaviate.classes.config import Configure, DataType, Property
from weaviate.classes.init import AdditionalConfig, Timeout
from weaviate.connect import ConnectionParams


def create_async_client(weaviate_host: str, weaviate_port: int, weaviate_grpc_port: int):
    return weaviate.WeaviateAsyncClient(
        connection_params=ConnectionParams.from_params(
            http_host=weaviate_host,
            http_port=weaviate_port,
            http_secure=False,
            grpc_host=weaviate_host,
            grpc_port=weaviate_grpc_port,
            grpc_secure=False,
        ),
        additional_config=AdditionalConfig(
            timeout=Timeout(init=60, query=120, insert=240),
        ),
        skip_init_checks=False,
    )


async def reindex_collection(pattern_path: str, collection: str, weaviate_host: str, weaviate_port: int, weaviate_grpc_port: int) -> bool:
    # noinspection PyBroadException
    try:
        async with create_async_client(weaviate_host, weaviate_port, weaviate_grpc_port) as async_client:
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


async def call_weaviate(collection: str, prompt: str, weaviate_host: str, weaviate_port: int, weaviate_grpc_port: int) -> dict[str, str]:
    with weaviate.WeaviateClient(
            connection_params=ConnectionParams.from_params(
                http_host=weaviate_host,
                http_port=weaviate_port,
                http_secure=False,
                grpc_host=weaviate_host,
                grpc_port=weaviate_grpc_port,
                grpc_secure=False,
            ),
    ) as client:
        pattern = client.collections.use(collection)
        from weaviate.collections.classes.grpc import MetadataQuery
        response = pattern.query.near_text(
            query=prompt,
            limit=1,
            return_metadata=MetadataQuery(distance=True)
        )
        if response.objects:
            return response.objects[0].properties
    return {}
