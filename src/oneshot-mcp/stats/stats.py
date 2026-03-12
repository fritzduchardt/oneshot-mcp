import psycopg

def insert_stat(owner:str, key:str, value: str, category: str, description: str):

    with psycopg.connect("dbname=oneshot user=app") as conn:

        # Open a cursor to perform database operations
        with conn.cursor() as cur:

            # Pass data to fill a query placeholders and let Psycopg perform
            # the correct conversion (no SQL injections!)
            cur.execute(
                "INSERT INTO oneshot_stats (owner, key, value, category, description) VALUES (%s, %s, %s, %s, %s)",
                (owner, key, value, category, description)
            )

            conn.commit()

def list_categories() -> list[str]:

    with psycopg.connect("dbname=oneshot user=app") as conn:

        with conn.cursor() as cur:

            cur.execute(
                "SELECT DISTINCT category FROM oneshot_stats ORDER BY category ASC"
            )
            rows = cur.fetchall()
            return [row[0] for row in rows]