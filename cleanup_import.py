from app import create_app, db
from app.models import Product
import os

def cleanup():
    app = create_app()
    with app.app_context():
        prods = Product.query.filter(Product.source_url.ilike('https://nelikvidi.com/%')).all()
        print(f"Deleting {len(prods)} products...")
        for p in prods:
            db.session.delete(p)
        db.session.commit()
    
    if os.path.exists("all_links.txt"):
        os.remove("all_links.txt")
        print("Removed all_links.txt")

if __name__ == "__main__":
    cleanup()
