"""
Миграция: добавление поля source_url в таблицу product
"""
from app import create_app, db
from sqlalchemy import text

def add_source_url_field():
    """Добавляет поле source_url в таблицу product"""
    app = create_app()
    
    with app.app_context():
        try:
            # Используем raw connection для DDL операций
            connection = db.engine.raw_connection()
            connection.autocommit = True
            cursor = connection.cursor()
            
            print("Проверка наличия поля source_url...")
            
            # Проверяем, существует ли поле
            cursor.execute(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name = 'product' AND column_name = 'source_url'"
            )
            
            if cursor.fetchone():
                print("✓ Поле source_url уже существует")
                cursor.close()
                connection.close()
                return
            
            print("Добавление поля source_url...")
            
            # Добавляем поле
            cursor.execute("ALTER TABLE product ADD COLUMN source_url TEXT")
            
            cursor.close()
            connection.close()
            
            print("✓ Поле source_url успешно добавлено")
            
        except Exception as e:
            print(f"❌ Ошибка миграции: {e}")


if __name__ == "__main__":
    add_source_url_field()
