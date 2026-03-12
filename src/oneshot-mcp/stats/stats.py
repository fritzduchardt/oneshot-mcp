import logging
from typing import Dict, List, Optional

import psycopg


def insert_stats(data: List[Dict[str, str]]) -> bool:

    try:
        with psycopg.connect('dbname=oneshot user=app') as conn:

            # Open a cursor to perform database operations
            with conn.cursor() as cur:

                for row in data:
                    if 'created_at' in row and row['created_at'] is not None:
                        cur.execute(
                            'INSERT INTO oneshot_stats (owner, key, value, category, description, created_at) VALUES (%s, %s, %s, %s, %s, %s)',
                            (row['owner'], row['key'], row['value'], row['category'], row['description'], row['created_at'])
                        )
                    else:
                        cur.execute(
                            'INSERT INTO oneshot_stats (owner, key, value, category, description) VALUES (%s, %s, %s, %s, %s)',
                            (row['owner'], row['key'], row['value'], row['category'], row['description'])
                        )
                    logging.info(f'Inserted oneshot stat: {row}')
                conn.commit()
    except psycopg.OperationalError as err:
        logging.error(err)
        return False
    return True


def list_categories() -> list[str]:
    logging.info("Listing all categories")
    with psycopg.connect('dbname=oneshot user=app') as conn:

        with conn.cursor() as cur:

            cur.execute(
                'SELECT DISTINCT category FROM oneshot_stats ORDER BY category ASC'
            )
            rows = cur.fetchall()
            return [row[0] for row in rows]


def read_stats(owners: List[str], category: str, key: Optional[str] = None) -> List[Dict[str, str]]:
    logging.info(f'Reading stats for {owners} / {category} / {key}')
    with psycopg.connect('dbname=oneshot user=app') as conn:

        with conn.cursor() as cur:
            query = 'SELECT owner, key, value, category, description, created_at FROM oneshot_stats'
            params: List[object] = []
            conditions: List[str] = []

            if owners:
                conditions.append('LOWER(owner) = ANY(%s)')
                params.append([owner.lower() for owner in owners])
            if category:
                conditions.append('LOWER(category) = %s')
                params.append(category.lower())
            if key:
                conditions.append('LOWER(key) = %s')
                params.append(key.lower())

            if conditions:
                query += ' WHERE ' + ' AND '.join(conditions)

            query += ' ORDER BY created_at DESC'

            cur.execute(query, params)
            rows = cur.fetchall()

            results: List[Dict[str, str]] = []
            for row in rows:
                result = {
                    'owner': row[0],
                    'key': row[1],
                    'value': row[2],
                    'category': row[3],
                    'created_at': _format_created_at(row[5])
                }
                if row[4] is not None:
                    result['description'] = row[4]
                results.append(result)
            return results


def _format_created_at(created_at) -> str:
    return created_at.isoformat(sep=' ', timespec='seconds')