from datetime import datetime
import os
import uuid
import traceback
from sqlalchemy import func, distinct

from flask import (
    Blueprint,
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    send_file,
    send_from_directory,
    session,
    url_for,
)
from flask_login import current_user, login_required
from PIL import Image
from sqlalchemy.orm import joinedload
from werkzeug.utils import secure_filename

from app import csrf, db
from app.models import Category, City, Message, Product, Region, Review, User, AnalyticsEvent, News

main = Blueprint("main", __name__, template_folder="../../templates")

try:
    from app.forms import ReviewForm
except ImportError:

    class ReviewForm:
        def __init__(self, *args, **kwargs):
            pass

        def validate_on_submit(self):
            return False


from app.utils import (
    _deserialize_images,
    _serialize_images,
    allowed_file,
    process_category_image,
    track_event,
)


@main.app_template_filter("deserialize_images")
def deserialize_images_filter(images_field):
    """Jinja-фильтр для безопасной десериализации изображений"""
    return _deserialize_images(images_field)

# === АНАЛИТИКА: Трекинг посещений ===
@main.before_app_request
def track_visits():
    """Записывает посещение страницы"""
    if request.path.startswith('/static') or request.path.startswith('/uploads'):
        return
    
    # Не трекаем админку и системные запросы в 'visit', чтобы не засорять
    if request.path.startswith('/admin') or request.path.startswith('/api'):
        return

    track_event('visit', current_user, url_path=request.path)

# === АНАЛИТИКА: API для клика по телефону ===
@main.route("/api/track-phone/<int:product_id>", methods=['POST'])
def track_phone_click(product_id):
    """AJAX endpoint для трекинга нажатия 'Показать телефон'"""
    # CSRF отключен, так как это публичный AJAX, но лучше включить
    # В данном случае csrf.exempt не нужен, если фронт шлет токен
    track_event('show_phone', current_user, resource_id=product_id, url_path=request.referrer)
    return jsonify({'status': 'ok'})

# === АНАЛИТИКА: Страница статистики ===
@main.route("/admin/stats")
@login_required
def admin_stats():
    """Страница статистики по дням"""
    if not current_user.role == 'admin': # Простая проверка прав, если нет поля is_admin
         if not getattr(current_user, 'is_admin', False): # Fallback
            flash('Доступ запрещен', 'error')
            return redirect(url_for('main.index'))
            
    date_str = request.args.get('date')
    if date_str:
        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            target_date = datetime.utcnow().date()
    else:
        target_date = datetime.utcnow().date()
        
    # --- Сбор статистики за выбранный день ---
    
    # 1. Уникальные посетители (всего)
    # Считаем уникальные fingerprint
    unique_visitors = db.session.query(func.count(distinct(AnalyticsEvent.fingerprint)))\
        .filter(func.date(AnalyticsEvent.created_at) == target_date)\
        .scalar()
        
    # 2. Новые регистрации
    registrations = db.session.query(func.count(AnalyticsEvent.id))\
        .filter(func.date(AnalyticsEvent.created_at) == target_date)\
        .filter(AnalyticsEvent.event_type == 'register')\
        .scalar()
        
    # 3. Клики "Показать телефон" (уникальные пользователи)
    phone_clicks_unique = db.session.query(func.count(distinct(AnalyticsEvent.fingerprint)))\
        .filter(func.date(AnalyticsEvent.created_at) == target_date)\
        .filter(AnalyticsEvent.event_type == 'show_phone')\
        .scalar()
        
    # 4. Просмотры товаров (кто выбрал товары - зашел в карточку)
    # event_type='view_product' - мы его добавим в product_detail
    product_views_unique = db.session.query(func.count(distinct(AnalyticsEvent.fingerprint)))\
        .filter(func.date(AnalyticsEvent.created_at) == target_date)\
        .filter(AnalyticsEvent.event_type == 'view_product')\
        .scalar()
        
    # 5. Посещения по страницам (Топ-20)
    page_stats = db.session.query(
            AnalyticsEvent.url_path, 
            func.count(distinct(AnalyticsEvent.fingerprint)).label('unique_users'),
            func.count(AnalyticsEvent.id).label('total_hits')
        )\
        .filter(func.date(AnalyticsEvent.created_at) == target_date)\
        .group_by(AnalyticsEvent.url_path)\
        .order_by(func.count(distinct(AnalyticsEvent.fingerprint)).desc())\
        .limit(50)\
        .all()
        
    return render_template('admin_stats.html', 
                         target_date=target_date,
                         unique_visitors=unique_visitors,
                         registrations=registrations,
                         phone_clicks=phone_clicks_unique,
                         product_views=product_views_unique,
                         page_stats=page_stats)


@main.route("/privacy-policy")
def privacy_policy():
    return render_template("policy.html")


@main.route("/help")
def help():
    return render_template("help.html")


@main.route("/system-description")
def system_description():
    return render_template("system_description.html")


# Debug route
@main.route("/debug/admin")
@login_required
def debug_admin():
    """Отладочная информация для админ-панели"""
    if not current_user.is_admin:
        return "Access denied", 403
    
    try:
        debug_info = {
            'user_id': current_user.id,
            'user_email': current_user.email,
            'method': request.method,
            'categories_count': Category.query.count(),
            'regions_count': Region.query.count(),
            'cities_count': City.query.count(),
            'products_count': Product.query.count(),
            'db_connection': str(db.engine.url) if db.engine else 'No engine'
        }
        
        return f"""
        <h1>Debug Info</h1>
        <pre>
{str(debug_info)}
        </pre>
        """
    except Exception as e:
        return f"""
        <h1>Debug Error</h1>
        <pre>
        Error: {str(e)}
        Traceback: {traceback.format_exc()}
        </pre>
        """


@main.route("/admin/categories", methods=['GET', 'POST'])
@login_required
def admin_categories():
    try:
        # Отладочная информация
        current_app.logger.info(f'admin_categories accessed by user {current_user.id}, method: {request.method}')
        
        if request.method == 'POST':
            action = request.form.get('action')
            current_app.logger.info(f'POST action: {action}')
            
            if action == 'add_category':
                name = request.form.get('name')
                parent_id = request.form.get('parent_id') or None
                description = request.form.get('description')
                
                current_app.logger.info(f'add_category: name={name}, parent_id={parent_id}')
                
                if not name:
                    flash('Название категории обязательно', 'error')
                    return redirect(url_for('main.admin_categories'))
                
                existing_category = Category.query.filter_by(name=name, parent_id=parent_id).first()
                if existing_category:
                    flash('Такая категория уже существует', 'error')
                    return redirect(url_for('main.admin_categories'))
                
                # === ОБРАБОТКА ЗАГРУЗКИ ИЗОБРАЖЕНИЯ ===
                image_filename = None
                if 'category_image' in request.files:
                    image_file = request.files['category_image']
                    if image_file and image_file.filename:
                        current_app.logger.info(f'Processing image: {image_file.filename}')
                        image_filename, error = process_category_image(image_file)
                        if error:
                            flash(f'Ошибка обработки изображения: {error}', 'warning')
                            current_app.logger.error(f'Image processing error: {error}')
                
                # === КОНЕЦ ОБРАБОТКИ ИЗОБРАЖЕНИЯ ===
                
                new_category = Category(
                    name=name,
                    description=description,
                    parent_id=parent_id if parent_id else None,
                    image=image_filename
                )
                db.session.add(new_category)
                db.session.commit()
                flash(f'Категория "{name}" успешно добавлена', 'success')
                current_app.logger.info(f'Category "{name}" added successfully')
        
        # ========== ОЧИСТКА НАЗВАНИЙ РЕГИОНОВ ==========
        current_app.logger.info('Starting region names cleanup')
        regions_to_clean = Region.query.filter(Region.name.like('% - %')).all()
        if regions_to_clean:
            for region in regions_to_clean:
                cleaned_name = region.name.split('-', 1)[-1].strip()
                region.name = cleaned_name
            db.session.commit()
            current_app.logger.info(f'Cleaned {len(regions_to_clean)} region names')
            
        current_app.logger.info('Loading categories for admin panel')
        categories = Category.query.all()
        parent_categories = Category.query.filter_by(parent_id=None).all()
        total_products = Product.query.count()
        current_app.logger.info(f'Loaded {len(categories)} categories, {len(parent_categories)} parent categories, {total_products} total products')
        
        all_regions = Region.query.all()
        regions = Region.query.filter_by(parent_id=None).all()
        child_regions = Region.query.filter(Region.parent_id.isnot(None)).all()
        all_cities = City.query.all()
        cities_count = len(all_cities)
        
        # Подсчет категорий с изображениями
        try:
            categories_with_images = Category.query.filter(Category.image.isnot(None)).all()
            current_app.logger.info(f'Categories with images: {len(categories_with_images)}')
        except AttributeError:
            categories_with_images = []
            current_app.logger.warning('AttributeError when counting categories with images')
        
        regions_with_cities = []
        for region in regions:
            region_cities = [city for city in all_cities if city.region_id == region.id]
            regions_with_cities.append({
                'region': region,
                'cities': region_cities
            })
        
        current_app.logger.info('Rendering admin_categories template')
        return render_template('admin_categories.html', 
                         categories=categories,
                         parent_categories=parent_categories,
                         categories_with_images=categories_with_images,
                         total_products=total_products,
                         all_regions=all_regions,
                         regions=regions,
                         child_regions=child_regions,
                         cities=all_cities,
                         cities_count=cities_count,
                         regions_with_cities=regions_with_cities)
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error in admin_categories: {str(e)}')
        current_app.logger.error(traceback.format_exc())
        flash(f'Ошибка в админ-панели: {str(e)}', 'error')
        return redirect(url_for('main.admin_categories'))


# ========== НОВОСТИ ==========
@main.route("/admin/news")
@login_required
def admin_news():
    """Админ-панель управления новостями"""
    try:
        current_app.logger.info(f'admin_news accessed by user {current_user.id}, role: {current_user.role}, is_admin: {current_user.is_admin}')
        
        if not current_user.is_admin:
            current_app.logger.warning(f'Access denied for user {current_user.id}: not admin')
            flash('Доступ запрещен', 'error')
            return redirect(url_for('main.index'))
        
        current_app.logger.info('Fetching news list...')
        news_list = News.query.order_by(News.created_at.desc()).all()
        current_app.logger.info(f'Found {len(news_list)} news items')
        
        return render_template('admin_news.html', news_list=news_list)
    except Exception as e:
        current_app.logger.error(f'Error in admin_news: {str(e)}')
        current_app.logger.error(traceback.format_exc())
        flash(f'Ошибка: {str(e)}', 'error')
        return redirect(url_for('main.index'))


@main.route("/admin/news/add", methods=['GET', 'POST'])
@login_required
def admin_add_news():
    """Добавление новости"""
    if not current_user.is_admin:
        flash('Доступ запрещен', 'error')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        
        if not title or not content:
            flash('Заголовок и текст обязательны', 'error')
            return redirect(url_for('main.admin_add_news'))
        
        # Обработка загрузки изображения
        image_filename = None
        if 'image' in request.files:
            image_file = request.files['image']
            if image_file and image_file.filename:
                # Создаем безопасное имя файла
                filename = secure_filename(image_file.filename)
                # Добавляем уникальный префикс
                unique_filename = f"{uuid.uuid4().hex}_{filename}"
                image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
                
                # Создаем папку, если не существует
                os.makedirs(os.path.dirname(image_path), exist_ok=True)
                
                # Обрабатываем и сжимаем изображение
                try:
                    # Открываем изображение
                    img = Image.open(image_file)
                    
                    # Конвертируем в RGB если нужно (для JPEG)
                    if img.mode in ('RGBA', 'LA', 'P'):
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        if img.mode == 'P':
                            img = img.convert('RGBA')
                        background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                        img = background
                    
                    # Уменьшаем размер изображения
                    max_width = 800  # Максимальная ширина
                    max_height = 600  # Максимальная высота
                    img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
                    
                    # Сохраняем с качеством 85%
                    img.save(image_path, 'JPEG', quality=85, optimize=True)
                    image_filename = unique_filename
                    
                except Exception as e:
                    current_app.logger.error(f'Error processing image: {str(e)}')
                    # Если обработка не удалась, сохраняем как есть
                    image_file.save(image_path)
                    image_filename = unique_filename
        
        news = News(title=title, content=content, image=image_filename)
        db.session.add(news)
        db.session.commit()
        flash('Новость успешно добавлена', 'success')
        return redirect(url_for('main.admin_news'))
    
    return render_template('admin_news_form.html')


@main.route("/admin/news/<int:news_id>/edit", methods=['GET', 'POST'])
@login_required
def admin_edit_news(news_id):
    """Редактирование новости"""
    if not current_user.is_admin:
        flash('Доступ запрещен', 'error')
        return redirect(url_for('main.index'))
    
    news = News.query.get_or_404(news_id)
    
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        
        if not title or not content:
            flash('Заголовок и текст обязательны', 'error')
            return redirect(url_for('main.admin_edit_news', news_id=news_id))
        
        # Обработка загрузки нового изображения
        if 'image' in request.files:
            image_file = request.files['image']
            if image_file and image_file.filename:
                # Создаем безопасное имя файла
                filename = secure_filename(image_file.filename)
                # Добавляем уникальный префикс
                unique_filename = f"{uuid.uuid4().hex}_{filename}"
                image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
                
                # Создаем папку, если не существует
                os.makedirs(os.path.dirname(image_path), exist_ok=True)
                
                # Обрабатываем и сжимаем изображение
                try:
                    # Открываем изображение
                    img = Image.open(image_file)
                    
                    # Конвертируем в RGB если нужно (для JPEG)
                    if img.mode in ('RGBA', 'LA', 'P'):
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        if img.mode == 'P':
                            img = img.convert('RGBA')
                        background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                        img = background
                    
                    # Уменьшаем размер изображения
                    max_width = 800  # Максимальная ширина
                    max_height = 600  # Максимальная высота
                    img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
                    
                    # Сохраняем с качеством 85%
                    img.save(image_path, 'JPEG', quality=85, optimize=True)
                    
                    # Удаляем старое изображение, если оно было
                    if news.image:
                        old_image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], news.image)
                        if os.path.exists(old_image_path):
                            os.remove(old_image_path)
                    
                    news.image = unique_filename
                    
                except Exception as e:
                    current_app.logger.error(f'Error processing image: {str(e)}')
                    # Если обработка не удалась, сохраняем как есть
                    image_file.save(image_path)
                    
                    # Удаляем старое изображение, если оно было
                    if news.image:
                        old_image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], news.image)
                        if os.path.exists(old_image_path):
                            os.remove(old_image_path)
                    
                    news.image = unique_filename
        
        news.title = title
        news.content = content
        news.updated_at = datetime.utcnow()
        db.session.commit()
        flash('Новость успешно обновлена', 'success')
        return redirect(url_for('main.admin_news'))
    
    return render_template('admin_news_form.html', news=news)


@main.route("/admin/news/<int:news_id>/delete", methods=['POST'])
@login_required
def admin_delete_news(news_id):
    """Удаление новости"""
    if not current_user.is_admin:
        flash('Доступ запрещен', 'error')
        return redirect(url_for('main.index'))
    
    news = News.query.get_or_404(news_id)
    
    if request.form.get('confirm') == 'yes':
        db.session.delete(news)
        db.session.commit()
        flash('Новость успешно удалена', 'success')
        return redirect(url_for('main.admin_news'))
    
    return redirect(url_for('main.admin_news'))


@main.route("/news/<int:news_id>")
def news_detail(news_id):
    """Детальная страница новости"""
    news = News.query.get_or_404(news_id)
    return render_template('news_detail.html', news=news)


@main.route("/")
def index():
    category_id = request.args.get("category_id")
    search_term = request.args.get("search", "").strip()
    location = request.args.get("location", "").strip()

    # Advanced filters
    region_id = request.args.get("region_id", type=int)
    city_id = request.args.get("city_id", type=int)
    price_min = request.args.get("price_min", type=float)
    price_max = request.args.get("price_max", type=float)
    with_vat = request.args.get("with_vat") == "on"
    with_delivery = request.args.get("with_delivery") == "on"
    condition = request.args.get("condition")
    sort_by = request.args.get("sort_by", "newest")

    query = Product.query.filter_by(status=Product.STATUS_PUBLISHED)

    if category_id and category_id.isdigit():
        cat_id = int(category_id)
        # Recursive category filtering
        category = Category.query.get(cat_id)
        if category:
            all_cat_ids = [cat_id]
            # Collecting all descendants
            stack = [category]
            while stack:
                curr = stack.pop()
                for child in curr.children:
                    all_cat_ids.append(child.id)
                    stack.append(child)
            query = query.filter(Product.category_id.in_(all_cat_ids))
        else:
            query = query.filter_by(category_id=cat_id)

    if search_term:
        query = query.filter(
            Product.title.ilike(f"%{search_term}%")
            | Product.description.ilike(f"%{search_term}%")
        )

    if location and location != "Все регионы":
        query = query.filter((Product.region == location) | (Product.city == location))

    # Apply new filters
    if region_id:
        query = query.filter_by(region_id=region_id)
    if city_id:
        query = query.filter_by(city_id=city_id)
    if price_min is not None:
        query = query.filter(Product.price >= price_min)
    if price_max is not None:
        query = query.filter(Product.price <= price_max)
    if with_vat:
        query = query.filter_by(vat_included=True)
    if with_delivery:
        query = query.filter_by(delivery=True)
    if condition:
        query = query.filter_by(condition=condition)

    # Sorting
    if sort_by == "cheapest":
        query = query.order_by(Product.price.asc())
    elif sort_by == "expensive":
        query = query.order_by(Product.price.desc())
    else:  # newest
        query = query.order_by(Product.created_at.desc())

    query = query.options(joinedload(Product.product_category))
    
    # --- Pagination ---
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 12, type=int)
    pagination = query.order_by(Product.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    products = pagination.items
    # ------------------

    # Используем иерархический список категорий (список словарей)
    from app.utils import get_category_choices

    categories = get_category_choices()

    # Для плиток категорий (только верхний уровень)
    root_categories = (
        Category.query.filter_by(parent_id=None).order_by(Category.name).all()
    )

    # For filter modal
    all_regions = Region.query.order_by(Region.name).all()

    # Check for sidebar banner
    sidebar_banner = None
    banner_folder = os.path.join(current_app.static_folder, "img/ads")
    if os.path.exists(banner_folder):
        for ext in ["jpg", "jpeg", "png", "gif"]:
            if os.path.exists(os.path.join(banner_folder, f"sidebar_banner.{ext}")):
                sidebar_banner = f"sidebar_banner.{ext}"
                break

    # Get news for main page
    news_list = News.query.filter_by(is_active=True).order_by(News.created_at.desc()).limit(3).all()

    return render_template(
        "main.html",
        products=products,
        pagination=pagination,
        categories=categories,
        root_categories=root_categories,
        search_term=search_term,
        sidebar_banner=sidebar_banner,
        regions=all_regions,
        news_list=news_list,
    )


@main.route("/dashboard")
@login_required
def dashboard():
    """User's products dashboard"""
    user_products = (
        Product.query.options(joinedload(Product.product_category))
        .filter_by(user_id=current_user.id)
        .order_by(Product.created_at.desc())
        .all()
    )

    # Автоматически снимаем с публикации просроченные товары
    expired_count = Product.query.filter(
        Product.user_id == current_user.id,
        Product.status == Product.STATUS_PUBLISHED,
        Product.expires_at <= datetime.utcnow(),
    ).update({Product.status: Product.STATUS_READY_FOR_PUBLICATION})
    if expired_count > 0:
        db.session.commit()
        # После коммита перезагружаем данные
        user_products = (
            Product.query.options(joinedload(Product.product_category))
            .filter_by(user_id=current_user.id)
            .order_by(Product.created_at.desc())
            .all()
        )

    # Добавляем image_list к каждому объекту Product для корректного отображения в шаблоне
    for product in user_products:
        product.image_list = _deserialize_images(product.images)

    # Подготавливаем JSON-данные для JS (остаётся как есть)
    products_data = []
    for product in user_products:
        product_dict = {
            "id": product.id,
            "title": product.title,
            "description": product.description,
            "price": product.price,
            "quantity": product.quantity,
            "manufacturer": product.manufacturer,
            "category_id": product.category_id,
            "images": _deserialize_images(product.images),
            "status": product.status,
            "status_text": product.status_text,
            "created_at": product.created_at.isoformat()
            if product.created_at
            else None,
            "expires_at": product.expires_at.isoformat()
            if product.expires_at
            else None,
            "view_count": product.view_count,
            "vat_included": product.vat_included,
            "condition": product.condition,
            "region": product.region,
            "city": product.city,
            "delivery": product.delivery,
            "days_remaining": product.days_remaining,
            "is_expired": product.is_expired,
            "product_category": {
                "id": product.product_category.id if product.product_category else None,
                "name": product.product_category.name
                if product.product_category
                else None,
            }
            if product.product_category
            else None,
        }
        products_data.append(product_dict)

    return render_template(
        "dashboard.html",
        products=user_products,
        products_json=products_data,
        now=datetime.utcnow(),
    )


@main.route("/product/<int:product_id>")
def product_detail(product_id):
    product = Product.query.options(
        joinedload(Product.product_category), joinedload(Product.owner)
    ).get_or_404(product_id)
    can_view = product.status == Product.STATUS_PUBLISHED or (
        current_user.is_authenticated
        and (current_user.id == product.user_id or current_user.role == "admin")
    )
    if not can_view:
        flash("Этот товар недоступен для просмотра", "error")
        return redirect(url_for("main.index"))
    if product.status == Product.STATUS_PUBLISHED:
        product.view_count = (product.view_count or 0) + 1
        db.session.commit()
    
    # Трекинг просмотра для аналитики
    track_event('view_product', current_user, resource_id=product.id, url_path=request.path)
    
    return render_template("product_detail.html", product=product)


@main.route("/add_product", methods=["GET", "POST"])
@login_required
def add_product():
    if request.method == "POST":
        try:
            title = request.form.get("title")
            description = request.form.get("description")
            price = request.form.get("price")
            category_id_str = request.form.get("category_id", "").strip()
            if not title:
                flash("Название товара обязательно для заполнения", "error")
                return redirect(url_for("main.add_product"))
            if not title:
                flash("Название товара обязательно для заполнения", "error")
                return redirect(url_for("main.add_product"))
            # Price is now optional
            # if not price:
            #    flash('Цена товара обязательна для заполнения', 'error')
            #    return redirect(url_for('main.add_product'))
            if not category_id_str:
                flash("Категория товара обязательна для выбора", "error")
                return redirect(url_for("main.add_product"))
            try:
                category_id_int = int(category_id_str)
            except (ValueError, TypeError):
                flash("Некорректный выбор категория", "error")
                return redirect(url_for("main.add_product"))
            category = Category.query.get(category_id_int)
            if not category:
                flash("Выбранная категория не существует", "error")
                return redirect(url_for("main.add_product"))
            region_id = request.form.get("region_id")
            city_id = request.form.get("city_id")
            old_region = request.form.get("old_region", "").strip()
            old_city = request.form.get("old_city", "").strip()
            region_name = None
            city_name = None
            if region_id:
                region = Region.query.get(int(region_id))
                region_name = region.name if region else old_region
            else:
                region_name = old_region
            if city_id:
                city = City.query.get(int(city_id))
                city_name = city.name if city else old_city
            else:
                city_name = old_city
            if not region_name:
                flash("Субъект РФ обязателен для выбора", "error")
                return redirect(url_for("main.add_product"))
            if not city_name:
                flash("Город обязателен для выбора", "error")
                return redirect(url_for("main.add_product"))

            # === Получение и валидация количества и производителя ===
            quantity_str = request.form.get("quantity", "1")
            manufacturer = request.form.get("manufacturer", "").strip()

            try:
                quantity = int(quantity_str)
                if quantity < 1:
                    quantity = 1
            except (ValueError, TypeError):
                quantity = 1
            # === Конец получения количества и производителя ===

            uploaded_files = request.files.getlist("image_files")
            new_images = []
            if uploaded_files and any(f.filename for f in uploaded_files):
                for file in uploaded_files:
                    if file and file.filename:
                        if not allowed_file(file.filename):
                            flash(
                                "Недопустимый тип файла. Разрешены: png, jpg, jpeg, gif, webp",
                                "error",
                            )
                            return redirect(url_for("main.add_product"))
                        filename = secure_filename(file.filename)
                        unique_filename = f"{uuid.uuid4().hex}_{filename}"
                        file_path = os.path.join(
                            current_app.config["UPLOAD_FOLDER"], unique_filename
                        )
                        try:
                            file.save(file_path)
                            new_images.append(unique_filename)
                        except Exception as e:
                            print(f"[ERROR] Failed to save file {file_path}: {e}")
                            flash(f"Ошибка при сохранении файла {filename}", "error")

            # === ЦЕНА И ТИП ЦЕНЫ ===
            price_val = request.form.get("price")
            price_type = request.form.get("price_type", "fixed")

            final_price = None
            if not price_val or price_val.strip() == "":
                price_type = "negotiable"
                final_price = None
            else:
                final_price = float(price_val)
            # =======================

            new_product = Product(
                title=title,
                description=description,
                price=final_price,
                price_type=price_type,
                quantity=quantity,
                manufacturer=manufacturer,
                category_id=category_id_int,
                user_id=current_user.id,
                images=",".join(new_images) if new_images else None,
                status=Product.STATUS_PUBLISHED,
                vat_included=request.form.get("vat_included") == "on",
                condition=request.form.get("condition", "new"),
                region=region_name,
                city=city_name,
                region_id=int(region_id) if region_id else None,
                city_id=int(city_id) if city_id else None,
                delivery=request.form.get("delivery") == "on",
            )
            db.session.add(new_product)
            db.session.commit()
            flash("Товар успешно добавлен! Срок размещения - 30 дней", "success")
            return redirect(url_for("main.dashboard"))
        except ValueError as e:
            flash(f"Некорректное значение: {str(e)}", "error")
            return redirect(url_for("main.add_product"))
        except Exception as e:
            db.session.rollback()
            flash(f"Ошибка при добавлении товара: {str(e)}", "error")
            return redirect(url_for("main.add_product"))
    categories = Category.query.filter_by(parent_id=None).order_by(Category.name).all()
    if not categories:
        flash("Прежде чем добавлять товары, создайте хотя бы одну категорию", "warning")
        return redirect(url_for("main.admin_categories"))
    regions = Region.query.filter_by(parent_id=None).order_by(Region.name).all()
    return render_template("add_product.html", categories=categories, regions=regions)


@main.route("/product/<int:product_id>/renew", methods=["POST"])
@login_required
def renew_product(product_id):
    product = Product.query.get_or_404(product_id)
    if product.user_id != current_user.id:
        flash("У вас нет прав для продления этого товара", "error")
        return redirect(url_for("main.product_detail", product_id=product_id))
    if product.status not in [
        Product.STATUS_READY_FOR_PUBLICATION,
        Product.STATUS_UNPUBLISHED,
    ]:
        flash("Этот товар нельзя опубликовать", "error")
        return redirect(url_for("main.product_detail", product_id=product_id))
    try:
        product.publish()
        db.session.commit()
        flash("Товар успешно опубликован! Срок размещения - 30 дней", "success")
    except Exception as e:
        db.session.rollback()
        flash("Ошибка при публикации товара", "error")
    return redirect(url_for("main.dashboard"))


@main.route("/product/<int:product_id>/unpublish", methods=["POST"])
@login_required
def unpublish_product(product_id):
    product = Product.query.get_or_404(product_id)
    if product.user_id != current_user.id:
        flash("У вас нет прав для снятия этого товара с публикации", "error")
        return redirect(url_for("main.product_detail", product_id=product_id))
    if product.status != Product.STATUS_PUBLISHED:
        flash("Этот товар уже не опубликован", "error")
        return redirect(url_for("main.product_detail", product_id=product_id))
    try:
        product.unpublish()
        db.session.commit()
        flash("Товар снят с публикации. Теперь он виден только вам.", "success")
    except Exception as e:
        db.session.rollback()
        flash("Ошибка при снятии товара с публикации", "error")
    return redirect(url_for("main.dashboard"))


@main.route("/product/<int:product_id>/edit", methods=["GET", "POST"])
@login_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    if product.user_id != current_user.id and current_user.role != "admin":
        flash("У вас нет прав для редактирования этого товара", "error")
        return redirect(url_for("main.product_detail", product_id=product_id))
    if request.method == "POST":
        try:
            title = request.form.get("title")
            description = request.form.get("description")
            price = request.form.get("price")
            category_id = request.form.get("category_id")
            if not title:
                flash("Название товара обязательно для заполнения", "error")
                return redirect(url_for("main.edit_product", product_id=product_id))
            if not title:
                flash("Название товара обязательно для заполнения", "error")
                return redirect(url_for("main.edit_product", product_id=product_id))
            # Price IS optional now
            # if not price:
            #     flash('Цена товара обязательна для заполнения', 'error')
            #     return redirect(url_for('main.edit_product', product_id=product_id))
            if not category_id:
                flash("Категория товара обязательна для выбора", "error")
                return redirect(url_for("main.edit_product", product_id=product_id))
            category = Category.query.get(int(category_id))
            if not category:
                flash("Выбранная категория не существует", "error")
                return redirect(url_for("main.edit_product", product_id=product_id))
            region_id = request.form.get("region_id")
            city_id = request.form.get("city_id")
            old_region = request.form.get("old_region", "").strip()
            old_city = request.form.get("old_city", "").strip()
            region_name = None
            city_name = None
            if region_id:
                region = Region.query.get(int(region_id))
                region_name = region.name if region else old_region
            else:
                region_name = old_region
            if city_id:
                city = City.query.get(int(city_id))
                city_name = city.name if city else old_city
            else:
                city_name = old_city
            if not region_name:
                flash("Субъект РФ обязателен для выбора", "error")
                return redirect(url_for("main.edit_product", product_id=product_id))
            if not city_name:
                flash("Город обязателен для выбора", "error")
                return redirect(url_for("main.edit_product", product_id=product_id))
            # === ЦЕНА И ТИП ЦЕНЫ (Edit) ===
            price_val = request.form.get("price")
            price_type = request.form.get("price_type", "fixed")

            if not price_val or price_val.strip() == "":
                product.price_type = "negotiable"
                product.price = None
            else:
                product.price = float(price_val)
                product.price_type = price_type
            # ==============================

            product.title = title
            product.description = description
            # Price updated above
            product.quantity = int(request.form.get("quantity", 1))
            product.manufacturer = request.form.get("manufacturer")
            product.category_id = int(category_id)
            product.status = int(request.form.get("status"))
            product.vat_included = request.form.get("vat_included") == "on"
            product.condition = request.form.get("condition", "new")
            product.region = region_name
            product.city = city_name
            product.region_id = int(region_id) if region_id else None
            product.city_id = int(city_id) if city_id else None
            product.delivery = request.form.get("delivery") == "on"
            expires_at_str = request.form.get("expires_at")
            if expires_at_str:
                product.expires_at = datetime.strptime(expires_at_str, "%Y-%m-%dT%H:%M")
            # ========== ИСПРАВЛЕННАЯ ОБРАБОТКА ИЗОБРАЖЕНИЙ ==========
            current_images = _deserialize_images(product.images)
            removed_images = request.form.get("removed_images", "")
            print(
                f"[DEBUG] Edit Product {product_id}: Existing={len(current_images)}, Removed={removed_images}"
            )

            if removed_images:
                removed_list = [
                    img.strip() for img in removed_images.split(",") if img.strip()
                ]
                current_images = [
                    img for img in current_images if img not in removed_list
                ]
                for image_filename in removed_list:
                    image_path = os.path.join(
                        current_app.config["UPLOAD_FOLDER"], image_filename
                    )
                    if os.path.exists(image_path):
                        try:
                            os.remove(image_path)
                            print(f"[DEBUG] Removed file: {image_path}")
                        except Exception as e:
                            print(f"[ERROR] Failed to remove file {image_path}: {e}")

            uploaded_files = request.files.getlist("image_files")
            print(f"[DEBUG] Uploaded files count: {len(uploaded_files)}")

            new_images = []
            if uploaded_files:
                available_slots = 8 - len(current_images)
                print(f"[DEBUG] Available slots: {available_slots}")

                if available_slots <= 0 and any(f.filename for f in uploaded_files):
                    # If trying to add files but no slots
                    print("[WARN] No slots available")
                    # We might want to continue saving other fields even if slots full, just warn.
                    # But current logic redirects. Let's fix this behavior if needed.
                    pass

                files_to_process = []
                for f in uploaded_files:
                    if f and f.filename:
                        # Fix for blobs sometimes having generic names or issues
                        print(
                            f"[DEBUG] Processing file: {f.filename}, Content-Type: {f.content_type}"
                        )
                        if available_slots > 0:
                            files_to_process.append(f)
                            available_slots -= 1

                for file in files_to_process:
                    if not allowed_file(file.filename):
                        print(f"[ERROR] Invalid file type: {file.filename}")
                        flash(f'Файл "{file.filename}" недопустимого типа.', "error")
                        return redirect(
                            url_for("main.edit_product", product_id=product_id)
                        )

                    filename = secure_filename(file.filename)
                    if not filename:
                        filename = "image.jpg"  # Fallback

                    unique_filename = f"{uuid.uuid4().hex}_{filename}"
                    file_path = os.path.join(
                        current_app.config["UPLOAD_FOLDER"], unique_filename
                    )
                    try:
                        file.save(file_path)
                        new_images.append(unique_filename)
                        print(
                            f"[DEBUG] Saved new image: {unique_filename} to {file_path}"
                        )
                    except Exception as e:
                        print(f"[ERROR] Failed to save {filename} to {file_path}: {e}")
                        flash(
                            f"Не удалось сохранить файл {filename}. Проверьте права доступа.",
                            "error",
                        )

            if new_images:
                current_images.extend(new_images)

            current_images = current_images[:8]  # Enforce limit strict
            product.images = _serialize_images(current_images)
            print(f"[DEBUG] Final images list: {current_images}")
            # ========== КОНЕЦ ОБРАБОТКИ ИЗОБРАЖЕНИЙ ==========

            db.session.commit()
            flash("Товар успешно обновлен", "success")
            return redirect(url_for("main.product_detail", product_id=product_id))
        except Exception as e:
            db.session.rollback()
            print(f"[CRITICAL ERROR] Edit Product Failed: {e}")
            import traceback

            traceback.print_exc()
            flash(f"Ошибка при обновлении товара: {str(e)}", "error")
            return redirect(url_for("main.edit_product", product_id=product_id))
    categories = Category.query.filter_by(parent_id=None).order_by(Category.name).all()
    if not categories:
        flash("Нет доступных категорий", "error")
        return redirect(url_for("main.index"))
    regions = Region.query.filter_by(parent_id=None).order_by(Region.name).all()
    cities = []
    if product.region_id:
        cities = (
            City.query.filter_by(region_id=product.region_id).order_by(City.name).all()
        )
    elif product.region:
        region_obj = Region.query.filter_by(name=product.region).first()
        if region_obj:
            product.region_id = region_obj.id
            cities = (
                City.query.filter_by(region_id=region_obj.id).order_by(City.name).all()
            )
    # Десериализуем изображения для корректной передачи в шаблоне
    if product.images:
        if isinstance(product.images, str):
            product_images = [
                img.strip() for img in product.images.split(",") if img.strip()
            ]
        elif isinstance(product.images, list):
            product_images = [img for img in product.images if img]
        else:
            product_images = []
    else:
        product_images = []

    # Get category path for pre-filling
    category_path = (
        product.product_category.get_ancestors() if product.product_category else []
    )

    return render_template(
        "edit_product.html",
        product=product,
        product_images=product_images,
        categories=categories,
        regions=regions,
        cities=cities,
        category_path=category_path,
    )


@main.route("/product/<int:product_id>/delete", methods=["POST"])
@login_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    if product.user_id != current_user.id and current_user.role != "admin":
        flash("У вас нет прав для удаления этого товара", "error")
        return redirect(url_for("main.product_detail", product_id=product_id))
    try:
        if product.images:
            for image_filename in _deserialize_images(product.images):
                if isinstance(image_filename, str) and not image_filename.startswith(
                    "http"
                ):
                    image_path = os.path.join(
                        current_app.config["UPLOAD_FOLDER"], image_filename
                    )
                    if os.path.exists(image_path):
                        os.remove(image_path)
        db.session.delete(product)
        db.session.commit()
        flash("Товар успешно удален", "success")
        return redirect(url_for("main.dashboard"))
    except Exception as e:
        db.session.rollback()
        flash("Ошибка при удалении товара", "error")
        return redirect(url_for("main.product_detail", product_id=product_id))


@main.route("/uploads/<filename>")
def serve_uploaded_file(filename):
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    file_path = os.path.join(upload_folder, filename)
    if os.path.exists(file_path):
        return send_from_directory(upload_folder, filename)
    else:
        return "File not found", 404


@main.route("/dashboard/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        current_user.username = request.form.get("username")
        current_user.company_name = request.form.get("company_name")
        current_user.inn = request.form.get("inn")
        current_user.legal_address = request.form.get("legal_address")
        current_user.contact_person = request.form.get("contact_person")
        current_user.position = request.form.get("position")
        current_user.phone = request.form.get("phone")
        current_user.industry = request.form.get("industry")
        current_user.about = request.form.get("about")
        new_password = request.form.get("new_password")
        if new_password and new_password.strip():
            if len(new_password) < 6:
                flash("Пароль должен содержать минимум 6 символов", "error")
                return redirect(url_for("main.profile"))
            current_user.set_password(new_password)
            flash("Пароль успешно изменен", "success")
        db.session.commit()
        flash("Данные успешно обновлены", "success")
        return redirect(url_for("main.profile"))
    return render_template("profile.html")


@main.route("/update_expired_products")
def update_expired_products():
    expired_products = Product.query.filter(
        Product.status == Product.STATUS_PUBLISHED,
        Product.expires_at < datetime.utcnow(),
    ).all()
    updated_count = 0
    for product in expired_products:
        if product.update_status():
            updated_count += 1
    if updated_count > 0:
        db.session.commit()
    return f"Обновлено {updated_count} товаров с истекшим сроком публикации"


@main.route("/dashboard/messages")
@main.route("/dashboard/messages/<int:recipient_id>")
@main.route("/dashboard/messages/<int:recipient_id>/<int:product_id>")
@login_required
def messages(recipient_id=None, product_id=None):
    """Messages page in WhatsApp style"""
    # Если переданы параметры, создаем новое сообщение или переходим к существующему диалогу
    if recipient_id and product_id:
        recipient = User.query.get(recipient_id)
        product = Product.query.get(product_id)
        
        if not recipient or not product:
            flash("Пользователь или товар не найден", "error")
            return redirect(url_for("main.messages"))
        
        if recipient_id == current_user.id:
            flash("Нельзя отправить сообщение себе", "error")
            return redirect(url_for("main.messages"))
        
        # Проверяем, есть ли уже сообщения между этими пользователями по этому товару
        existing_conversation = Message.query.filter(
            ((Message.sender_id == current_user.id) & (Message.recipient_id == recipient_id) |
             (Message.sender_id == recipient_id) & (Message.recipient_id == current_user.id)),
            Message.product_id == product_id
        ).first()
        
        if not existing_conversation:
            # Создаем приветственное сообщение
            welcome_message = Message(
                sender_id=current_user.id,
                recipient_id=recipient_id,
                subject=f"Вопрос по товару: {product.title}",
                body=f"Здравствуйте! У меня есть вопрос по товару \"{product.title}\".",
                product_id=product_id
            )
            db.session.add(welcome_message)
            db.session.commit()
            flash("Диалог создан. Теперь вы можете отправить сообщение.", "success")
    
    return render_template("messages.html", recipient_id=recipient_id, product_id=product_id)


@main.route("/messages/unread-count")
@login_required
def unread_count():
    """Get count of unread messages for current user"""
    unread_count = Message.query.filter_by(
        recipient_id=current_user.id, 
        is_read=False, 
        is_deleted_by_recipient=False
    ).count()
    return jsonify({"count": unread_count})


@main.route("/messages/send", methods=["POST"])
@login_required
def send_message():
    """Send a new message via AJAX"""
    try:
        data = request.get_json()
        recipient_id = int(data.get('recipient_id', 0))
        product_id = data.get('product_id')
        message_body = data.get('message')
        
        if not all([recipient_id, message_body]):
            return jsonify({"success": False, "error": "Missing required fields"}), 400
        
        recipient = User.query.get(recipient_id)
        
        if not recipient:
            return jsonify({"success": False, "error": "Invalid recipient"}), 400
        
        if recipient_id == current_user.id:
            return jsonify({"success": False, "error": "Cannot send message to yourself"}), 400
        
        # Обрабатываем product_id (может быть 0 или None для сообщений без товара)
        product = None
        if product_id and str(product_id) != '0':
            product_id = int(product_id)
            product = Product.query.get(product_id)
            if not product:
                return jsonify({"success": False, "error": "Invalid product"}), 400
        else:
            product_id = None
        
        # Создаем новое сообщение
        new_message = Message(
            sender_id=current_user.id,
            recipient_id=recipient_id,
            subject=f"Вопрос по товару: {product.title}" if product else "Личное сообщение",
            body=message_body,
            product_id=product_id
        )
        
        db.session.add(new_message)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": {
                "id": new_message.id,
                "body": new_message.body,
                "created_at": new_message.created_at_formatted,
                "sender": current_user.username or current_user.email.split('@')[0]
            }
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@main.route("/messages/send-file", methods=["POST"])
@login_required
def send_message_file():
    try:
        recipient_id = int(request.form.get("recipient_id", 0))
        product_id = request.form.get("product_id")
        uploaded_file = request.files.get("file")

        if not recipient_id or not uploaded_file or not uploaded_file.filename:
            return jsonify({"success": False, "error": "Missing required fields"}), 400

        recipient = User.query.get(recipient_id)
        if not recipient:
            return jsonify({"success": False, "error": "Invalid recipient"}), 400

        if recipient_id == current_user.id:
            return jsonify({"success": False, "error": "Cannot send message to yourself"}), 400

        product = None
        if product_id and str(product_id) != "0":
            product_id = int(product_id)
            product = Product.query.get(product_id)
            if not product:
                return jsonify({"success": False, "error": "Invalid product"}), 400
        else:
            product_id = None

        filename = secure_filename(uploaded_file.filename)
        if "." not in filename:
            return jsonify({"success": False, "error": "Invalid file"}), 400

        ext = filename.rsplit(".", 1)[1].lower()
        allowed_exts = current_app.config.get("MESSAGE_ALLOWED_EXTENSIONS") or set()
        if ext not in allowed_exts:
            return jsonify({"success": False, "error": "File type not allowed"}), 400

        upload_root = current_app.config.get("UPLOAD_FOLDER")
        if not upload_root:
            return jsonify({"success": False, "error": "Upload folder is not configured"}), 500

        messages_folder = os.path.join(upload_root, "messages")
        os.makedirs(messages_folder, exist_ok=True)

        stored_filename = f"{uuid.uuid4().hex}.{ext}"
        stored_abs_path = os.path.join(messages_folder, stored_filename)
        uploaded_file.save(stored_abs_path)

        try:
            attachment_size = os.path.getsize(stored_abs_path)
        except Exception:
            attachment_size = None

        attachment_rel_path = f"messages/{stored_filename}"
        attachment_url = url_for("static", filename=f"uploads/{attachment_rel_path}")

        new_message = Message(
            sender_id=current_user.id,
            recipient_id=recipient_id,
            subject=f"Вопрос по товару: {product.title}" if product else "Личное сообщение",
            body=filename,
            product_id=product_id,
            attachment_filename=attachment_rel_path,
            attachment_original_name=uploaded_file.filename,
            attachment_mime=uploaded_file.mimetype,
            attachment_size=attachment_size,
        )

        db.session.add(new_message)
        db.session.commit()

        return jsonify(
            {
                "success": True,
                "message": {
                    "id": new_message.id,
                    "body": new_message.body,
                    "created_at": new_message.created_at_formatted,
                    "sender": current_user.username or current_user.email.split("@")[0],
                    "attachment_url": attachment_url,
                    "attachment_original_name": new_message.attachment_original_name,
                    "attachment_mime": new_message.attachment_mime,
                    "attachment_size": new_message.attachment_size,
                },
            }
        )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@main.route("/api/user/<int:user_id>")
def get_user_info(user_id):
    """Get user information for messages"""
    user = User.query.get_or_404(user_id)
    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "company_name": user.company_name
    })


@main.route("/api/product/<int:product_id>")
def get_product_info(product_id):
    """Get product information for messages"""
    product = Product.query.get_or_404(product_id)
    return jsonify({
        "id": product.id,
        "title": product.title,
        "price": product.price
    })


@main.route("/api/conversations")
@login_required
def get_conversations():
    """Get user's conversations"""
    print(f"API: Загрузка диалогов для пользователя {current_user.id}")
    
    # Временно упрощаем запрос - ищем все сообщения пользователя
    messages = Message.query.filter(
        (Message.sender_id == current_user.id) | (Message.recipient_id == current_user.id)
    ).order_by(Message.created_at.desc()).all()
    
    print(f"API: Найдено сообщений: {len(messages)}")
    
    # Группируем сообщения по диалогам (пользователь + товар)
    conversations = {}
    for message in messages:
        print(f"API: Сообщение {message.id} - от {message.sender_id} к {message.recipient_id}")
        
        # Определяем собеседника
        other_user_id = message.recipient_id if message.sender_id == current_user.id else message.sender_id
        other_user = User.query.get(other_user_id)
        
        if not other_user:
            continue
            
        # Создаем ключ диалога
        dialog_key = f"{other_user_id}_{message.product_id or 0}"
        
        if dialog_key not in conversations:
            conversations[dialog_key] = {
                'user_id': other_user_id,
                'username': other_user.username or other_user.company_name or other_user.email.split('@')[0],
                'product_id': message.product_id,
                'product_title': message.product.title if message.product else None,
                'last_message': message.body,
                'last_time': message.created_at_formatted,
                'unread_count': 0
            }
        
        # Считаем непрочитанные сообщения
        if message.recipient_id == current_user.id and not message.is_read:
            conversations[dialog_key]['unread_count'] += 1
    
    print(f"API: Создано диалогов: {len(conversations)}")
    return jsonify(list(conversations.values()))


@main.route("/api/messages/<int:user_id>")
@main.route("/api/messages/<int:user_id>/<int:product_id>")
@login_required
def get_messages(user_id, product_id=None):
    """Get messages for a specific conversation"""
    # Проверяем, что пользователь участвует в диалоге
    if user_id != current_user.id:
        # Проверяем, есть ли сообщения между этими пользователями
        has_conversation = Message.query.filter(
            ((Message.sender_id == current_user.id) & (Message.recipient_id == user_id)) |
            ((Message.sender_id == user_id) & (Message.recipient_id == current_user.id))
        ).first()
        
        if not has_conversation:
            return jsonify({"error": "Conversation not found"}), 404
    
    # Получаем сообщения
    query = Message.query.filter(
        ((Message.sender_id == current_user.id) & (Message.recipient_id == user_id)) |
        ((Message.sender_id == user_id) & (Message.recipient_id == current_user.id))
    )
    
    if product_id:
        query = query.filter(Message.product_id == product_id)
    
    messages = query.order_by(Message.created_at.asc()).all()
    
    # Отмечаем сообщения как прочитанные
    unread_messages = Message.query.filter(
        Message.recipient_id == current_user.id,
        Message.sender_id == user_id,
        Message.is_read == False
    )
    
    if product_id:
        unread_messages = unread_messages.filter(Message.product_id == product_id)
    
    for message in unread_messages:
        message.is_read = True
    
    db.session.commit()
    
    # Форматируем сообщения
    result = []
    for message in messages:
        attachment_url = None
        if getattr(message, "attachment_filename", None):
            attachment_url = url_for("static", filename=f"uploads/{message.attachment_filename}")
        result.append({
            'id': message.id,
            'body': message.body,
            'created_at': message.created_at_formatted,
            'sender_id': message.sender_id,
            'is_sent': message.sender_id == current_user.id,
            'sender_name': message.sender.username or message.sender.email.split('@')[0],
            'attachment_url': attachment_url,
            'attachment_original_name': getattr(message, 'attachment_original_name', None),
            'attachment_mime': getattr(message, 'attachment_mime', None),
            'attachment_size': getattr(message, 'attachment_size', None)
        })
    
    return jsonify(result)


# Redirect old messages URL to new dashboard/messages
@main.route("/messages/<int:user_id>/<int:product_id>")
@login_required
def old_messages_redirect(user_id, product_id):
    """Redirect old message links to new messages page"""
    flash("Система сообщений обновлена. Теперь все сообщения в личном кабинете", "info")
    return redirect(url_for("main.messages"))


# Redirect old /profile to /dashboard/profile
@main.route("/profile")
@login_required
def old_profile_redirect():
    """Redirect old profile URL to new dashboard/profile"""
    return redirect(url_for("main.profile"), code=301)


# Redirect old /favorites to /dashboard/favorites
@main.route("/favorites")
@login_required
def old_favorites_redirect():
    """Redirect old favorites URL to new dashboard/favorites"""
    return redirect(url_for("main.favorites"), code=301)


@main.route("/product/<int:product_id>/report", methods=["POST"])
@login_required
def report_product(product_id):
    product = Product.query.get_or_404(product_id)
    reason = request.form.get("reason")
    if reason:
        flash("Жалоба отправлена. Спасибо за участие!", "success")
    else:
        flash("Выберите причину жалобы", "error")
    return redirect(url_for("main.product_detail", product_id=product_id))


@main.route("/dashboard/favorites")
@login_required
def favorites():
    """User's favorite products page"""
    favorite_products = current_user.favorited_products.all()
    return render_template("favorites.html", products=favorite_products)


@main.route("/favorites/toggle/<int:product_id>", methods=["POST"])
@login_required
def toggle_favorite(product_id):
    """Toggle product in user's favorites"""
    product = Product.query.get_or_404(product_id)

    # Check if already in favorites
    is_favorite = product in current_user.favorited_products

    if is_favorite:
        # Remove from favorites
        current_user.favorited_products.remove(product)
        message = "Товар удален из избранного"
    else:
        # Add to favorites
        current_user.favorited_products.append(product)
        message = "Товар добавлен в избранное"

    try:
        db.session.commit()
        return jsonify(
            {"success": True, "is_favorite": not is_favorite, "message": message}
        )
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"Ошибка: {str(e)}"}), 500


@main.route("/user/<int:user_id>/reviews")
def user_reviews(user_id):
    user = User.query.get_or_404(user_id)
    reviews = (
        Review.query.filter(Review.seller_id == user_id, Review.is_published == True)
        .order_by(Review.created_at.desc())
        .all()
    )
    total_reviews = len(reviews)
    if total_reviews > 0:
        average_rating = sum(r.rating for r in reviews) / total_reviews
        average_rating = round(average_rating, 1)
        rating_distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for review in reviews:
            rating_distribution[review.rating] += 1
    else:
        average_rating = 0
        rating_distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    return render_template(
        "user_reviews.html",
        user=user,
        reviews=reviews,
        total_reviews=total_reviews,
        average_rating=average_rating,
        rating_distribution=rating_distribution,
    )


@main.route("/product/<int:product_id>/add_review", methods=["GET", "POST"])
@login_required
def add_review(product_id):
    product = Product.query.get_or_404(product_id)
    if current_user.id == product.user_id:
        flash("Вы не можете оставить отзыв на свой товар", "error")
        return redirect(request.referrer or url_for("main.index"))
    existing_review = Review.query.filter_by(
        seller_id=product.user_id, buyer_id=current_user.id, product_id=product_id
    ).first()
    if existing_review:
        flash("Вы уже оставляли отзыв на этот товар", "error")
        return redirect(url_for("main.product_detail", product_id=product_id))
    form = ReviewForm()
    if form.validate_on_submit():
        try:
            review = Review(
                seller_id=product.user_id,
                buyer_id=current_user.id,
                product_id=product_id,
                rating=form.rating.data,
                text=form.text.data,
            )
            db.session.add(review)
            db.session.commit()
            flash(
                "Спасибо за ваш отзыв! Он будет опубликован после проверки.", "success"
            )
            return redirect(url_for("main.product_detail", product_id=product_id))
        except Exception as e:
            db.session.rollback()
            flash(f"Ошибка при сохранении отзыва: {str(e)}", "error")
    return render_template("add_review.html", form=form, product=product)


@main.route("/user/<int:user_id>/add_review_direct", methods=["GET", "POST"])
@login_required
def add_review_direct(user_id):
    seller = User.query.get_or_404(user_id)
    if current_user.id == seller.id:
        flash("Вы не можете оставить отзыв самому себе", "error")
        return redirect(url_for("main.user_reviews", user_id=user_id))
    form = ReviewForm()
    if form.validate_on_submit():
        try:
            review = Review(
                seller_id=seller.id,
                buyer_id=current_user.id,
                rating=form.rating.data,
                text=form.text.data,
            )
            db.session.add(review)
            db.session.commit()
            flash(
                "Спасибо за ваш отзыв! Он будет опубликован после проверки.", "success"
            )
            return redirect(
                request.referrer or url_for("main.product_detail", product_id=...)
            )
        except Exception as e:
            db.session.rollback()
            flash(f"Ошибка при сохранении отзыва: {str(e)}", "error")
    return render_template("add_review_direct.html", form=form, seller=seller)


@main.route("/user/<int:user_id>/profile")
def user_profile_modal(user_id):
    user = User.query.get_or_404(user_id)
    return render_template("partials/user_profile_modal.html", user=user)


@main.route("/user/<int:user_id>/reviews_content")
def user_reviews_content(user_id):
    from app.models import Review, User

    user = User.query.get_or_404(user_id)
    reviews = (
        Review.query.filter(Review.seller_id == user.id, Review.is_published == True)
        .order_by(Review.created_at.desc())
        .all()
    )
    return render_template(
        "partials/user_reviews_content.html", user=user, reviews=reviews
    )


@main.route("/user/<int:user_id>/review_form")
def review_form(user_id):
    from app.forms import ReviewForm
    from app.models import Review, User

    seller = User.query.get_or_404(user_id)
    if current_user.is_authenticated:
        existing_review = Review.query.filter_by(
            seller_id=seller.id, buyer_id=current_user.id
        ).first()
        if existing_review:
            return '<div class="p-3 text-center"><p class="text-muted">Вы уже оставили отзыв этому пользователю.</p><button class="btn btn-sm btn-secondary" onclick="closeReviewFormModal()">Закрыть</button></div>'
    form = ReviewForm()
    return render_template("partials/review_form.html", seller=seller, form=form)


@main.route("/review/<int:review_id>/delete", methods=["POST"])
@login_required
def delete_review(review_id):
    from app.models import Review

    review = Review.query.get_or_404(review_id)
    if review.buyer_id != current_user.id:
        flash("Вы не можете удалить чужой отзыв.", "danger")
        return redirect(request.referrer or url_for("main.index"))
    db.session.delete(review)
    db.session.commit()
    flash("Ваш отзыв удалён.", "success")
    return redirect(request.referrer or url_for("main.index"))


@main.route("/upload_category_image", methods=["POST"])
@login_required
def upload_category_image():
    """Загрузка изображения для категории"""
    if "category_image" not in request.files:
        return jsonify({"error": "No file selected"}), 400

    category_id = request.form.get("category_id")
    if not category_id:
        return jsonify({"error": "Category ID is required"}), 400

    file = request.files["category_image"]

    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    # Обрабатываем изображение
    filename, error = process_category_image(file, category_id)

    if error:
        return jsonify({"error": error}), 400

    # Обновляем категорию в базе
    category = Category.query.get(int(category_id))
    if category:
        # Удаляем старое изображение если есть
        if category.image:
            try:
                # Удаляем все размеры
                base_filename = category.image.rsplit(".", 1)[0]
                ext = (
                    category.image.rsplit(".", 1)[1] if "." in category.image else "jpg"
                )

                sizes = ["thumbnail", "small", "medium", "large", "original"]
                for size in sizes:
                    if size == "thumbnail":
                        old_filename = category.image
                    else:
                        old_filename = f"{base_filename}_{size}.{ext}"

                    old_path = os.path.join(
                        current_app.config["UPLOAD_FOLDER"], "categories", old_filename
                    )
                    if os.path.exists(old_path):
                        os.remove(old_path)
            except Exception as e:
                print(f"Error deleting old image: {e}")

        category.image = filename
        db.session.commit()

        return jsonify(
            {
                "success": True,
                "image_url": url_for(
                    "main.get_category_image_by_size",
                    category_id=category_id,
                    size="thumbnail",
                ),
                "filename": filename,
            }
        )

    return jsonify({"error": "Category not found"}), 404


@main.route("/category/<int:category_id>/image/<size>")
def get_category_image_by_size(category_id, size="thumbnail"):
    """Возвращает изображение категории нужного размера"""
    category = Category.query.get_or_404(category_id)

    if not category.image:
        # Возвращаем дефолтное изображение
        return send_from_directory(
            os.path.join(current_app.root_path, "static", "images"), "no-image.png"
        )

    # Определяем имя файла нужного размера
    base_filename = category.image.rsplit(".", 1)[0]
    ext = category.image.rsplit(".", 1)[1] if "." in category.image else "jpg"

    # Поддерживаемые размеры
    valid_sizes = ["thumbnail", "small", "medium", "large", "original"]
    if size not in valid_sizes:
        size = "thumbnail"

    # Формируем имя файла
    if size == "thumbnail":
        filename = category.image  # thumbnail - основное имя
    else:
        filename = f"{base_filename}_{size}.{ext}"

    # Проверяем существует ли файл
    filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], "categories", filename)

    if not os.path.exists(filepath):
        # Если файла нужного размера нет, пробуем вернуть оригинал (thumbnail)
        filename = category.image
        filepath = os.path.join(
            current_app.config["UPLOAD_FOLDER"], "categories", filename
        )

        # Если и оригинала нет, возвращаем заглушку
        if not os.path.exists(filepath):
            return send_from_directory(
                os.path.join(current_app.root_path, "static", "images"), "no-image.png"
            )

    return send_from_directory(
        os.path.join(current_app.config["UPLOAD_FOLDER"], "categories"), filename
    )


@main.route("/api/categories/children/<int:parent_id>")
def get_child_categories(parent_id):
    children = (
        Category.query.filter_by(parent_id=parent_id).order_by(Category.name).all()
    )
    return jsonify(
        [
            {"id": c.id, "name": c.name, "has_children": bool(c.children)}
            for c in children
        ]
    )


# Старая функция для обратной совместимости - перенаправляет на новую
@main.route("/category_image/<filename>")
def category_image(filename):
    """Отдача изображений категорий (для обратной совместимости)"""
    return send_from_directory(
        os.path.join(current_app.config["UPLOAD_FOLDER"], "categories"), filename
    )


@main.route("/contact_captcha")
def contact_captcha():
    from app.utils import generate_captcha_image

    code, image_io = generate_captcha_image()
    session["contact_captcha"] = code
    return send_file(image_io, mimetype="image/png")


@main.route("/contact", methods=["POST"])
def contact():
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "No data provided"}), 400

    contact_info = data.get("contact_info")
    category = data.get("category")
    message = data.get("message")
    captcha_input = data.get("captcha")
    captcha_session = session.get("contact_captcha")

    # Clear captcha
    session.pop("contact_captcha", None)

    if not captcha_input or captcha_input != captcha_session:
        return jsonify({"success": False, "message": "Неверный код с картинки"}), 400

    if not contact_info or not message:
        return jsonify(
            {"success": False, "message": "Заполните обязательные поля"}
        ), 400

    try:
        from app.models import ContactRequest

        new_request = ContactRequest(
            contact_info=contact_info, category=category, message=message
        )
        db.session.add(new_request)
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
