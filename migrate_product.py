from app import db
from sqlalchemy import text

def migrate():
    try:
        # Add source_url, external_contact, and maybe others
        with db.engine.connect() as conn:
            print("Adding fields to product table...")
            # Check if columns already exist
            existing_cols = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'product'")).fetchall()
            existing_cols = [c[0] for c in existing_cols]
            
            if 'source_url' not in existing_cols:
                conn.execute(text("ALTER TABLE product ADD COLUMN source_url TEXT"))
                print("Added source_url")
            
            if 'external_contact' not in existing_cols:
                conn.execute(text("ALTER TABLE product ADD COLUMN external_contact VARCHAR(256)"))
                print("Added external_contact")
            
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
