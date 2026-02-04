"""
Генератор тестовых объявлений для системы продажи товаров B2B
Создает реалистичные объявления с фотографиями из Google Custom Search
"""
import os
import random
import requests
from datetime import datetime, timedelta
from app import create_app, db
from app.models import Product, Category, User, Region
import uuid
import time

# Конфигурация
MIN_PRODUCTS = 10
MAX_PRODUCTS = 200000
OWNER_USER_ID = 1

# Google Custom Search API
API_KEY = "AIzaSyAJAgCovRWVPw9ycVCGzKtT1CVj2go2_Q8"
SEARCH_ENGINE_ID = "b499bf2caa97b49b7"

# Конкретные примеры товаров
SPECIFIC_PRODUCTS = {
    "Электрооборудование": [
        "Щит распределительный навесной ЩРн-П-6 IP41",
        "Трансформатор ТМГ-1000/10/0.4",
        "Автоматический выключатель ВА47-29 3P 25А",
        "Кабель ВВГнг-LS 3х2.5 мм²",
        "Светильник LED ДПП 01-135-50-Д120",
        "Контактор КМИ-23210 32А 230В",
        "Реле времени РВО-П2-15 220В",
        "УЗО ВД1-63 2P 40А 30мА",
    ],
    "Трубопроводная арматура": [
        "Задвижка клиновая 30с41нж Ду100 Ру16",
        "Кран шаровой фланцевый КШФР Ду50 Ру40",
        "Затвор дисковый поворотный Ду200 Ру16",
        "Клапан обратный 16ч6р Ду80",
    ],
    "Метизы и крепеж": [
        "Болт М16х60 ГОСТ 7798-70 оцинкованный",
        "Гайка М12 DIN 934 класс прочности 8",
        "Шайба 20 ГОСТ 11371-78 увеличенная",
        "Шпилька М20х120 ГОСТ 22032-76",
    ],
    "Насосное оборудование": [
        "Насос центробежный К 65-50-160",
        "Насос погружной ЭЦВ 6-10-110",
        "Насосная станция Grundfos Hydro MPC-E 2 CR15-2",
        "Насос вихревой ВК 1/16 0.37кВт",
    ],
    "Подшипники": [
        "Подшипник 6205-2RS (25х52х15)",
        "Подшипник роликовый 32210 (50х90х23)",
        "Подшипник шариковый 180204 (20х47х14)",
    ],
    "Инструмент": [
        "Дрель ударная Makita HP1631K 710Вт",
        "Болгарка Bosch GWS 750-125 750Вт",
        "Перфоратор DeWalt D25133K 800Вт SDS-plus",
        "Компрессор CA2180324 8 атм 24л",
    ],
    "Спецтехника": [
        "Погрузчик SEM 655D 2017г.в.",
        "Экскаватор Hyundai R220LC-9S 2019г.в.",
        "Автокран Галичанин КС-55713-1 25т",
    ],
}

COMPANY_NAMES = [
    'ООО "СтройТехСнаб"', 'АО "ПромКомплект"', 'ООО "ИндустриТорг"',
    'ЗАО "ТехноСнаб"', 'ООО "МетизПром"', 'АО "ЭлектроКомплект"',
]

CONDITIONS = ["new", "used"]
CONDITION_DESCRIPTIONS = {
    "new": ["Новое", "С хранения", "Не использовалось"],
    "used": ["Б/У", "Рабочее состояние", "После эксплуатации"],
}

PRICE_TYPES = ["fixed", "negotiable"]


def generate_product_name(category):
    """Генерирует название товара"""
    for cat_key in SPECIFIC_PRODUCTS:
        if cat_key.lower() in category.lower():
            return random.choice(SPECIFIC_PRODUCTS[cat_key])
    
    all_products = []
    for products_list in SPECIFIC_PRODUCTS.values():
        all_products.extend(products_list)
    return random.choice(all_products)


def generate_description(product_name, condition):
    """Генерирует описание товара"""
    condition_desc = random.choice(CONDITION_DESCRIPTIONS[condition])
    descriptions = [
        f"Состояние: {condition_desc}\\n\\nПредлагаем к реализации {product_name.lower()}. Товар соответствует всем требованиям ГОСТ.",
        f"Состояние: {condition_desc}\\n\\nВ наличии {product_name.lower()}. Возможна отгрузка со склада в течение 3 рабочих дней.",
        f"Состояние: {condition_desc}\\n\\nРеализуем {product_name.lower()}. Вся продукция сертифицирована.",
    ]
    return random.choice(descriptions)


def download_product_image(product_name, upload_dir):
    """Скачивает изображение товара через Google Custom Search API"""
    try:
        search_query = f'"{product_name}" купить цена фото'
        
        params = {
            'q': search_query,
            'cx': SEARCH_ENGINE_ID,
            'key': API_KEY,
            'searchType': 'image',
            'num': 1,
            'imgSize': 'large',
            'imgType': 'photo',
            'safe': 'active',
            'hl': 'ru',
            'gl': 'ru'
        }
        
        response = requests.get(
            'https://www.googleapis.com/customsearch/v1',
            params=params,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if 'items' in data and len(data['items']) > 0:
                image_url = data['items'][0]['link']
                
                img_response = requests.get(image_url, timeout=15)
                
                if img_response.status_code == 200 and len(img_response.content) > 1000:
                    filename = f"{uuid.uuid4().hex}.jpg"
                    filepath = os.path.join(upload_dir, filename)
                    
                    with open(filepath, 'wb') as f:
                        f.write(img_response.content)
                    
                    print(f"  ✅ {product_name[:50]}")
                    time.sleep(0.5)  # Задержка между запросами
                    return filename
                else:
                    print(f"  ⚠️ Не удалось скачать: {product_name[:50]}")
            else:
                print(f"  ⚠️ Не найдено: {product_name[:50]}")
        else:
            print(f"  ❌ API error {response.status_code}")
            
    except Exception as e:
        print(f"  ❌ Ошибка: {str(e)[:50]}")
    
    return None


def generate_products(count):
    """Генерирует указанное количество товаров"""
    app = create_app()
    
    with app.app_context():
        owner = db.session.get(User, OWNER_USER_ID)
        if not owner:
            print(f"Пользователь с ID {OWNER_USER_ID} не найден!")
            return
        
        categories = Category.query.all()
        if not categories:
            print("Категории не найдены!")
            return
        
        regions = Region.query.filter_by(parent_id=None).all()
        upload_dir = app.config.get('UPLOAD_FOLDER', 'app/static/uploads')
        
        print(f"Начинаем генерацию {count} товаров...")
        print(f"⚠️ Лимит Google API: 100 запросов/день")
        
        created_count = 0
        
        for i in range(count):
            try:
                category = random.choice(categories)
                product_name = generate_product_name(category.name)
                condition = random.choice(CONDITIONS)
                description = generate_description(product_name, condition)
                
                price_type = random.choice(PRICE_TYPES)
                price = 0.0 if price_type == "negotiable" else round(random.uniform(100, 500000), 2)
                quantity = random.randint(1, 1000)
                vat_included = random.choice([True, False])
                region = random.choice(regions) if regions else None
                days_ago = random.randint(1, 365)
                created_at = datetime.now() - timedelta(days=days_ago)
                view_count = random.randint(0, 500)
                company = random.choice(COMPANY_NAMES)
                
                # Загружаем изображение
                images = []
                image_filename = download_product_image(product_name, upload_dir)
                if image_filename:
                    images.append(image_filename)
                
                product = Product(
                    title=product_name,
                    description=description,
                    price=price,
                    price_type=price_type,
                    quantity=quantity,
                    category_id=category.id,
                    user_id=owner.id,
                    images=images,
                    status=Product.STATUS_PUBLISHED,
                    condition=condition,
                    region=region.name if region else None,
                    region_id=region.id if region else None,
                    view_count=view_count,
                    vat_included=vat_included,
                    created_at=created_at,
                    external_organization=company,
                    external_phone="+X XXX XXX-XX-XX",
                )
                
                db.session.add(product)
                created_count += 1
                
                if created_count % 10 == 0:
                    db.session.commit()
                    print(f"Создано {created_count} товаров...")
            
            except Exception as e:
                print(f"Ошибка при создании товара {i+1}: {e}")
                db.session.rollback()
        
        try:
            db.session.commit()
            print(f"\\n✓ Успешно создано {created_count} товаров!")
        except Exception as e:
            print(f"Ошибка при финальном сохранении: {e}")
            db.session.rollback()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        try:
            count = int(sys.argv[1])
            if count < MIN_PRODUCTS or count > MAX_PRODUCTS:
                print(f"Количество должно быть от {MIN_PRODUCTS} до {MAX_PRODUCTS}")
                sys.exit(1)
        except ValueError:
            print("Укажите корректное число")
            sys.exit(1)
    else:
        count = int(input(f"Сколько товаров создать ({MIN_PRODUCTS}-{MAX_PRODUCTS})? "))
        if count < MIN_PRODUCTS or count > MAX_PRODUCTS:
            print(f"Количество должно быть от {MIN_PRODUCTS} до {MAX_PRODUCTS}")
            sys.exit(1)
    
    generate_products(count)
