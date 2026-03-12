import logging
from typing import Dict, List

import psycopg

def insert_stats(data: List[Dict[str, str]]) -> bool:

    try:
        with psycopg.connect("dbname=oneshot user=app") as conn:

            # Open a cursor to perform database operations
            with conn.cursor() as cur:

                for row in data:
                    if "created_at" in row and row["created_at"] is not None:
                        cur.execute(
                            "INSERT INTO oneshot_stats (owner, key, value, category, description, created_at) VALUES (%s, %s, %s, %s, %s, %s)",
                            (row["owner"], row["key"], row["value"], row["category"], row["description"], row["created_at"])
                        )
                    else:
                        cur.execute(
                            "INSERT INTO oneshot_stats (owner, key, value, category, description) VALUES (%s, %s, %s, %s, %s)",
                            (row["owner"], row["key"], row["value"], row["category"], row["description"])
                        )
                    logging.info(f"Inserted oneshot stat: {row}")
                conn.commit()
    except psycopg.OperationalError as err:
        logging.error(err)
        return False
    return True


def list_categories() -> list[str]:

    with psycopg.connect("dbname=oneshot user=app") as conn:

        with conn.cursor() as cur:

            cur.execute(
                "SELECT DISTINCT category FROM oneshot_stats ORDER BY category ASC"
            )
            rows = cur.fetchall()
            return [row[0] for row in rows]
