# 1. Восстановим оригинальный config.py, но с правильным паролем
cat > /opt/flask_inventory_system/config.py << 'EOF'
import os
import tempfile

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-123'

    # Определяем среду
    is_production = os.environ.get('DATABASE_URL') is not None
    
    if is_production:
        # Для продакшена (Selectel, Render, Heroku и т.д.)
        database_url = os.environ.get('DATABASE_URL', '')
        
        # Исправляем URL и добавляем диалект для psycopg3
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql+psycopg://", 1)
        elif database_url.startswith("postgresql://"):
            # Меняем диалект на psycopg3
            database_url = database_url.replace("postgresql://", "postgresql+psycopg://", 1)
        
        SQLALCHEMY_DATABASE_URI = database_url
        DEBUG = False
        # print(f"🚀 ПРОДАКШЕН: Используется PostgreSQL с psycopg3")
        
        # В продакшене используем временную папку (лучше настроить S3 в будущем)
        UPLOAD_FOLDER = '/opt/flask_inventory_system/app/static/uploads'
        
    else:
        # Локальная разработка - ОБНОВЛЕН ПАРОЛЬ!
        SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg://postgres:Mat604192@localhost:5432/flask_inventory'
        DEBUG = True
        # print("💻 РАЗРАБОТКА: Локальный PostgreSQL")
        
        UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app', 'static', 'uploads')
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

    # Telegram Bot настройки
    TELEGRAM_BOT_TOKEN = '8576859315:AAFUsWf2_L2ZaJEE8lUxTgOxK_e2IlOTnD0' 
    TELEGRAM_CHAT_ID = '390300'  # Ваш Chat ID
    TELEGRAM_ENABLED = True

    # Email settings
    MAIL_SERVER = 'mail.hosting.reg.ru'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = 'no-reply@asauda.ru'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or '!Mat604192'
    MAIL_DEFAULT_SENDER = 'no-reply@asauda.ru'

    # DaData API
    DADATA_API_KEY = os.environ.get('DADATA_API_KEY') or '101eb3d6682561b0db5bf155c592a3f8dad52dcf'
EOF

# 2. Добавим load_dotenv() в app/__init__.py перед созданием приложения
sed -i '1s/^/from dotenv import load_dotenv\nload_dotenv()\n/' /opt/flask_inventory_system/app/__init__.py

# 3. Проверим, что добавилось
head -10 /opt/flask_inventory_system/app/__init__.py

# 4. Проверим работу приложения
cd /opt/flask_inventory_system
python3 -c "
from app import create_app
app = create_app()
print('Приложение создано успешно!')
print('DATABASE_URL:', app.config['SQLALCHEMY_DATABASE_URI'])
print('DEBUG:', app.config['DEBUG'])
"

# 5. Запустим gunicorn для теста
pkill -f gunicorn
sudo -u www-data /opt/flask_inventory_system/venv/bin/gunicorn \
    --workers 1 \
    --bind 127.0.0.1:8000 \
    wsgi:app &
sleep 3
curl -s http://127.0.0.1:8000/ | head -20 || echo "Ошибка"
pkill -f gunicorn