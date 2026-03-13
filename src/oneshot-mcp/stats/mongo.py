import atexit
import json
import logging
import os
from typing import Dict, List, Any

from pymongo import MongoClient

client = MongoClient(
    f'mongodb://{os.environ.get("MONGO_HOST", "localhost")}:{os.environ.get("MONGO_PORT", 27017)}'
)
db = client['oneshot']


@atexit.register
def close_mongo_client():
    client.close()


def insert_stats(collection: str, payload: str) -> bool:
    logging.info(f'Inserts into collection: {collection}, payload: {payload}')

    try:
        collection = db[collection]
        collection.insert_many(json.loads(payload))
        return True

    except Exception as e:
        logging.error(f'Mongo failure: {e}')
        return False


def list_distinct(collection: str, field: str) -> list[str]:
    logging.info(f'In {collection} listing distinct values of: {field}')
    try:
        collection = db[collection]
        return sorted(collection.distinct(field))

    except Exception as e:
        logging.error(f'Mongo failure: {e}')
        return []


def read_stats(collection: str, filters: str) -> list[dict[str, Any]] | None:
    logging.info(f'Reading stats for: {collection} with: {filters}')
    try:
        collection = db[collection]
        results = collection.find(json.loads(filters))
        result_list = []
        for result in results:
            result.pop('_id', None)
            result_list.append(result)
        return result_list

    except Exception as e:
        logging.error(f'Mongo failure: {e}')
        return None
