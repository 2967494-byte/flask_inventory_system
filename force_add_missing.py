"""
Скрипт принудительного добавления недостающих колонок.
Специально для исправления ошибки: column "external_contact" does not exist
"""
from app import create_app, db

def force_fix():
    app = create_app()
    with app.app_context():
        print("🛠️ Начинаем принудительный ремонт БД...")
        
        conn = db.engine.raw_connection()
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Список колонок, которые ТОЧНО нужны генератору
        columns = [
            # имя, тип
            ('external_contact', 'VARCHAR(256)'),      # <-- ИМЕННО ОНА ВЫЗЫВАЛА ОШИБКУ
            ('external_organization', 'VARCHAR(256)'), 
            ('source_url', 'TEXT'),
            ('external_phone', 'VARCHAR(256)'),
            ('external_email', 'VARCHAR(120)'),
            ('region_id', 'INTEGER'),
        ]
        
        for col, dtype in columns:
            try:
                print(f"Попытка добавить {col}...")
                cursor.execute(f"ALTER TABLE product ADD COLUMN {col} {dtype}")
                print(f"✅ Успешно: колонка {col} добавлена.")
            except Exception as e:
                # Ошибка "Duplicate column" нас устраивает - значит колонка есть
                err_str = str(e).lower()
                if "already exists" in err_str or "уже существует" in err_str:
                     print(f"👌 Колонка {col} уже существует.")
                else:
                    print(f"❌ Ошибка с {col}: {e}")
        
        cursor.close()
        conn.close()
        print("🏁 Ремонт завершен. Теперь можно запускать генератор.")

if __name__ == "__main__":
    force_fix()
