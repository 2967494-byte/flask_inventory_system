from app import create_app, db
from app.models import Product
import json

def check():
    app = create_app()
    with app.app_context():
        # Get the very last added product
        p = Product.query.order_by(Product.id.desc()).first()
        if p:
            data = {
                "id": p.id,
                "title": p.title,
                "external_contact": p.external_contact,
                "external_organization": p.external_organization,
                "owner": p.owner.username,
                "owner_company": p.owner.company_name,
                "images": p.images
            }
            print(json.dumps(data, indent=4, ensure_ascii=False))
        else:
            print("No products found.")

if __name__ == "__main__":
    check()
