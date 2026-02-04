"""
Скрипт для гарантированного исправления структуры базы данных.
Проверяет и добавляет ВСЕ поля, необходимые для работы с внешними данными.
"""
from app import create_app, db

def fix_all_db_columns():
    app = create_app()
    with app.app_context():
        print("🔧 Полная диагностика и ремонт структуры БД...")
        
        connection = db.engine.raw_connection()
        connection.autocommit = True
        cursor = connection.cursor()
        
        # Список полей, которые должны быть в таблице product
        # Format: (column_name, sql_type)
        required_columns = [
            ('source_url', 'TEXT'),
            ('external_id', 'VARCHAR(100)'), # На всякий случай
            ('external_contact', 'VARCHAR(256)'),
            ('external_email', 'VARCHAR(120)'),
            ('external_phone', 'VARCHAR(256)'),
            ('external_organization', 'VARCHAR(256)'),
            ('region_id', 'INTEGER'),
        ]

        try:
            for col_name, col_type in required_columns:
                print(f"🔍 Проверка {col_name}...")
                
                cursor.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'product' AND column_name = %s
                """, (col_name,))
                
                if cursor.fetchone():
                    print(f"  ✅ {col_name} существует")
                else:
                    print(f"  ⚠️ {col_name} отсутствует. Добавляем...")
                    try:
                        cursor.execute(f"ALTER TABLE product ADD COLUMN {col_name} {col_type}")
                        print(f"  ✅ {col_name} успешно добавлена")
                    except Exception as add_err:
                        print(f"  ❌ Ошибка при добавлении {col_name}: {add_err}")

            print("\n🏁 Диагностика завершена.")

        except Exception as e:
            print(f"❌ Критическая ошибка: {e}")
        finally:
            cursor.close()
            connection.close()

if __name__ == "__main__":
    fix_all_db_columns()
