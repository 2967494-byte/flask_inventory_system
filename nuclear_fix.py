"""
Скрипт "Nuclear Fix" - использует чистый psycopg2.
Никакой SQLAlchemy, никаких ORM. Только хардкорный SQL.
"""
import os
import psycopg2
from urllib.parse import urlparse

# Получаем URL базы из .env или хардкодом (если нужно)
# Попытайтесь найти DATABASE_URL в .env или вставьте сюда вручную, если знаете
# Пример: postgresql://user:pass@localhost:5432/dbname

def get_db_url():
    # Пытаемся прочитать из .env файла
    try:
        with open('.env') as f:
            for line in f:
                if line.startswith('DATABASE_URL='):
                    return line.split('=', 1)[1].strip().strip('"').strip("'")
    except:
        pass
    
    # Fallback - попробуйте заменить на реальный, если скрипт не найдет
    return "postgresql://flask_user:flask_password@localhost/flask_inventory"

def nuclear_fix():
    print("☢️ ЗАПУСК ЯДЕРНОГО РЕМОНТА...")
    db_url = get_db_url()
    print(f"📡 Подключение к {db_url.split('@')[-1]}...") # скрываем пароль
    
    try:
        conn = psycopg2.connect(db_url)
        conn.autocommit = True # Самое важное!
        cursor = conn.cursor()
        
        columns = [
            "external_contact VARCHAR(256)",
            "external_organization VARCHAR(256)",
            "external_phone VARCHAR(256)",
            "source_url TEXT",
            "region_id INTEGER"
        ]
        
        for col_def in columns:
            col_name = col_def.split()[0]
            print(f"🔨 Работаем над {col_name}...")
            try:
                cursor.execute(f"ALTER TABLE product ADD COLUMN IF NOT EXISTS {col_def}")
                print(f"   ✅ Успех.")
            except Exception as e:
                print(f"   ❌ Ошибка: {e}")
                
        # Насильная проверка
        print("\n🔍 Итоговая проверка:")
        cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'product'")
        cols = {row[0] for row in cursor.fetchall()}
        
        missing = []
        for col_def in columns:
            name = col_def.split()[0]
            if name in cols:
                print(f"   🆗 {name} на месте")
            else:
                print(f"   😱 {name} ВСЁ ЕЩЁ НЕТ!")
                missing.append(name)
                
        conn.close()
        
        if not missing:
            print("\n🎉 ПОБЕДА! Можно запускать генератор.")
        else:
            print("\n💀 Что-то пошло совсем не так.")

    except Exception as e:
        print(f"\n❌ Ошибка подключения: {e}")
        print("Проверьте DATABASE_URL в скрипте!")

if __name__ == "__main__":
    nuclear_fix()
