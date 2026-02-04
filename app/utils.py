import uuid
import random
import io
import os
from flask import current_app
from werkzeug.utils import secure_filename
from PIL import Image, ImageDraw, ImageFont

def generate_captcha_image():
    """Generates a secure numeric captcha image with rotation and noise."""
    # Generate 4 random digits
    code = str(random.randint(1000, 9999))
    
    # Image dimensions
    width, height = 180, 60  # Increased size slightly
    # Create white background
    image = Image.new('RGB', (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(image)
    
    # Load font (try various system fonts or fallback)
    try:
        font = ImageFont.truetype("arial.ttf", 40) # Increased font size
    except IOError:
        try:
             font = ImageFont.truetype("segoeui.ttf", 40)
        except IOError:
            font = ImageFont.load_default()
    
    # Draw each character with random rotation
    # Reduce char_width slightly or ensure total fits
    char_spacing = 40 # Increased spacing
    start_x = 10
    
    for i, char in enumerate(code):
        # Create a separate image for the character to rotate it
        # Make it larger than needed to avoid clipping during rotation
        txt_img = Image.new('RGBA', (50, 50), (255, 255, 255, 0))
        txt_draw = ImageDraw.Draw(txt_img)
        
        # Draw text centered in the small image
        txt_draw.text((10, 5), char, font=font, fill=(0, 0, 0, 255))
        
        # Rotate randomly between -10 and 10 degrees (Reduced rotation)
        angle = random.randint(-10, 10)
        rotated_txt = txt_img.rotate(angle, expand=1, resample=Image.BICUBIC)
        
        # Calculate position to paste
        jitter_x = random.randint(-2, 2)
        jitter_y = random.randint(-2, 2)
        
        paste_x = start_x + (i * char_spacing) + jitter_x
        paste_y = 5 + jitter_y
        
        image.paste(rotated_txt, (paste_x, paste_y), rotated_txt)

    # Add noise: lines (Reduced noise)
    for _ in range(5):
        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        x2 = random.randint(0, width)
        y2 = random.randint(0, height)
        color = (random.randint(50, 200), random.randint(50, 200), random.randint(50, 200))
        draw.line((x1, y1, x2, y2), fill=color, width=1)
        
    # Add noise: points (Reduced noise)
    for _ in range(50):
        x = random.randint(0, width)
        y = random.randint(0, height)
        color = (random.randint(100, 200), random.randint(100, 200), random.randint(100, 200))
        draw.point((x, y), fill=color)

    # Return code and image bytes
    byte_io = io.BytesIO()
    image.save(byte_io, 'PNG')
    byte_io.seek(0)
    return code, byte_io


from flask import current_app, request
from app import db
from app.models import AnalyticsEvent

def track_event(event_type, user=None, resource_id=None, url_path=None):
    """
    Записывает событие аналитики в базу данных.
    """
    try:
        # Пытаемся получить IP
        if request.headers.getlist("X-Forwarded-For"):
            ip = request.headers.getlist("X-Forwarded-For")[0]
        else:
            ip = request.remote_addr
            
        user_id = user.id if user and user.is_authenticated else None
        
        # Обрезаем URL если слишком длинный
        if url_path and len(url_path) > 250:
            url_path = url_path[:250]
            
        event = AnalyticsEvent(
            event_type=event_type,
            user_id=user_id,
            fingerprint=ip,
            resource_id=resource_id,
            url_path=url_path
        )
        db.session.add(event)
        # Commit делаем сразу, чтобы статистика была realtime
        db.session.commit()
    except Exception as e:
        # Аналитика не должна ломать основное приложение
        print(f"Analytics Error: {e}")
        db.session.rollback()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def _deserialize_images(images_field):
    """Преобразует значение поля images (строка или список) в список имён файлов."""
    if not images_field:
        return []
    if isinstance(images_field, list):
        return [img for img in images_field if img]
    if isinstance(images_field, str):
        return [img.strip() for img in images_field.split(',') if img.strip()]
    return []

def _serialize_images(images_list):
    """Преобразует список имён файлов в строку для хранения в БД."""
    return ','.join(images_list) if images_list else ''

def process_category_image(file, category_id=None):
    """Обрабатывает и сохраняет изображение категории с обрезкой"""
    if file and allowed_file(file.filename):
        try:
            # Открываем изображение
            img = Image.open(file)
            
            # Конвертируем в RGB если нужно
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            
            # Определяем размеры
            width, height = img.size
            
            # Если изображение очень большое, уменьшаем перед обрезкой
            max_dimension = 800
            if width > max_dimension or height > max_dimension:
                if width > height:
                    new_width = max_dimension
                    new_height = int(height * (max_dimension / width))
                else:
                    new_height = max_dimension
                    new_width = int(width * (max_dimension / height))
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                width, height = img.size
            
            # Обрезаем до квадрата (центрированно)
            target_size = min(width, height)
            
            # Координаты для обрезки
            left = (width - target_size) // 2
            top = (height - target_size) // 2
            right = left + target_size
            bottom = top + target_size
            
            img_cropped = img.crop((left, top, right, bottom))
            
            # Создаем несколько размеров
            sizes = {
                'original': (target_size, target_size),  # Оригинальный квадрат
                'large': (200, 200),  # Для десктопа
                'medium': (150, 150), # Для планшетов
                'small': (100, 100),  # Для мобильных
                'thumbnail': (80, 80)  # Для превью (как в блоке категорий)
            }
            
            # Генерируем уникальное имя файла
            unique_filename = str(uuid.uuid4())
            original_filename = secure_filename(file.filename)
            ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else 'jpg'
            
            base_filename = f"{unique_filename}_{original_filename.split('.')[0]}"
            
            # Сохраняем все размеры
            saved_filenames = {}
            
            for size_name, (size_width, size_height) in sizes.items():
                # Ресайзим
                img_resized = img_cropped.resize((size_width, size_height), Image.Resampling.LANCZOS)
                
                # Формируем имя файла
                if size_name == 'thumbnail':
                    filename = f"{base_filename}.{ext}"  # Основное имя для thumbnail
                else:
                    filename = f"{base_filename}_{size_name}.{ext}"
                
                # Путь для сохранения
                upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'categories')
                os.makedirs(upload_folder, exist_ok=True)
                
                filepath = os.path.join(upload_folder, filename)
                
                # Сохраняем с оптимизацией
                if ext in ['jpg', 'jpeg']:
                    img_resized.save(filepath, 'JPEG', quality=85, optimize=True)
                elif ext == 'png':
                    img_resized.save(filepath, 'PNG', optimize=True)
                else:
                    img_resized.save(filepath)
                
                saved_filenames[size_name] = filename
            
            # Возвращаем имя thumbnail-файла (основное)
            return saved_filenames['thumbnail'], None
            
        except Exception as e:
            print(f"Error processing category image: {e}")
            return None, str(e)
    
    return None, "Invalid file format"

def save_uploaded_files(files):
    saved_files = []
    print(f"  🔍 save_uploaded_files: начало, файлов: {len(files)}")
    
    upload_folder = current_app.config['UPLOAD_FOLDER']
    print(f"  🔍 Абсолютный путь для сохранения: '{upload_folder}'")
    print(f"  🔍 Текущая рабочая папка: '{os.getcwd()}'")
    
    # Создаем папку с проверкой
    try:
        os.makedirs(upload_folder, exist_ok=True)
        print(f"  ✅ Папка создана/проверена: {upload_folder}")
        print(f"  ✅ Папка существует: {os.path.exists(upload_folder)}")
    except Exception as e:
        print(f"  ❌ Ошибка создания папки: {e}")
        return []
    
    for i, file in enumerate(files):
        print(f"  🔍 Обработка файла {i}:")
        
        if file and file.filename:
            print(f"    📄 Имя файла: '{file.filename}'")
            
            if allowed_file(file.filename):
                ext = file.filename.rsplit('.', 1)[1].lower()
                filename = f"{uuid.uuid4().hex}.{ext}"
                file_path = os.path.join(upload_folder, filename)
                
                print(f"    📁 Сохраняем как: '{filename}'")
                print(f"    📁 Полный путь: '{file_path}'")
                
                try:
                    file.save(file_path)
                    
                    if os.path.exists(file_path):
                        file_size = os.path.getsize(file_path)
                        print(f"    ✅ Файл успешно сохранен! Размер: {file_size} байт")
                        saved_files.append(filename)
                        
                        # Проверим где реально сохранился файл
                        actual_path = os.path.abspath(file_path)
                        print(f"    📍 Реальный путь файла: '{actual_path}'")
                    else:
                        print(f"    ❌ Файл не сохранился!")
                        
                except Exception as e:
                    print(f"    ❌ Ошибка сохранения файла: {e}")
                    
            else:
                print(f"    ❌ Тип файла не разрешен: {file.filename}")
        else:
            print(f"    ❌ Файл {i} пустой или без имени")
    
    print(f"  🔍 save_uploaded_files: конец, сохранено: {saved_files}")
    return saved_files

def get_category_choices(parent_id=None, level=0):
    """
    Рекурсивно получает категории для выпадающего списка с учетом иерархии.
    Возвращает список словарей: {'id', 'name', 'level', 'display_name'}
    """
    from app.models import Category
    
    choices = []
    # Сортировка по алфавиту
    cats = Category.query.filter_by(parent_id=parent_id).order_by(Category.name).all()
    for cat in cats:
        choices.append({
            'id': cat.id,
            'name': cat.name,
            'level': level,
            'display_name': ('— ' * level) + cat.name
        })
        choices.extend(get_category_choices(cat.id, level + 1))
    return choices

def format_price(value):
    """Форматирует цену с пробелом в качестве разделителя тысяч."""
    if value is None:
        return ""
    try:
        # Приводим к float
        val = float(value)
        # Если целое число, то без дробной части, иначе с двумя знаками
        if val.is_integer():
             return "{:,.0f}".format(val).replace(",", " ")
        return "{:,.2f}".format(val).replace(",", " ").replace(".", ",")
    except (ValueError, TypeError):
        return str(value)

def format_product_price(product):
    """
    Форматирует цену товара с учетом типа цены (от, договорная).
    Возвращает готовую HTML строку или текст.
    """
    if product.price is None:
        return "Договорная"
    
    price_str = format_price(product.price)
    suffix = " ₽"
    prefix = ""
    
    if product.price_type == 'from':
        prefix = "от "
    
    return f"{prefix}{price_str}{suffix}"
