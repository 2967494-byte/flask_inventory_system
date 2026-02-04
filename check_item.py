from app import create_app, db
from app.models import Product, Category
import json

def check_one():
    app = create_app()
    with app.app_context():
        p = Product.query.filter(Product.source_url.isnot(None)).order_by(Product.id.desc()).first()
        if p:
            data = {
                "id": p.id,
                "title": p.title,
                "author": p.external_contact,
                "organization": p.external_organization,
                "category": p.product_category.name if p.product_category else None,
                "parent": p.product_category.parent.name if p.product_category and p.product_category.parent else None,
                "views": p.view_count,
                "date": str(p.created_at),
                "source": p.source_url
            }
            with open("item_debug.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print("Saved debug to item_debug.json")

if __name__ == "__main__":
    check_one()
