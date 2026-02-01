#!/usr/bin/env python3
"""
Скрипт для создания таблицы сообщений в базе данных
"""

from sqlalchemy import inspect, text

from app import create_app, db
from app.models import Message


def create_messages_table():
    """Создает таблицу сообщений если она не существует"""

    app = create_app()

    with app.app_context():
        print("[INFO] Проверяем существование таблицы message...")

        try:
            # Проверяем существование таблицы
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()

            if "message" not in tables:
                print("[INFO] Таблица message не найдена, создаем...")

                # Создаем таблицу напрямую через SQL
                db.session.execute(
                    text("""
                    CREATE TABLE message (
                        id SERIAL PRIMARY KEY,
                        sender_id INTEGER NOT NULL REFERENCES "user"(id),
                        recipient_id INTEGER NOT NULL REFERENCES "user"(id),
                        subject VARCHAR(200) NOT NULL,
                        body TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        is_read BOOLEAN DEFAULT FALSE,
                        is_deleted_by_sender BOOLEAN DEFAULT FALSE,
                        is_deleted_by_recipient BOOLEAN DEFAULT FALSE,
                        product_id INTEGER REFERENCES product(id)
                    )
                """)
                )

                # Создаем индексы для оптимизации
                db.session.execute(
                    text("""
                    CREATE INDEX idx_message_sender_id ON message(sender_id);
                """)
                )

                db.session.execute(
                    text("""
                    CREATE INDEX idx_message_recipient_id ON message(recipient_id);
                """)
                )

                db.session.execute(
                    text("""
                    CREATE INDEX idx_message_created_at ON message(created_at);
                """)
                )

                db.session.execute(
                    text("""
                    CREATE INDEX idx_message_is_read ON message(is_read);
                """)
                )

                db.session.commit()
                print("[SUCCESS] Таблица message создана успешно!")

            else:
                print("[OK] Таблица message уже существует")

                # Проверим структуру существующей таблицы
                columns = [col["name"] for col in inspector.get_columns("message")]
                print(f"[INFO] Колонки в таблице: {', '.join(columns)}")

                # Проверим и добавим недостающие колонки если нужно
                required_columns = {
                    "id": "SERIAL PRIMARY KEY",
                    "sender_id": "INTEGER NOT NULL",
                    "recipient_id": "INTEGER NOT NULL",
                    "subject": "VARCHAR(200) NOT NULL",
                    "body": "TEXT NOT NULL",
                    "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
                    "is_read": "BOOLEAN DEFAULT FALSE",
                    "is_deleted_by_sender": "BOOLEAN DEFAULT FALSE",
                    "is_deleted_by_recipient": "BOOLEAN DEFAULT FALSE",
                    "product_id": "INTEGER",
                }

                for col_name, col_type in required_columns.items():
                    if col_name not in columns:
                        print(f"[INFO] Добавляем недостающую колонку: {col_name}")
                        db.session.execute(
                            text(
                                f"ALTER TABLE message ADD COLUMN {col_name} {col_type}"
                            )
                        )

                db.session.commit()
                print("[OK] Структура таблицы проверена и обновлена")

        except Exception as e:
            print(f"[ERROR] Ошибка при создании таблицы message: {e}")
            db.session.rollback()
            raise


if __name__ == "__main__":
    create_messages_table()
    print("[SUCCESS] Миграция завершена!")
