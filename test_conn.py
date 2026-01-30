import psycopg
import sys

def test_conn():
    # Exact credentials from config.py
    conn_str = "postgresql://postgres:postgres@localhost:5432/flask_inventory"
    try:
        print(f"Attempting to connect with: {conn_str}")
        conn = psycopg.connect(conn_str)
        print("Successfully connected to flask_inventory!")
        conn.close()
    except Exception as e:
        print(f"Failed to connect: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_conn()
