from app import create_app, db
from app.models import Product
import sys
import codecs

# Use UTF-8 for output
sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

def verify():
    app = create_app()
    with app.app_context():
        prods = Product.query.filter(Product.description.like('%Source: https://nelikvidi.com/%')).all()
        print(f"Found {len(prods)} nelikvidi products in DB:")
        for p in prods:
            print(f"ID: {p.id} | Title: {p.title} | Price: {p.price} | Category: {p.category_id}")

if __name__ == "__main__":
    verify()
