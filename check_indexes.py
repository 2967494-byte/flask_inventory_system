#!/usr/bin/env python3
"""
Скрипт для проверки существующих индексов в таблице review
"""

from app import create_app, db
from sqlalchemy import text

def check_review_indexes():
    """Проверяет существующие индексы в таблице review"""
    
    app = create_app()
    with app.app_context():
        try:
            # Получаем все индексы таблицы review
            result = db.session.execute(text("""
                SELECT indexname, indexdef 
                FROM pg_indexes 
                WHERE tablename = 'review'
                ORDER BY indexname
            """))
            
            indexes = result.fetchall()
            
            print("Индексы в таблице review:")
            for index in indexes:
                print(f"  - {index[0]}: {index[1]}")
            
            # Проверяем конкретные индексы из миграции
            expected_indexes = [
                'idx_review_buyer_id',
                'idx_review_created_at', 
                'idx_review_product_id',
                'idx_review_seller_id'
            ]
            
            existing_index_names = [idx[0] for idx in indexes]
            
            print("\nСтатус индексов из миграции:")
            for idx_name in expected_indexes:
                exists = idx_name in existing_index_names
                print(f"  - {idx_name}: {'СУЩЕСТВУЕТ' if exists else 'ОТСУТСТВУЕТ'}")
            
        except Exception as e:
            print(f"Ошибка при проверке индексов: {e}")

if __name__ == "__main__":
    check_review_indexes()
