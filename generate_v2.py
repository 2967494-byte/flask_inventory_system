"""
Финальный генератор товаров v2.
- Реалистичные цены для каждой категории
- Генерация стабильных изображений через Lorem Picsum
- Умный подбор цен
"""
import random
import uuid
import os
import requests
from datetime import datetime, timedelta
from app import create_app, db
from app.models import Product, Category, User, Region

COUNT = 50
OWNER_USER_ID = 1

COMPANY_NAMES = [
    'ООО "СтройТехСнаб"', 'АО "ПромКомплект"', 'ООО "ИндустриТорг"',
    'ЗАО "ТехноСнаб"', 'ООО "МетизПром"', 'АО "ЭлектроКомплект"',
]

# Структура: Категория -> [(Название, Мин.цена, Макс.цена)]
PRODUCTS_DB = {
    "Электрооборудование": [
        ("Щит распределительный навесной ЩРн-П-6 IP41", 3000, 8000),
        ("Трансформатор ТМГ-1000/10/0.4", 400000, 650000),
        ("Автоматический выключатель ВА47-29 3P 25А", 150, 450),
        ("Кабель ВВГнг-LS 3х2.5 мм²", 80, 150),
        ("Светильник LED ДПП 01-135-50-Д120", 1500, 3500),
        ("Контактор КМИ-23210 32А 230В", 800, 1500),
    ],
    "Трубопроводная арматура": [
        ("Задвижка клиновая 30с41нж Ду100 Ру16", 15000, 25000),
        ("Кран шаровой фланцевый КШФР Ду50 Ру40", 3500, 6000),
        ("Затвор дисковый поворотный Ду200 Ру16", 8000, 14000),
        ("Клапан обратный 16ч6р Ду80", 2500, 4500),
    ],
    "Метизы и крепеж": [
        ("Болт М16х60 ГОСТ 7798-70 оцинкованный", 25, 80),
        ("Гайка М12 DIN 934 класс прочности 8", 5, 15),
        ("Шайба 20 ГОСТ 11371-78 увеличенная", 2, 8),
        ("Шпилька М20х120 ГОСТ 22032-76", 40, 120),
        ("Анкер клиновой 12х100", 35, 90),
    ],
    "Насосное оборудование": [
        ("Насос центробежный К 65-50-160", 45000, 75000),
        ("Насос погружной ЭЦВ 6-10-110", 35000, 60000),
        ("Насосная станция Grundfos Hydro MPC-E 2 CR15-2", 250000, 450000),
        ("Насос вихревой ВК 1/16 0.37кВт", 12000, 18000),
    ],
    "Подшипники": [
        ("Подшипник 6205-2RS (25х52х15)", 150, 400),
        ("Подшипник роликовый 32210 (50х90х23)", 800, 1500),
        ("Подшипник шариковый 180204 (20х47х14)", 200, 500),
    ],
    "Инструмент": [
        "Дрель ударная Makita HP1631K 710Вт", 4500, 7000),
        ("Болгарка Bosch GWS 750-125 750Вт", 5000, 8000),
        ("Перфоратор DeWalt D25133K 800Вт SDS-plus", 12000, 18000),
        ("Компрессор CA2180324 8 атм 24л", 15000, 22000),
    ],
    "Спецтехника": [
        ("Погрузчик SEM 655D 2017г.в.", 3500000, 5500000),
        ("Экскаватор Hyundai R220LC-9S 2019г.в.", 6500000, 9000000),
        ("Автокран Галичанин КС-55713-1 25т", 8000000, 12000000),
    ],
    "Строительные материалы": [
        ("КИРПИЧ ОГНЕУПОР.ОСН:ФАСОННЫЙ;ША К-713-13", 85, 150),
        ("Цемент ПЦ 500-Д0 М500 50кг", 350, 500),
        ("Пескобетон М300 (40кг)", 250, 400),
    ],
    "Оргтехника": [
        ("МФУ Kyocera ECOSYS M2040dn", 35000, 55000),
        ("Принтер этикеток Godex G500", 12000, 18000),
    ]
}

def download_placeholder_image(upload_dir, seed_str):
    """Скачивает стабильную картинку с Picsum на основе названия"""
    try:
        # Генерируем уникальный, но стабильный ID для картинки (0-1000)
        img_id = abs(hash(seed_str)) % 1000
        url = f"https://picsum.photos/id/{img_id}/800/600"
        
        response = requests.get(url, timeout=10, allow_redirects=True)
        if response.status_code == 200:
            filename = f"{uuid.uuid4().hex}.jpg"
            filepath = os.path.join(upload_dir, filename)
            with open(filepath, 'wb') as f:
                f.write(response.content)
            return filename
    except:
        pass
    return None

def main():
    app = create_app()
    with app.app_context():
        # Сброс сессии
        db.session.remove()
        
        upload_dir = os.path.join(app.root_path, 'static/uploads')
        os.makedirs(upload_dir, exist_ok=True)
        
        owner = db.session.get(User, OWNER_USER_ID)
        categories = Category.query.all()
        regions = Region.query.filter_by(parent_id=None).all()
        
        print(f"🚀 Генерация {COUNT} товаров с РЕАЛЬНЫМИ ценами...")
        
        cnt = 0
        for i in range(COUNT):
            try:
                # 1. Выбор категории и товара
                cat_obj = random.choice(categories)
                
                # Ищем подходящие товары для этой категории
                candidates = []
                for db_cat, items in PRODUCTS_DB.items():
                    if db_cat.lower() in cat_obj.name.lower():
                        candidates = items
                        break
                
                # Если не нашли - берем любые
                if not candidates:
                    candidates = random.choice(list(PRODUCTS_DB.values()))
                
                item_data = random.choice(candidates)
                
                # Если кортеж (Название, Мин, Макс)
                if len(item_data) == 3:
                     title, min_p, max_p = item_data
                     price = round(random.uniform(min_p, max_p), 2)
                else:
                    # Fallback
                    title = item_data[0]
                    price = 1000
                
                # 2. Картинка (одна)
                images = []
                # Скачиваем 1 картинку (стабильную для этого названия)
                img_file = download_placeholder_image(upload_dir, title)
                if img_file:
                    images.append(img_file)

                # 3. Создаем продукт
                product = Product(
                    title=title,
                    description=f"Состояние: Новое\n\nПредлагаем: {title}.\nЦена указана с НДС.\nДоставка по РФ.",
                    price=price,
                    price_type="fixed",
                    quantity=random.randint(10, 5000) if "Болт" in title else random.randint(1, 50),
                    category_id=cat_obj.id,
                    user_id=owner.id,
                    status=1,
                    images=images,
                    condition="new",
                    region=random.choice(regions).name if regions else None,
                    region_id=random.choice(regions).id if regions else None,
                    external_organization=random.choice(COMPANY_NAMES),
                    external_contact="Отдел продаж",
                    external_phone="+X XXX XXX-XX-XX",
                    vat_included=True,
                    source_url=None,
                    view_count=random.randint(0, 300),
                    created_at=datetime.now() - timedelta(days=random.randint(1, 45))
                )
                
                db.session.add(product)
                cnt += 1
                
                # Коммит пачками по 10
                if cnt % 10 == 0:
                    db.session.commit()
                    print(f"  Создано {cnt}...")

            except Exception as e:
                print(f"⚠️ Ошибка на {i}: {e}")
                db.session.rollback()
        
        db.session.commit()
        print(f"✅ Успешно! Создано {cnt} товаров.")

if __name__ == "__main__":
    main()
