import os
import time
import requests
import re
from urllib.parse import urljoin
from datetime import datetime, timedelta
from app import create_app, db
from app.models import Product, Category, User, Region, City
from nelikvidi_parser import NelikvidiParser
import uuid
import sys
import codecs

# Configuration
LIMIT = 100 
OWNER_USER_ID = 1 
DEFAULT_CATEGORY_ID = 1

MONTH_MAP = {
    'янв': 1, 'февр': 2, 'мар': 3, 'апр': 4, 'мая': 5, 'июня': 6,
    'июля': 7, 'авг': 8, 'сент': 9, 'окт': 10, 'нояб': 11, 'дек': 12
}

def clean_text(text):
    if not text: return ""
    # Remove "купить" and "продажа" in various cases
    text = re.sub(r'(?i)\b(купить|продажа|продам|куплю)\b', '', text)
    # Remove VIP prefix if any
    text = text.replace('VIP', '')
    # Remove internal reference codes like (ПИ123456) or (пи123456)
    text = re.sub(r'\(\s*[Пп][Ии]\d+\s*\)', '', text)
    return text.strip().strip(',').strip()

def parse_nelikvidi_date(date_str):
    try:
        match = re.search(r'(\d+)\s+([а-яё]+)', date_str.lower())
        if match:
            day = int(match.group(1))
            month_str = match.group(2)
            month = MONTH_MAP.get(month_str, datetime.now().month)
            time_match = re.search(r'(\d{1,2}):(\d{2})', date_str)
            hour, minute = 0, 0
            if time_match:
                hour = int(time_match.group(1))
                minute = int(time_match.group(2))
            now = datetime.now()
            year = now.year
            dt = datetime(year, month, day, hour, minute)
            if dt > now: dt = datetime(year - 1, month, day, hour, minute)
            return dt
    except: pass
    return datetime.utcnow()

def get_or_create_category(nelikvidi_cat_str):
    try:
        # Default parent
        parent_name = "Электрооборудование"
        sub_name = clean_text(nelikvidi_cat_str)
        
        # Check for "(ParentName)"
        match = re.search(r'(.*?)\((.*?)\)', nelikvidi_cat_str)
        if match:
            sub_name = clean_text(match.group(1))
            parent_name = clean_text(match.group(2))
        
        # Ensure parent exists
        parent = Category.query.filter(Category.name.ilike(parent_name)).first()
        if not parent:
            parent = Category(name=parent_name)
            db.session.add(parent)
            db.session.flush()
        
        # Ensure sub exists
        if sub_name and sub_name != parent_name:
            sub = Category.query.filter(Category.name.ilike(sub_name), Category.parent_id == parent.id).first()
            if not sub:
                sub = Category(name=sub_name, parent_id=parent.id)
                db.session.add(sub)
                db.session.flush()
            return sub.id
        return parent.id
    except:
        return DEFAULT_CATEGORY_ID

def get_or_match_region(region_str):
    """Match region string from parsing to database Region"""
    if not region_str or len(region_str) < 3:
        return None
    
    try:
        # Clean the region string
        region_clean = region_str.strip()
        
        # Try exact match first (case-insensitive)
        region = Region.query.filter(Region.name.ilike(region_clean)).first()
        if region:
            return region.id
        
        # Try partial match - check if our DB region is contained in the parsed string
        # Example: "Архангельская область" should match "Архангельская"
        regions = Region.query.filter(Region.parent_id == None).all()
        for r in regions:
            if r.name.lower() in region_clean.lower() or region_clean.lower() in r.name.lower():
                return r.id
        
        # If no match found, return None (will use string field instead)
        return None
    except:
        return None

def mask_phone(phone_str):
    """Mask phone number to show only partial digits like +X XXX XXX-XX-XX"""
    if not phone_str or phone_str == "По запросу":
        return phone_str
    
    # Extract only digits
    digits = re.sub(r'\D', '', phone_str)
    
    if len(digits) < 4:
        return "+X XXX XXX-XX-XX"
    
    # Format: +X XXX XXX-XX-XX (show only first digit and last 2 digits)
    if len(digits) >= 11:
        return f"+{digits[0]} XXX XXX-XX-{digits[-2:]}"
    elif len(digits) >= 7:
        return f"+X XXX XXX-XX-{digits[-2:]}"
    else:
        return "+X XXX XXX-XX-XX"

def import_products():
    app = create_app()
    parser = NelikvidiParser()
    
    with app.app_context():
        owner = db.session.get(User, OWNER_USER_ID)
        if not owner: return

        links_file = "all_links.txt"
        links = []
        if os.path.exists(links_file):
            with open(links_file, "r") as f:
                links = [line.strip() for line in f if line.strip()]
        
        if len(links) < LIMIT:
            new_links = parser.get_catalog_links(max_pages=(LIMIT // 20) + 1)
            links = list(set(links + new_links))
            with open(links_file, "w") as f:
                for l in links: f.write(l + "\n")

        print(f"Total links: {len(links)}")
        to_process = links[:LIMIT]
        
        processed_count = 0
        for url in to_process:
            existing = Product.query.filter_by(source_url=url).first()
            if existing: continue

            data = parser.scrape_product(url)
            if not data: continue

            details = data.get('details', {})
            
            # 1. Clean Title: remove "купить", "продажа" and add asterisk
            title = clean_text(data.get('name', 'Без названия')) + ' *'
            
            # 2. Description: remove Source and specific details
            description = data.get('description', '')
            # Remove internal reference codes from description
            description = re.sub(r'\(\s*[Пп][Ии]\d+\s*\)', '', description)
            
            # Add back "Состояние" if available
            condition_text = details.get('Состояние', '')
            if condition_text:
                description = f"Состояние: {condition_text}\n\n" + description
            
            # Add disclaimer at the end
            description += "\n\n* Информация получена из открытых источников (сайт https://nelikvidi.com). Просим уточнять актуальность у продавца."
            
            # 3. Author / Organization
            author_raw = details.get('Разместил', '')
            # Remove HTML and everything after a non-breaking space or many spaces
            author = re.sub(r'<.*?>', '', author_raw).split('\xa0')[0].split('  ')[0].strip()
            # Remove digits, plus signs, and other non-letter symbols from the name
            author = re.sub(r'[0-9\+\>\<\-\(\)]', '', author).strip()
            # Ensure it's not empty after cleaning
            if not author: author = "Автор не указан"
            
            org = details.get('Организация', '')
            org = re.sub(r'<.*?>', '', org).strip()

            # 4. Category
            cat_id = get_or_create_category(details.get('Группа товаров', ''))
            
            # 5. Price/Qty/Views
            try:
                # Clean price string like "1 141,15" or "1.141,15"
                p_raw = data.get('price', '0')
                p_clean = re.sub(r'[^\d,.]', '', p_raw).replace(' ', '').replace('\xa0', '')
                if ',' in p_clean and '.' in p_clean:
                    # Mixed separators, usually dot is thousands and comma is decimal
                    p_clean = p_clean.replace('.', '').replace(',', '.')
                elif ',' in p_clean:
                    p_clean = p_clean.replace(',', '.')
                price = float(p_clean or 0)
            except: price = 0.0

            try:
                quantity = int(re.sub(r'\D', '', str(data.get('quantity', '1'))) or 1)
            except: quantity = 1

            try:
                view_count = int(re.sub(r'\D', '', str(details.get('Просмотров', '0'))) or 0)
            except: view_count = 0

            # 6. Date
            created_at = parse_nelikvidi_date(details.get('Размещено', ''))

            # 7. Images
            saved_images = []
            upload_dir = app.config['UPLOAD_FOLDER']
            for img_url in data.get('images', []):
                if "no-image" in img_url: continue # Skip placeholders
                try:
                    # USE PARSER SESSION TO BYPASS 403
                    r = parser.session.get(img_url, timeout=15)
                    if r.status_code == 200:
                        ext = img_url.split('.')[-1].lower().split('?')[0]
                        if len(ext) > 4: ext = 'jpg'
                        filename = f"{uuid.uuid4().hex}.{ext}"
                        with open(os.path.join(upload_dir, filename), 'wb') as f:
                            f.write(r.content)
                        saved_images.append(filename)
                        print(f"  Downloaded image: {filename}")
                    else:
                        print(f"  Image download failed. Status: {r.status_code}")
                except Exception as e:
                    print(f"  Image download error: {e}")

            # Match region to database
            region_str = details.get('Регион', '')
            region_id = get_or_match_region(region_str)

            # Create product
            product = Product(
                title=title,
                description=description,
                price=price,
                price_type='negotiable' if data.get('negotiable') else 'fixed',
                quantity=quantity,
                category_id=cat_id,
                user_id=owner.id,
                images=saved_images, # Save as LIST for JSON column
                status=Product.STATUS_PUBLISHED,
                condition='new' if 'Б/У' not in str(details.get('Состояние', '')) else 'used',
                region=region_str,
                region_id=region_id,
                view_count=view_count,
                created_at=created_at,
                source_url=url,
                external_contact=author,
                external_organization=org,
                external_phone=mask_phone(data.get('phone')) if data.get('phone') else "По запросу",
                vat_included=data.get('vat_included', False)
            )
            
            db.session.add(product)
            db.session.commit()
            
            processed_count += 1
            print(f"[{processed_count}/{LIMIT}] Imported: {title}")
            time.sleep(0.5)

        print(f"\nImport finished. {processed_count} items added.")

if __name__ == "__main__":
    import_products()
