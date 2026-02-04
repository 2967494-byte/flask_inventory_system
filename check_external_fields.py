from app import create_app, db
from app.models import Product

def check():
    app = create_app()
    with app.app_context():
        # Get last 5 products
        prods = Product.query.order_by(Product.id.desc()).limit(5).all()
        for p in prods:
            print(f"ID: {p.id}")
            print(f"  External Contact: '{p.external_contact}'")
            print(f"  External Org: '{p.external_organization}'")

if __name__ == "__main__":
    check()
