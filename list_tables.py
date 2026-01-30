import psycopg
import sys

def list_tables():
    conn_str = "postgresql://postgres:postgres@localhost:5432/flask_inventory"
    try:
        conn = psycopg.connect(conn_str)
        with conn.cursor() as cur:
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            tables = cur.fetchall()
            print("Tables found in flask_inventory:")
            for table in tables:
                print(f" - {table[0]}")
        conn.close()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    list_tables()
