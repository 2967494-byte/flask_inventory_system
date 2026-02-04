"""
Скрипт для жесткого исправления структуры базы данных.
Использует прямые SQL-запросы в режиме autocommit, минуя ORM.
"""
from app import create_app, db
from sqlalchemy import text

def fix_db_structure():
    app = create_app()
    with app.app_context():
        print("🔧 Подключение к базе данных...")
        
        # Получаем "сырое" подключение к драйверу базы
        # Это позволяет обойти механизмы транзакций SQLAlchemy
        connection = db.engine.raw_connection()
        connection.autocommit = True
        cursor = connection.cursor()
        
        try:
            # 1. Проверяем наличие колонки source_url
            print("Проверка наличия source_url...")
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'product' AND column_name = 'source_url'
            """)
            
            if cursor.fetchone():
                print("✅ Колонка source_url уже существует.")
            else:
                print("⚠️ Колонка отсутствует. Добавляем...")
                cursor.execute("ALTER TABLE product ADD COLUMN source_url TEXT")
                print("✅ Колонка source_url успешно добавлена.")

            # 2. Проверяем наличие колонки external_phone и её тип
            print("Проверка external_phone...")
            cursor.execute("""
                SELECT character_maximum_length 
                FROM information_schema.columns 
                WHERE table_name = 'product' AND column_name = 'external_phone'
            """)
            row = cursor.fetchone()
            
            if not row:
                print("⚠️ Колонка external_phone отсутствует. Добавляем...")
                cursor.execute("ALTER TABLE product ADD COLUMN external_phone VARCHAR(256)")
                print("✅ Колонка external_phone добавлена.")
            elif row[0] and row[0] < 256:
                print(f"⚠️ Колонка слишком короткая ({row[0]}). Расширяем...")
                cursor.execute("ALTER TABLE product ALTER COLUMN external_phone TYPE VARCHAR(256)")
                print("✅ Колонка external_phone расширена до 256 символов.")
            else:
                print("✅ Колонка external_phone в порядке.")

        except Exception as e:
            print(f"❌ Критическая ошибка при работе с БД: {e}")
        finally:
            cursor.close()
            connection.close()
            print("🏁 Соединение закрыто.")

if __name__ == "__main__":
    fix_db_structure()
