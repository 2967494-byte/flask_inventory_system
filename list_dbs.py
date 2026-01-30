import psycopg
import sys

def list_dbs():
    conn_str = "host=localhost port=5432 user=postgres password=postgres dbname=postgres"
    try:
        conn = psycopg.connect(conn_str)
        with conn.cursor() as cur:
            cur.execute("SELECT datname FROM pg_database;")
            dbs = cur.fetchall()
            print("Databases found:")
            for db in dbs:
                print(f" - {db[0]}")
        conn.close()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    list_dbs()
