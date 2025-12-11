from flask import Flask, g
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from time import time
import os

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()

# =========== ДОБАВЬТЕ ЭТО ===========
try:
    from .telegram_bot import telegram_bot
except ImportError as e:
    print(f"⚠️ Не удалось импортировать Telegram бот: {e}")
    telegram_bot = None
# ====================================

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    # Инициализация расширений
    db.init_app(app)
    migrate.init_app(app, db) 
    login_manager.init_app(app)
    csrf.init_app(app)
    
    # =========== ДОБАВЬТЕ ЭТО ===========
    # Инициализируем Telegram бота
    if telegram_bot:
        telegram_bot.init_app(app)
        print(f"✅ Telegram бот инициализирован: токен={'установлен' if app.config.get('TELEGRAM_BOT_TOKEN') else 'не указан'}, chat_id={app.config.get('TELEGRAM_CHAT_ID')}")
    else:
        print("⚠️ Telegram бот не загружен")
    # ====================================
    
    @app.before_request
    def before_request():
        g.start_time = time()

    @app.context_processor
    def inject_generation_time():
        if hasattr(g, 'start_time'):
            elapsed = (time() - g.start_time) * 1000  # мс
            return {'generation_time_ms': f"{elapsed:.2f}"}
        return {'generation_time_ms': '0.00'}

    # Настройки login_manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Пожалуйста, войдите в систему для доступа к этой странице.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return db.session.get(User, int(user_id))

    # Импортируем Region для Flask-Admin
    from app.models import Region
    
    # Создаем папку для загрузок
    try:
        upload_folder = app.config.get('UPLOAD_FOLDER')
        if upload_folder:
            os.makedirs(upload_folder, exist_ok=True)
            print(f"✅ Папка загрузок: {upload_folder}")
            
            # Проверяем доступность папки
            test_file = os.path.join(upload_folder, 'test.txt')
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            print("✅ Папка загрузок доступна для записи")
    except Exception as e:
        print(f"⚠️ Ошибка папки загрузок: {e}")
    
    # Регистрация blueprint
    from app.routes import main
    from app.auth import auth
    from app.admin import admin_bp  # ← только один импорт

    # Flask-Admin
    from flask_admin import Admin
    from flask_admin.contrib.sqla import ModelView

    admin_flask = Admin(app, name='Админка')
    admin_flask.add_view(ModelView(Region, db.session, name='Регионы', category='Справочники'))

    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(admin_bp)  # ← только одна регистрация
    
    print("=" * 50)
    print("🎉 Приложение инициализировано успешно!")
    print("=" * 50)
    
    return app