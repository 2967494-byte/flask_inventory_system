"""
YANDO: Yandex Image Loader Service
Безопасный фоновый загрузчик изображений для товаров.
Версия: 1.0.0
"""
import os
import json
import time
import random
import logging
import requests
import re
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from urllib.parse import quote, urlparse
from app import create_app, db
from app.models import Product

# === КОНФИГУРАЦИЯ ===
MAX_DAILY_LIMIT = 100
IMAGES_PER_PRODUCT = 2
TIMEOUT = 20
STATE_FILE = "yandex_loader_state.json"
LOG_FILE = "yandex_loader.log"
UPLOAD_FOLDER = 'app/static/uploads'

# Паузы (секунды)
DELAY_REQUEST = (5, 15)   # Пауза перед самим HTTP-запросом (микро-пауза)
DELAY_PRODUCT = (180, 1200) # Пауза между ТОВАРАМИ (3 - 20 минут)
DELAY_CAPTCHA = (360, 780)  # Пауза при КАПЧЕ (6 - 13 минут)

# Коды ошибок
ERRORS = {
    "E001": "Достигнут суточный лимит",
    "E002": "Блокировка IP (403/429)",
    "E003": "CAPTCHA обнаружена",
    "E004": "Изображения не найдены",
    "E005": "Ошибка скачивания",
    "E006": "Ошибка сохранения файла"
}

# Ротация User-Agent
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0"
]

# Настройка логирования
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger('').addHandler(console)

class YandexLoader:
    def __init__(self):
        self.state = self._load_state()
        self.session = requests.Session()
        self.app = create_app()

    def _load_state(self):
        """Загрузка состояния из файла"""
        default_state = {
            "date": datetime.now().strftime('%Y-%m-%d'),
            "count": 0,
            "blocked_until": None
        }
        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE, 'r') as f:
                    data = json.load(f)
                    # Сброс счетчика, если новый день
                    if data.get("date") != datetime.now().strftime('%Y-%m-%d'):
                        data["date"] = datetime.now().strftime('%Y-%m-%d')
                        data["count"] = 0
                    return data
            except Exception as e:
                logging.error(f"Ошибка чтения state файла: {e}")
        return default_state

    def _save_state(self):
        """Сохранение состояния"""
        try:
            with open(STATE_FILE, 'w') as f:
                json.dump(self.state, f, indent=4)
        except Exception as e:
            logging.error(f"Ошибка записи state файла: {e}")

    def _check_limits(self):
        """Проверка лимитов и блокировок"""
        # 1. Проверка блокировки
        if self.state["blocked_until"]:
            block_time = datetime.fromisoformat(self.state["blocked_until"])
            if datetime.now() < block_time:
                logging.warning(f"⏸️ Система на паузе до {block_time} из-за блокировки.")
                return False
            else:
                self.state["blocked_until"] = None
                self._save_state()

        # 2. Суточный лимит
        if self.state["count"] >= MAX_DAILY_LIMIT:
            logging.info(f"🛑 {ERRORS['E001']}: {self.state['count']}/{MAX_DAILY_LIMIT}")
            return False

        return True

    def _get_headers(self):
        """Ротация заголовков"""
        return {
            'User-Agent': random.choice(USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
            'Referer': 'https://yandex.ru/',
            'Connection': 'keep-alive',
        }

    def _search_yandex(self, query):
        """Поиск и парсинг первых изображений"""
        url = f"https://yandex.ru/images/search?text={quote(query)}&nomisspell=1"
        
        try:
            # Рандомная пауза перед запросом
            delay = random.uniform(*DELAY_REQUEST)
            time.sleep(delay)
            
            response = self.session.get(
                url, 
                headers=self._get_headers(), 
                timeout=TIMEOUT,
                verify=False # Иногда нужны, если есть проблемы с SSL
            )
            
            # 1. Проверка на капчу/блокировку
            if "captcha" in response.url or "showcaptcha" in response.text:
                logging.error(f"🚫 {ERRORS['E003']}")
                return "CAPTCHA"
            
            if response.status_code in [403, 429]:
                logging.error(f"🚫 {ERRORS['E002']}: Код {response.status_code}")
                # Блокировка на 24 часа
                self.state["blocked_until"] = (datetime.now() + timedelta(hours=24)).isoformat()
                self._save_state()
                return "BLOCK"

            # 2. Продвинутый парсинг (ищем JSON в скриптах)
            soup = BeautifulSoup(response.text, 'html.parser')
            found_urls = []

            # Способ А: Ищем в тегах <script> (там часто лежит JSON с данными)
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string:
                    # Ищем прямые ссылки на картинки (оригиналы)
                    urls = re.findall(r'"url":"(https?://[^"]+\.(?:jpg|jpeg|png))"', script.string)
                    found_urls.extend(urls)
                    
                    # Ищем origin url в другой нотации
                    urls2 = re.findall(r'"origin":\s*{"url":"(https?://[^"]+)"', script.string)
                    found_urls.extend(urls2)

            # Способ Б: data-bem (legacy)
            if not found_urls:
                items = soup.find_all('div', class_='serp-item')
                for item in items:
                    try:
                        data = json.loads(item.get('data-bem', '{}'))
                        if 'serp-item' in data:
                            u = data['serp-item'].get('img_href')
                            if u: found_urls.append(u)
                    except: pass
            
            # Способ В: Хардкорный Regex по всему тексту (на самый крайний случай)
            if not found_urls:
                # Ищем http...jpg, но фильтруем маленькие иконки
                urls = re.findall(r'(https?://[^"\'\s]+\.(?:jpg|jpeg|png))', response.text)
                # Фильтруем мусор (yandex.net, аватарки и т.д.)
                clean_urls = [u for u in urls if 'avatars.mds.yandex.net' not in u and 'favicon' not in u]
                found_urls.extend(clean_urls)
            
            # Удаляем дубликаты и оставляем топ-5
            unique_urls = []
            seen = set()
            for u in found_urls:
                if u not in seen:
                    unique_urls.append(u)
                    seen.add(u)
            
            final_urls = unique_urls[:5]

            if not final_urls:
                logging.warning(f"⚠️ {ERRORS['E004']} для запроса: {query}")
                # Для отладки можно сохранить HTML
                # with open("debug_yandex.html", "w", encoding="utf-8") as f: f.write(response.text)
                return []
                
            return final_urls

        except Exception as e:
            logging.error(f"❌ Ошибка сети: {e}")
            return []

    def _download_and_save(self, url, product_id):
        """Скачивание и сохранение файла"""
        try:
            # 3 попытки ретрая
            for attempt in range(3):
                try:
                    r = self.session.get(url, headers=self._get_headers(), timeout=10, stream=True)
                    if r.status_code == 200:
                        break
                except:
                    if attempt == 2: raise
                    time.sleep(2)
            
            # Валидация
            if len(r.content) < 5000: # Слишком маленькая картинка
                return None
                
            # Имя файла
            parsed = urlparse(url)
            ext = os.path.splitext(parsed.path)[1]
            if not ext or len(ext) > 5: ext = '.jpg'
            
            filename = f"ya_{product_id}_{int(time.time())}_{random.randint(100,999)}{ext}"
            
            abs_path = os.path.join(self.app.root_path, 'static/uploads', filename)
            
            with open(abs_path, 'wb') as f:
                for chunk in r.iter_content(1024):
                    f.write(chunk)
                    
            return filename
            
        except Exception as e:
            logging.warning(f"{ERRORS['E005']}: {url} - {e}")
            return None

    def run(self):
        """Главный цикл"""
        print("🚀 Запуск сервиса загрузки изображений YANDO")
        logging.info("=== Start Session ===")
        
        if not self._check_limits():
            print("Лимиты исчерпаны или блокировка. См. лог.")
            return

        with self.app.app_context():
            # Находим товары БЕЗ картинок (или с пустым списком)
            # Используем casthint для корректного сравнения JSON с текстом
            from sqlalchemy import cast, String, Text
            
            # Фильтр: images IS NULL ИЛИ images (как текст) == '[]' ИЛИ images == ''
            products = Product.query.filter(
                (Product.images == None) | 
                (cast(Product.images, String) == '[]') | 
                (cast(Product.images, String) == '')
            ).limit(20).all() # Берем пачку 20 штук за раз
            
            if not products:
                logging.info("Нет товаров без изображений.")
                print("Все товары имеют изображения.")
                return

            print(f"Найдено {len(products)} товаров для обработки.")
            
            for product in products:
                # Обновляем состояние объекта из БД
                db.session.refresh(product)
                
                # Проверяем, вдруг он уже заполнен (дубликат, обработанный на прошлом шаге)
                current_imgs = str(product.images) if product.images else ''
                if current_imgs and current_imgs != '[]':
                    continue

                if not self._check_limits():
                    break
                    
                logging.info(f"📦 Обработка товара ID {product.id}: {product.title}")
                
                # === ЭТАП 0: Умный поиск (Reuse) ===
                # Ищем, есть ли уже товар с таким названием И картинкой
                existing_with_img = Product.query.filter(
                    Product.title == product.title,
                    Product.images != None,
                    cast(Product.images, String) != '[]',
                    cast(Product.images, String) != ''
                ).first()

                if existing_with_img:
                    logging.info(f"   ♻️ Найдено существующее изображение у ID {existing_with_img.id}. Копируем...")
                    product.images = existing_with_img.images
                    db.session.commit()
                    continue

                # === ЭТАП 1: Поиск в Яндекс ===
                search_query = f"{product.title}"
                results = self._search_yandex(search_query)
                
                if results == "BLOCK":
                    print("🛑 Обнаружена блокировка! Пауза 24 часа.")
                    break
                elif results == "CAPTCHA":
                    logging.warning(f"⏩ Пропуск товара ID {product.id} из-за капчи")
                    
                    # При капче делаем долгую паузу, чтобы Яндекс "остыл"
                    c_delay = random.uniform(*DELAY_CAPTCHA)
                    logging.warning(f"⚠️ Обнаружена капча. Остываем {c_delay/60:.1f} минут...")
                    time.sleep(c_delay)
                    
                    # Если капча, можно просто пропустить, не маркируя дубликаты
                    continue
                elif not results or isinstance(results, list) and len(results) == 0:
                    continue 
                
                # === ЭТАП 2: Скачивание ===
                saved_images = []
                for img_url in results[:IMAGES_PER_PRODUCT]:
                    filename = self._download_and_save(img_url, product.id)
                    if filename:
                        saved_images.append(filename)
                        logging.info(f"   ✅ Сохранено: {filename}")
                    
                    random_sleep = random.uniform(2, 5)
                    time.sleep(random_sleep)
                
                # === ЭТАП 3: Сохранение и дубликация ===
                if saved_images:
                    try:
                        img_str = ",".join(saved_images)
                        
                        # 1. Обновляем текущий
                        product.images = img_str
                        
                        # 2. Обновляем ВСЕ товары с таким же названием, у которых нет картинок
                        duplicates = Product.query.filter(
                            Product.title == product.title,
                            (Product.images == None) | 
                            (cast(Product.images, String) == '[]') | 
                            (cast(Product.images, String) == '')
                        ).all()
                        
                        count_dups = 0
                        for dup in duplicates:
                            if dup.id != product.id: # Текущий уже обновили
                                dup.images = img_str
                                count_dups += 1
                        
                        db.session.commit()
                        
                        if count_dups > 0:
                            logging.info(f"   ✨ Применено к {count_dups} дубликатам")
                        
                        # Обновляем счетчик запросов Яндекса (только 1 раз за серию)
                        self.state["count"] += 1
                        self._save_state()
                        
                    except Exception as e:
                        logging.error(f"{ERRORS['E006']}: {e}")
                        db.session.rollback()
                
                # Пауза
                p_delay = random.uniform(*DELAY_PRODUCT)
                logging.info(f"💤 Пауза {p_delay:.1f} сек...")
                time.sleep(p_delay)

        logging.info("=== End Session ===")
        print("Сессия завершена.")

if __name__ == "__main__":
    loader = YandexLoader()
    loader.run()
