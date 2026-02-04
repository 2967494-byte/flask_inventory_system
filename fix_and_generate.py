"""
Скрипт "Все-в-одном":
1. Проверяет и исправляет структуру БД (добавляет source_url)
2. Генерирует тестовые товары (без картинок для стабильности)
"""
import os
import random
import uuid
from datetime import datetime, timedelta
from sqlalchemy import text
from app import create_app, db
from app.models import Product, Category, User, Region

# Настройки
COUNT = 20  # Количество товаров
OWNER_USER_ID = 1

# Данные для генерации
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
    "Спецтехника": [
        "Погрузчик SEM 655D 2017г.в.",
        "Экскаватор Hyundai R220LC-9S 2019г.в.",
        "Автокран Галичанин КС-55713-1 25т",
    ],
    "Строительные материалы": [
        "КИРПИЧ ОГНЕУПОР.ОСН:ФАСОННЫЙ;ША К-713-13",
        "Цемент ПЦ 500-Д0 М500 50кг",
    ],
}

def fix_database():
    """Исправляет структуру БД (добавляет source_url)"""
    print("🔧 Проверка структуры базы данных...")
    try:
        connection = db.engine.raw_connection()
        connection.autocommit = True
        cursor = connection.cursor()
        
        # Проверяем наличие колонки
        cursor.execute(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name = 'product' AND column_name = 'source_url'"
        )
        
        if not cursor.fetchone():
            print("  --> Добавляем колонку source_url...")
            cursor.execute("ALTER TABLE product ADD COLUMN source_url TEXT")
            print("  ✓ Колонка успешно добавлена")
        else:
            print("  ✓ Структура БД в порядке")
            
        cursor.close()
        connection.close()
        return True
    except Exception as e:
        print(f"❌ Ошибка при обновлении БД: {e}")
        return False

def generate_product_name(category):
    for cat_key in SPECIFIC_PRODUCTS:
        if cat_key.lower() in category.lower():
            return random.choice(SPECIFIC_PRODUCTS[cat_key])
    
    # Fallback
    all_products = []
    for p in SPECIFIC_PRODUCTS.values():
        all_products.extend(p)
    return random.choice(all_products) if all_products else "Промышленное оборудование"

def main():
    app = create_app()
    
    with app.app_context():
        # 1. Исправляем БД
        if not fix_database():
            return

        # 2. Очищаем сессию на всякий случай
        db.session.remove()
        
        # 3. Подготовка данных
        owner = db.session.get(User, OWNER_USER_ID)
        if not owner:
            print(f"❌ Пользователь ID {OWNER_USER_ID} не найден")
            return
            
        categories = Category.query.all()
        regions = Region.query.filter_by(parent_id=None).all()
        
        print(f"🚀 Начинаем генерацию {COUNT} товаров...")
        
        for i in range(COUNT):
            try:
                category = random.choice(categories)
                product_name = generate_product_name(category.name)
                region = random.choice(regions) if regions else None
                company = random.choice(COMPANY_NAMES)
                
                # Создаем товар
                product = Product(
                    title=product_name,
                    description=f"Состояние: Новое\n\nПродаем {product_name}. В наличии на складе. Документы в порядке.",
                    price=round(random.uniform(1000, 500000), 2),
                    price_type="fixed",
                    quantity=random.randint(1, 100),
                    category_id=category.id,
                    user_id=owner.id,
                    images=[], # Без картинок, чтобы избежать ошибок API
                    status=1, # Published
                    condition="new",
                    region=region.name if region else None,
                    region_id=region.id if region else None,
                    view_count=random.randint(0, 100),
                    vat_included=True,
                    created_at=datetime.now() - timedelta(days=random.randint(1, 30)),
                    external_organization=company,
                    external_phone="+X XXX XXX-XX-XX",
                    source_url=None
                )
                
                db.session.add(product)
                
                if (i + 1) % 10 == 0:
                    db.session.commit()
                    print(f"  Создано {i + 1} товаров...")
                    
            except Exception as e:
                print(f"  ❌ Ошибка создания товара {i+1}: {e}")
                db.session.rollback()
        
        try:
            db.session.commit()
            print(f"\n✅ Готово! Успешно создано {COUNT} товаров.")
        except Exception as e:
            print(f"\n❌ Финальная ошибка сохранения: {e}")

if __name__ == "__main__":
    main()
