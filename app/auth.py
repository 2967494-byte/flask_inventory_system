from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models import User
import logging

# === ДОБАВЬТЕ ЭТОТ ИМПОРТ ===
from app.telegram_bot import telegram_bot

auth = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            email = request.form['email']
            password = request.form['password']
            confirm_password = request.form['confirm_password']
            username = request.form.get('username') or email.split('@')[0]
            
            if password != confirm_password:
                flash('Пароли не совпадают', 'error')
                return redirect(url_for('auth.register'))
            
            if User.query.filter_by(email=email).first():
                flash('Пользователь с таким email уже существует', 'error')
                return redirect(url_for('auth.register'))
            
            if User.query.filter_by(username=username).first():
                flash('Пользователь с таким именем пользователя уже существует', 'error')
                return redirect(url_for('auth.register'))
            
            if 'agree_terms' not in request.form:
                flash('Необходимо согласие с условиями использования', 'error')
                return redirect(url_for('auth.register'))
            
            new_user = User(
                email=email,
                username=username,
                company_name=request.form['company_name'],
                inn=request.form['inn'],
                legal_address=request.form['legal_address'],
                contact_person=request.form['contact_person'],
                position=request.form['position'],
                phone=request.form['phone'],
                industry=request.form.get('industry', ''),
                about=request.form.get('about', '')
            )
            new_user.set_password(password)
            
            db.session.add(new_user)
            db.session.commit()
            
            # === ДОБАВЬТЕ ЭТОТ КОД ДЛЯ TELEGRAM УВЕДОМЛЕНИЯ ===
            try:
                # Проверяем, включен ли Telegram бот
                from flask import current_app
                if current_app.config.get('TELEGRAM_ENABLED', True):
                    success = telegram_bot.send_new_user_notification(new_user)
                    if success:
                        logger.info(f"✅ Telegram уведомление отправлено о новом пользователе: {username}")
                    else:
                        logger.warning(f"⚠️ Не удалось отправить Telegram уведомление о пользователе: {username}")
            except Exception as e:
                logger.error(f"❌ Ошибка при отправке Telegram уведомления: {e}")
                # Не прерываем регистрацию из-за ошибки Telegram
            # === КОНЕЦ ДОБАВЛЕННОГО КОДА ===
            
            # =========== ДОБАВЬТЕ ЭТОТ ИМПОРТ ===========
            try:
                from .telegram_bot import telegram_bot
                TELEGRAM_BOT_AVAILABLE = True
            except ImportError:
                telegram_bot = None
                TELEGRAM_BOT_AVAILABLE = False
                print("⚠️ Telegram бот не доступен в auth.py")
            # ============================================

            if TELEGRAM_BOT_AVAILABLE and telegram_bot:
                try:
                    if current_app.config.get('TELEGRAM_ENABLED', True):
                        success = telegram_bot.send_new_user_notification(new_user)
                        if success:
                            logger.info(f"✅ Telegram уведомление отправлено о новом пользователе: {new_user.username}")
                        else:
                            logger.warning(f"⚠️ Не удалось отправить Telegram уведомление о пользователе: {new_user.username}")
                except Exception as e:
                    logger.error(f"❌ Ошибка при отправке Telegram уведомления: {e}")
                    # Не прерываем регистрацию из-за ошибки Telegram
            else:
                logger.info("ℹ️ Telegram бот не доступен, уведомление не отправлено")

            # Автоматический вход после регистрации
            login_user(new_user)
            flash('Регистрация успешна! Вы вошли в систему.', 'success')
            return redirect(url_for('main.dashboard'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при регистрации: {str(e)}', 'error')
            return redirect(url_for('auth.register'))
    
    return render_template('register.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash('Вы успешно вошли в систему!', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Неверный email или пароль', 'error')
    
    return render_template('login.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('main.index'))

@auth.route('/debug_register')
def debug_register():
    return render_template('debug_register.html')