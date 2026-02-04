"""
Скрипт добавления колонок по одной (One-by-One Fix).
Гарантирует фиксацию изменений, так как за один запуск делается только одно действие.
"""
from app import create_app, db
import sys

def fix_one_column():
    app = create_app()
    with app.app_context():
        print("🛠️ One-by-One Column Fixer")
        
        conn = db.engine.raw_connection()
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Список колонок. Порядок важен!
        columns = [
            ('external_contact', 'VARCHAR(256)'),
            ('external_organization', 'VARCHAR(256)'),
            ('external_phone', 'VARCHAR(256)'),
            ('source_url', 'TEXT'),
            ('region_id', 'INTEGER'),
        ]
        
        for col_name, col_type in columns:
            try:
                # Проверяем наличие
                cursor.execute(f"SELECT 1 FROM information_schema.columns WHERE table_name='product' AND column_name='{col_name}'")
                if cursor.fetchone():
                    print(f"✅ {col_name} уже есть.")
                    continue
                
                # Если нет - пытаемся добавить
                print(f"➕ Добавляем {col_name}...")
                cursor.execute(f"ALTER TABLE product ADD COLUMN {col_name} {col_type}")
                print(f"🎉 Ура! {col_name} успешно добавлена! (Завершаем скрипт для фиксации)")
                
                # Сразу выходим, чтобы ничего не испортить
                cursor.close()
                conn.close()
                return True
                
            except Exception as e:
                print(f"❌ Ошибка с {col_name}: {e}")
                # Если транзакция сломалась, переподключаемся для следующей попытки (в следующем запуске)
                cursor.close()
                conn.close()
                return False

        print("\n✨ Все колонки на месте!")
        return True

if __name__ == "__main__":
    fix_one_column()
