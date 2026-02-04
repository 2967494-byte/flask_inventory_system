from app import create_app, db
from app.models import Product

def check():
    app = create_app()
    with app.app_context():
        p = Product.query.filter(Product.id < 10).first()
        if p:
            print(f"ID: {p.id}")
            print(f"Type of images: {type(p.images)}")
            print(f"Value of images: {p.images}")

if __name__ == "__main__":
    check()
