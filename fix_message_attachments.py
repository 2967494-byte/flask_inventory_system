#!/usr/bin/env python3
"""
Скрипт для добавления полей вложений в таблицу message
"""

from app import create_app, db
from sqlalchemy import text

def add_message_attachment_fields():
    """Добавляет поля для вложений в таблицу message"""
    
    app = create_app()
    with app.app_context():
        try:
            # Проверяем, существуют ли уже поля
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'message' 
                AND column_name IN ('attachment_filename', 'attachment_original_name', 'attachment_mime', 'attachment_size')
            """))
            
            existing_columns = [row[0] for row in result.fetchall()]
            
            # Добавляем недостающие поля
            fields_to_add = [
                ('attachment_filename', 'VARCHAR(255)'),
                ('attachment_original_name', 'VARCHAR(255)'),
                ('attachment_mime', 'VARCHAR(120)'),
                ('attachment_size', 'INTEGER')
            ]
            
            for field_name, field_type in fields_to_add:
                if field_name not in existing_columns:
                    print(f"Добавление поля: {field_name}")
                    db.session.execute(text(f"""
                        ALTER TABLE message 
                        ADD COLUMN {field_name} {field_type}
                    """))
                else:
                    print(f"Поле {field_name} уже существует")
            
            db.session.commit()
            print("✅ Поля для вложений успешно добавлены в таблицу message")
            
        except Exception as e:
            print(f"❌ Ошибка при добавлении полей: {e}")
            db.session.rollback()

if __name__ == "__main__":
    add_message_attachment_fields()
