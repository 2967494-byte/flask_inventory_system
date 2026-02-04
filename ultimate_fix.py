"""
ULTIMATE FIX SCRIPT
1. Исправляет структуру БД (добавляет все недостающие колонки) через raw SQL.
2. Генерирует товары в безопасном режиме.
"""
import random
import uuid
from datetime import datetime, timedelta
from app import create_app, db
from app.models import Product, Category, User, Region

# Настройки генерации
COUNT = 20
OWNER_USER_ID = 1

def fix_schema_raw():
    """Исправление схемы БД прямыми запросами с autocommit"""
    print("🔧 [1/2] Проверка и исправление структуры БД...")
    
    # Создаем принудительно чистое подключение
    conn = db.engine.raw_connection()
    conn.autocommit = True  # Важно: autocommit режим
    cursor = conn.cursor()
    
    # Список колонок для проверки: (имя, тип)
    columns_to_check = [
        ('source_url', 'TEXT'),
        ('external_id', 'VARCHAR(100)'),
        ('external_contact', 'VARCHAR(256)'),
        ('external_email', 'VARCHAR(120)'),
        ('external_phone', 'VARCHAR(256)'),
        ('external_organization', 'VARCHAR(256)'),
        ('region_id', 'INTEGER'),
        ('city_id', 'INTEGER'),
    ]
    
    try:
        for col_name, col_type in columns_to_check:
            # Проверяем наличие
            cursor.execute(f"""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'product' AND column_name = '{col_name}'
            """)
            
            if not cursor.fetchone():
                print(f"   ⚠️ Колонка '{col_name}' отсутствует. Добавляем...")
                try:
                    cursor.execute(f"ALTER TABLE product ADD COLUMN {col_name} {col_type}")
                    print(f"   ✅ Колонка '{col_name}' добавлена.")
                except Exception as e:
                    print(f"   ❌ Ошибка при добавлении '{col_name}': {e}")
            else:
                # Проверка размера для varchar полей
                if 'VARCHAR' in col_type:
                    cursor.execute(f"""
                        SELECT character_maximum_length 
                        FROM information_schema.columns 
                        WHERE table_name = 'product' AND column_name = '{col_name}'
                    """)
                    row = cursor.fetchone()
                    target_len = int(col_type.split('(')[1].split(')')[0])
                    if row and row[0] and row[0] < target_len:
                         print(f"   ⚠️ Колонка '{col_name}' слишком короткая ({row[0]}). Расширяем до {target_len}...")
                         cursor.execute(f"ALTER TABLE product ALTER COLUMN {col_name} TYPE {col_type}")
                         print(f"   ✅ Колонка '{col_name}' обновлена.")

        print("✅ [1/2] Структура БД проверена и исправлена.")
        
    except Exception as e:
        print(f"❌ Критическая ошибка SQL: {e}")
    finally:
        cursor.close()
        conn.close()

def generate_products_safe():
    """Генерация товаров в новой чистой сессии"""
    print("\n🚀 [2/2] Запуск генерации товаров...")
    
    # Важно: сбрасываем сессию перед началом работы ORM
    db.session.remove()
    
    try:
        # Проеряем пользователя
        owner = db.session.get(User, OWNER_USER_ID)
        if not owner:
            print(f"❌ Пользователь ID {OWNER_USER_ID} не найден.")
            return

        categories = Category.query.all()
        regions = Region.query.filter_by(parent_id=None).all()
        
        created_cnt = 0
        for i in range(COUNT):
            category = random.choice(categories) if categories else None
            # Простое название
            p_name = f"Товар {category.name} #{random.randint(1000,9999)}" if category else f"Товар #{random.randint(1000,9999)}"
            
            region = random.choice(regions) if regions else None
            
            prod = Product(
                title=p_name,
                description=f"Автоматически созданный товар.\nДата: {datetime.now()}",
                price=random.randint(100, 50000),
                price_type="fixed",
                quantity=10,
                category_id=category.id if category else 1,
                user_id=owner.id,
                status=1,
                images=[],
                region=region.name if region else "РФ",
                region_id=region.id if region else None,
                external_organization='ООО "ТестГео"',
                external_phone='+X XXX XXX-XX-XX'
            )
            db.session.add(prod)
            created_cnt += 1
        
        db.session.commit()
        print(f"✅ Успешно создано {created_cnt} товаров.")
        
    except Exception as e:
        print(f"❌ Ошибка генерации: {e}")
        db.session.rollback()

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        # Шаг 1: Raw SQL fix
        fix_schema_raw()
        
        # Шаг 2: ORM generation
        generate_products_safe()
