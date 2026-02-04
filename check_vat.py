from app import create_app, db
from app.models import Product
import json

def check_vat():
    app = create_app()
    with app.app_context():
        p = Product.query.order_by(Product.id.desc()).first()
        if p:
            print(f"ID: {p.id}")
            print(f"Title: {p.title}")
            print(f"Price: {p.price} ({p.price_type})")
            print(f"VAT Incl: {p.vat_included}")
            print(f"Source: {p.source_url}")

if __name__ == "__main__":
    check_vat()
