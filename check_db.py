import psycopg
import sys

def check_db():
    conn_str = "host=localhost port=5432 user=postgres password=postgres dbname=postgres"
    try:
        conn = psycopg.connect(conn_str, autocommit=True)
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname = 'flask_inventory'")
            exists = cur.fetchone()
            if not exists:
                print("Database 'flask_inventory' does not exist. Creating it...")
                cur.execute("CREATE DATABASE flask_inventory")
                print("Database 'flask_inventory' created successfully.")
            else:
                print("Database 'flask_inventory' already exists.")
        conn.close()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    check_db()
