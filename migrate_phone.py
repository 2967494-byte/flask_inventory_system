from app import create_app, db
from sqlalchemy import text

def increase_phone_limit():
    app = create_app()
    with app.app_context():
        try:
            with db.engine.connect() as conn:
                print("Updating external_phone column length...")
                conn.execute(text("ALTER TABLE product ALTER COLUMN external_phone TYPE VARCHAR(256)"))
                conn.commit()
                print("Successfully increased external_phone to 256.")
        except Exception as e:
            print(f"Error updating database: {e}")

if __name__ == "__main__":
    increase_phone_limit()
