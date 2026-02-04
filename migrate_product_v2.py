from app import db
from sqlalchemy import text

def migrate():
    try:
        with db.engine.connect() as conn:
            print("Checking product table for external_organization...")
            existing_cols = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'product'")).fetchall()
            existing_cols = [c[0] for c in existing_cols]
            
            if 'external_organization' not in existing_cols:
                conn.execute(text("ALTER TABLE product ADD COLUMN external_organization VARCHAR(256)"))
                print("Added external_organization")
            
            # Also ensure external_phone exists just in case
            if 'external_phone' not in existing_cols:
                conn.execute(text("ALTER TABLE product ADD COLUMN external_phone VARCHAR(50)"))
                print("Added external_phone")

            conn.commit()
            print("Migration successful.")
    except Exception as e:
        print(f"Migration error: {e}")

if __name__ == "__main__":
    from app import create_app
    app = create_app()
    with app.app_context():
        migrate()
