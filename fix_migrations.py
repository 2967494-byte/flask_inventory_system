#!/usr/bin/env python3
"""
Скрипт для исправления миграций - устанавливает правильную версию в базе данных
"""

from app import create_app, db
from sqlalchemy import text

def fix_migrations():
    """Устанавливает правильную версию миграции в базе данных"""
    
    app = create_app()
    with app.app_context():
        try:
            # Проверяем существует ли таблица alembic_version
            result = db.session.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'alembic_version'
                )
            """))
            table_exists = result.scalar()
            
            if not table_exists:
                # Создаем таблицу alembic_version
                print("Создание таблицы alembic_version...")
                db.session.execute(text("""
                    CREATE TABLE alembic_version (
                        version_num VARCHAR(32) NOT NULL
                    )
                """))
            
            # Устанавливаем последнюю версию миграции
            print("Установка версии миграции b7e2c4d1a9f0...")
            db.session.execute(text("""
                DELETE FROM alembic_version
            """))
            
            db.session.execute(text("""
                INSERT INTO alembic_version (version_num) 
                VALUES ('b7e2c4d1a9f0')
            """))
            
            db.session.commit()
            print("✅ Миграции успешно исправлены!")
            
        except Exception as e:
            print(f"❌ Ошибка при исправлении миграций: {e}")
            db.session.rollback()

if __name__ == "__main__":
    fix_migrations()
