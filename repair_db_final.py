"""
Скрипт диагностики и ремонта БД (Final Repair)
Использует чистый SQL (autocommit) для обхода ошибок транзакций SQLAlchemy.
"""
from app import create_app, db
from sqlalchemy import text

def repair_database():
    app = create_app()
    with app.app_context():
        print("🔍 Диагностика базы данных...")
        
        # Используем сырое соединение с autocommit = True
        # Это предотвращает ошибку InFailedSqlTransaction
        conn = db.engine.raw_connection()
        conn.autocommit = True
        cursor = conn.cursor()
        
        try:
            # 1. Получаем список существующих колонок
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'product'
            """)
            existing_columns = {row[0] for row in cursor.fetchall()}
            print(f"📋 Найдено {len(existing_columns)} колонок в таблице 'product'")
            
            # 2. Список необходимых колонок
            required_cols = {
                'source_url': 'TEXT',
                'external_contact': 'VARCHAR(256)',
                'external_organization': 'VARCHAR(256)',
                'external_phone': 'VARCHAR(256)',
                'external_email': 'VARCHAR(120)',
                'external_id': 'VARCHAR(100)',
                'region_id': 'INTEGER',
                'city_id': 'INTEGER'
            }
            
            # 3. Добавляем недостающие
            for col, col_type in required_cols.items():
                if col not in existing_columns:
                    print(f"⚠️ Колонка '{col}' отсутствует. Добавляем...")
                    try:
                        cursor.execute(f"ALTER TABLE product ADD COLUMN {col} {col_type}")
                        print(f"   ✅ '{col}' успешно добавлена.")
                    except Exception as e:
                        print(f"   ❌ Ошибка добавления '{col}': {e}")
                else:
                    print(f"   ✓ '{col}' уже существует")
            
            print("\n🧪 Тестовая вставка (Raw SQL)...")
            # 4. Пробуем вставить запись без ORM, чтобы проверить ограничения
            try:
                # Вставляем минимально допустимую запись
                cursor.execute("""
                    INSERT INTO product (
                        title, price, category_id, user_id, 
                        status, quantity, description, created_at,
                        external_contact, external_organization, external_phone
                    ) VALUES (
                        'Test Product DB Check', 100, 1, 1, 
                        1, 1, 'Check', NOW(),
                        'Test Contact', 'Test Org', '+0000'
                    ) RETURNING id
                """)
                new_id = cursor.fetchone()[0]
                print(f"✅ Успешно создана тестовая запись ID={new_id}")
                
                # Удаляем тест
                cursor.execute(f"DELETE FROM product WHERE id = {new_id}")
                print("✅ Тестовая запись удалена")
                
            except Exception as e:
                print(f"❌ Ошибка вставки записи: {e}")
                print("Это указывает на проблему с типами данных или ограничениями (NOT NULL).")

        except Exception as e:
            print(f"❌ Критическая ошибка подключения: {e}")
        finally:
            cursor.close()
            conn.close()
            print("\n🏁 Диагностика завершена.")

if __name__ == "__main__":
    repair_database()
