import psycopg
import json

def get_columns():
    conn_str = "postgresql://postgres:postgres@localhost:5432/flask_inventory"
    try:
        conn = psycopg.connect(conn_str)
        with conn.cursor() as cur:
            cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'product'")
            cols = [col[0] for col in cur.fetchall()]
            print("Product columns:")
            print(cols)
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_columns()
