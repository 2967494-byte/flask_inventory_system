"""
Безопасный генератор товаров.
Принудительно сбрасывает транзакции перед началом работы.
"""
import random
from datetime import datetime, timedelta
from app import create_app, db
from app.models import Product, Category, User, Region

# Настройки
COUNT = 20
OWNER_USER_ID = 1

COMPANY_NAMES = [
    'ООО "СтройТехСнаб"', 'АО "ПромКомплект"', 'ООО "ИндустриТорг"',
    'ЗАО "ТехноСнаб"', 'ООО "МетизПром"', 'АО "ЭлектроКомплект"',
]

SPECIFIC_PRODUCTS = {
    "Электрооборудование": [
        "Щит распределительный навесной ЩРн-П-6 IP41",
        "Трансформатор ТМГ-1000/10/0.4",
        "Автоматический выключатель ВА47-29 3P 25А",
        "Кабель ВВГнг-LS 3х2.5 мм²",
    ],
    # ... остальные категории (упрощено для стабильности)
}

def generate_safe():
    app = create_app()
    with app.app_context():
        # СБРОС СЕССИИ - САМОЕ ВАЖНОЕ
        db.session.rollback()
        db.session.remove()
        
        print("🚀 Начинаем генерацию...")
        
        try:
            owner = db.session.get(User, OWNER_USER_ID)
            if not owner:
                print(f"❌ User {OWNER_USER_ID} not found")
                return

            categories = Category.query.all()
            regions = Region.query.filter_by(parent_id=None).all()
            
            for i in range(COUNT):
                category = random.choice(categories)
                # Simple generate name logic for this fix script
                product_name = random.choice(SPECIFIC_PRODUCTS.get(category.name, [f"Товар {category.name}"]))
                
                region = random.choice(regions) if regions else None
                company = random.choice(COMPANY_NAMES)
                
                product = Product(
                    title=product_name,
                    description=f"Состояние: Новое\\n\\n{product_name} в наличии.",
                    price=round(random.uniform(1000, 500000), 2),
                    price_type="fixed",
                    quantity=random.randint(1, 100),
                    category_id=category.id,
                    user_id=owner.id,
                    images=[], # Без картинок
                    status=1,
                    condition="new",
                    region=region.name if region else None,
                    region_id=region.id if region else None,
                    view_count=random.randint(0, 500),
                    vat_included=True,
                    created_at=datetime.now() - timedelta(days=random.randint(1, 60)),
                    external_organization=company,
                    external_phone="+X XXX XXX-XX-XX",
                    source_url=None # Явно указываем None, поле теперь есть
                )
                
                db.session.add(product)
            
            db.session.commit()
            print(f"✅ Успешно создано {COUNT} товаров.")
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            db.session.rollback()

if __name__ == "__main__":
    generate_safe()
