from app import create_app, db
from app.models import User, Category, Product, Region, City
import json

app = create_app()

def list_info():
    with app.app_context():
        print("--- USERS ---")
        users = User.query.all()
        for u in users:
            print(f"ID: {u.id}, Email: {u.email}, Role: {u.role}")
        
        print("\n--- CATEGORIES (First 10) ---")
        cats = Category.query.limit(10).all()
        for c in cats:
            print(f"ID: {c.id}, Name: {c.name}")

if __name__ == "__main__":
    list_info()
