from app import create_app, db
from app.models import Category

app = create_app()

with app.app_context():
    # Helper to print ancestors
    def print_ancestors(cat_name):
        cat = Category.query.filter_by(name=cat_name).first()
        if cat:
            print(f"Ancestors for '{cat.name}': {[c.name for c in cat.get_ancestors()]}")
        else:
            print(f"Category '{cat_name}' not found")

    # 1. Create a test hierarchy if not exists
    root = Category.query.filter_by(name='TestRoot').first()
    if not root:
        root = Category(name='TestRoot')
        db.session.add(root)
        db.session.commit()
    
    child = Category.query.filter_by(name='TestChild').first()
    if not child:
        child = Category(name='TestChild', parent_id=root.id)
        db.session.add(child)
        db.session.commit()
        
    grandchild = Category.query.filter_by(name='TestGrandChild').first()
    if not grandchild:
        grandchild = Category(name='TestGrandChild', parent_id=child.id)
        db.session.add(grandchild)
        db.session.commit()

    # 2. Test
    print_ancestors('TestRoot')
    print_ancestors('TestChild')
    print_ancestors('TestGrandChild')
    
    # Clean up
    db.session.delete(grandchild)
    db.session.delete(child)
    db.session.delete(root)
    db.session.commit()
    print("Cleanup done.")
