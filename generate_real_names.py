"""
Финальный генератор товаров.
- Использует реалистичные названия (Насос К-80, Кирпич ША-5 и т.д.)
- Пока без картинок (чтобы избежать API Error 403)
- Безопасно работает с БД
"""
import random
import uuid
from datetime import datetime, timedelta
from app import create_app, db
from app.models import Product, Category, User, Region

# Настройки
COUNT = 50
OWNER_USER_ID = 1

COMPANY_NAMES = [
    'ООО "СтройТехСнаб"', 'АО "ПромКомплект"', 'ООО "ИндустриТорг"',
    'ЗАО "ТехноСнаб"', 'ООО "МетизПром"', 'АО "ЭлектроКомплект"',
    'ООО "СпецПоставка"', 'ООО "ПромРесурс"', 'АО "ТехСервис"',
]

# БАЗА РЕАЛИСТИЧНЫХ НАЗВАНИЙ
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
        "Электродвигатель АИР 132 М4 11кВт",
        "Частотный преобразователь 5.5кВт 380В",
    ],
    "Трубопроводная арматура": [
        "Задвижка клиновая 30с41нж Ду100 Ру16",
        "Кран шаровой фланцевый КШФР Ду50 Ру40",
        "Затвор дисковый поворотный Ду200 Ру16",
        "Клапан обратный 16ч6р Ду80",
        "Фланец воротниковый Ду100 Ру16",
        "Отвод стальной 90гр 219х6",
    ],
    "Метизы и крепеж": [
        "Болт М16х60 ГОСТ 7798-70 оцинкованный",
        "Гайка М12 DIN 934 класс прочности 8",
        "Шайба 20 ГОСТ 11371-78 увеличенная",
        "Шпилька М20х120 ГОСТ 22032-76",
        "Анкер клиновой 12х100",
    ],
    "Насосное оборудование": [
        "Насос центробежный К 65-50-160",
        "Насос погружной ЭЦВ 6-10-110",
        "Насосная станция Grundfos Hydro MPC-E 2 CR15-2",
        "Насос вихревой ВК 1/16 0.37кВт",
        "Мотопомпа для грязной воды 80м3/ч",
    ],
    "Подшипники": [
        "Подшипник 6205-2RS (25х52х15)",
        "Подшипник роликовый 32210 (50х90х23)",
        "Подшипник шариковый 180204 (20х47х14)",
        "Подшипник корпусной UCP 208",
    ],
    "Инструмент": [
        "Дрель ударная Makita HP1631K 710Вт",
        "Болгарка Bosch GWS 750-125 750Вт",
        "Перфоратор DeWalt D25133K 800Вт SDS-plus",
        "Компрессор CA2180324 8 атм 24л",
        "Станок сверлильный 2М112",
        "Тиски слесарные 200мм",
    ],
    "Спецтехника": [
        "Погрузчик SEM 655D 2017г.в.",
        "Экскаватор Hyundai R220LC-9S 2019г.в.",
        "Автокран Галичанин КС-55713-1 25т",
        "Генератор дизельный 100 кВт",
        "Вилочный погрузчик Toyota 1.5т",
    ],
    "Строительные материалы": [
        "КИРПИЧ ОГНЕУПОР.ОСН:ФАСОННЫЙ;ША К-713-13",
        "Цемент ПЦ 500-Д0 М500 50кг",
        "Пескобетон М300 (40кг)",
        "Профнастил С8 0.45мм Цинк 2м",
        "Грунтовка глубокого проникновения 10л",
        "Сетка кладочная 50х50х3 (2х0.38м)",
    ],
    "Металлопрокат": [
        "Труба профильная 40х20х1.5 6м",
        "Уголок стальной 50х50х5",
        "Швеллер 10П (12м)",
        "Лист г/к 3мм 1250х2500",
        "Арматура А500С ф12 мм",
    ],
    "Оргтехника": [
        "МФУ Kyocera ECOSYS M2040dn",
        "Принтер этикеток Godex G500",
        "Сервер HP ProLiant DL360 Gen10",
        "Коммутатор Cisco Catalyst 2960",
    ]
}

def get_smart_name(category_name):
    # 1. Прямое совпадение категории
    for key, items in SPECIFIC_PRODUCTS.items():
        if key.lower() in category_name.lower():
            return random.choice(items)
    
    # 2. Если категория совсем неизвестна - берем случайное из всей базы
    all_items = []
    for items in SPECIFIC_PRODUCTS.values():
        all_items.extend(items)
    return random.choice(all_items)

def generate_products(count_to_gen):
    app = create_app()
    with app.app_context():
        # Сброс сессии для безопасности
        db.session.remove()
        
        print(f"🚀 Генерация {count_to_gen} товаров с реалистичными названиями...")
        
        owner = db.session.get(User, OWNER_USER_ID)
        categories = Category.query.all()
        regions = Region.query.filter_by(parent_id=None).all()
        
        if not owner or not categories:
            print("❌ Ошибка: нет пользователя или категорий")
            return

        cnt = 0
        for i in range(count_to_gen):
            try:
                category = random.choice(categories)
                
                # УМНАЯ ГЕНЕРАЦИЯ ИМЕНИ
                title = get_smart_name(category.name)
                
                region = random.choice(regions) if regions else None
                company = random.choice(COMPANY_NAMES)
                price_type = random.choice(['fixed', 'negotiable'])
                
                product = Product(
                    title=title,
                    description=f"Состояние: Новое\n\nПредлагаем к поставке: {title}.\nПродукция в наличии на складе. Паспорт качества прилагается.\nРаботаем с НДС.",
                    price=0 if price_type == 'negotiable' else round(random.uniform(500, 1500000), 2),
                    price_type=price_type,
                    quantity=random.randint(1, 1000),
                    category_id=category.id,
                    user_id=owner.id,
                    status=1,
                    images=[], # Без картинок
                    condition="new",
                    region=region.name if region else None,
                    region_id=region.id if region else None,
                    external_organization=company,
                    external_contact="Отдел продаж",
                    external_phone="+X XXX XXX-XX-XX",
                    # external_email - убран, так как нет в модели
                    source_url=None,
                    vat_included=True,
                    view_count=random.randint(5, 500),
                    created_at=datetime.now() - timedelta(days=random.randint(1, 90))
                )
                
                db.session.add(product)
                cnt += 1
                
                if cnt % 50 == 0:
                    db.session.commit()
                    print(f"  ...создано {cnt}")
                    
            except Exception as e:
                print(f"⚠️ Ошибка на товаре {i}: {e}")
                db.session.rollback()

        db.session.commit()
        print(f"✅ Готово! Всего создано: {cnt}")

if __name__ == "__main__":
    import sys
    count = 50
    if len(sys.argv) > 1:
        count = int(sys.argv[1])
    generate_products(count)
