import asyncio
import logging
import os
from pathlib import Path

import weaviate
from weaviate.classes.init import AdditionalConfig, Timeout
from weaviate.connect import ConnectionParams

COLLECTION_NAME = "PatternFile"
async_client = weaviate.WeaviateAsyncClient(
    connection_params=ConnectionParams.from_params(
        http_host="localhost",
        http_port=8099,
        http_secure=False,
        grpc_host="localhost",
        grpc_port=50051,
        grpc_secure=False,
    ),
    additional_config=AdditionalConfig(
        timeout=Timeout(init=30, query=60, insert=120),  # Values in seconds
    ),
    skip_init_checks=False
)

async def insert_patterns(pattern_path: str):
    from weaviate.classes.config import Configure, Property, DataType

    async with async_client:
        logging.info(f"Delete collection: {COLLECTION_NAME}")
        await async_client.collections.delete(COLLECTION_NAME)
        logging.info(f"Create collection: {COLLECTION_NAME}")
        collection = await async_client.collections.create(
            name=f"{COLLECTION_NAME}",
            vector_config=Configure.Vectors.text2vec_openai(vectorize_collection_name=True),
            properties=[
                Property(name="path", data_type=DataType.TEXT),
                Property(name="content", data_type=DataType.TEXT),
            ],
        )

        tasks = []
        logging.info(f"Fill collection {COLLECTION_NAME}")
        for root, dirs, files in os.walk(pattern_path):
            for filename in files:
                if filename.endswith('.md'):
                    file_path = f"{root}/{filename}"
                    logging.info(f"Add: {file_path}")
                    tasks.append(collection.data.insert(properties={
                        "path": file_path,
                        "content": Path(file_path).read_text()
                    }))


        await asyncio.gather(*tasks)
