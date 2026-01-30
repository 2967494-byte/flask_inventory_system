import psycopg
import sys

def check_db_name():
    conn_str = "host=localhost port=5432 user=postgres password=postgres dbname=postgres"
    try:
        conn = psycopg.connect(conn_str)
        with conn.cursor() as cur:
            cur.execute("SELECT datname, length(datname) FROM pg_database WHERE datname LIKE 'flask_inventory%';")
            dbs = cur.fetchall()
            print("Databases found with similar names:")
            for db in dbs:
                print(f" - '{db[0]}' (Length: {db[1]})")
        conn.close()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    check_db_name()
