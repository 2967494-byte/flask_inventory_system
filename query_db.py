import psycopg
import sys

def query_db():
    conn_str = "postgresql://postgres:postgres@localhost:5432/flask_inventory"
    try:
        conn = psycopg.connect(conn_str)
        with conn.cursor() as cur:
            cur.execute('SELECT count(*) FROM "user"')
            count = cur.fetchone()[0]
            print(f"Users count in flask_inventory: {count}")
        conn.close()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    query_db()
