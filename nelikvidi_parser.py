import requests
import os
import json
import time
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin
import sys

class NelikvidiParser:
    def __init__(self):
        self.base_url = "https://nelikvidi.com"
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Referer': 'https://nelikvidi.com/',
        }
        self.session.headers.update(self.headers)
        self.passed_gate = False

    def pass_anti_bot(self):
        print("Passing anti-bot gate...")
        try:
            self.session.get(self.base_url)
            r = self.session.post(f"{self.base_url}/a9f3-get-pass-cookie")
            if r.status_code == 200:
                print("Successfully set pass-cookie.")
                self.passed_gate = True
                return True
            else:
                print(f"Failed to set cookie. Status: {r.status_code}")
                return False
        except Exception as e:
            print(f"Error passing gate: {e}")
            return False

    def get_catalog_links(self, max_pages=1):
        if not self.passed_gate:
            self.pass_anti_bot()
        
        links = []
        for page in range(1, max_pages + 1):
            url = f"{self.base_url}/catalog?page={page}"
            print(f"Crawling catalog page {page}...")
            r = self.session.get(url)
            r.encoding = 'utf-8'
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, 'lxml')
                for a in soup.find_all('a', href=True):
                    href = a['href']
                    full_url = urljoin(self.base_url, href)
                    if re.search(r'-\d+\.html$', full_url):
                        if not any(x in full_url for x in ['/org-', '/news/', '/contests-', '/conpart-', '/site/']):
                            links.append(full_url)
            time.sleep(1)
        return list(set(links))

    def get_all_product_links(self):
        if not self.passed_gate:
            self.pass_anti_bot()
        
        print("Fetching sitemap index...")
        links = []
        try:
            r = self.session.get(f"{self.base_url}/sitemap.xml")
            r.encoding = 'utf-8'
            if r.status_code == 200:
                sitemaps = re.findall(r'<loc>(.*?)</loc>', r.text)
                for s in sitemaps:
                    if 'sitemap-' in s:
                        sr = self.session.get(s)
                        sr.encoding = 'utf-8'
                        if sr.status_code == 200:
                            sub_links = re.findall(r'<loc>(.*?)</loc>', sr.text)
                            product_links = []
                            for l in sub_links:
                                if re.search(r'-\d+\.html$', l):
                                    if not any(x in l for x in ['/org-', '/news/', '/contests-', '/conpart-', '/site/']):
                                        product_links.append(l)
                            links.extend(product_links)
            return list(set(links))
        except Exception as e:
            print(f"Error gathering links: {e}")
            return []

    def scrape_product(self, url):
        if not self.passed_gate:
            self.pass_anti_bot()

        try:
            r = self.session.get(url)
            r.encoding = 'utf-8'
            if r.status_code != 200:
                return None
            
            soup = BeautifulSoup(r.text, 'lxml')
            data = {}
            
            # JSON-LD for core structured data
            json_ld_script = soup.find('script', type='application/ld+json')
            if json_ld_script:
                try:
                    ld = json.loads(json_ld_script.string)
                    if isinstance(ld, list): ld = ld[0]
                    data['name'] = ld.get('name', '').replace('VIP', '', 1).strip()
                    data['description'] = ld.get('description', '').strip()
                    data['category'] = ld.get('category', '').strip()
                    data['quantity'] = ld.get('numberOfItems', '').strip()
                    if 'offers' in ld:
                        data['price'] = ld['offers'].get('price', '').strip()
                except:
                    pass

            # Enhanced Price & VAT extraction
            data['vat_included'] = False
            price_table = soup.select_one('table.product-actions')
            if price_table:
                price_cell = price_table.select_one('td.price')
                if price_cell:
                    # 1. VAT Status
                    small_tag = price_cell.find('small')
                    if small_tag:
                        small_text = small_tag.get_text(strip=True).lower()
                        data['vat_included'] = 'с ндс' in small_text and 'без' not in small_text
                    
                    # 2. Price Value
                    if 'Договорная' in price_cell.get_text():
                        data['price'] = '0'
                        data['negotiable'] = True
                    else:
                        # Get all text and remove small tag text
                        full_text = price_cell.get_text(separator=' ', strip=True)
                        if small_tag:
                            full_text = full_text.replace(small_tag.get_text(strip=True), '')
                        data['price'] = full_text.strip()
            
            # Fallback if table method fails
            if 'price' not in data:
                price_tag = soup.select_one('.formated_price')
                if price_tag:
                    data['price'] = price_tag.get_text(strip=True)
                
                alt_price = soup.find(class_='h3', string=re.compile('Договорная', re.I))
                if alt_price:
                    data['price'] = '0'
                    data['negotiable'] = True

            if not data.get('name'):
                title_tag = soup.find('h1')
                data['name'] = title_tag.get_text(strip=True).replace('VIP', '', 1).strip() if title_tag else ""

            # Extract details using a more robust method
            details = {}
            for p in soup.find_all('p'):
                b = p.find('b')
                if b:
                    label = b.get_text(strip=True).replace(':', '').strip()
                    # Get everything AFTER the <b> tag in this paragraph
                    raw_p = str(p)
                    # Use regex to get text after </b>
                    match = re.search(r'</b>(.*?)</p>', raw_p, re.DOTALL | re.IGNORECASE)
                    if match:
                        val_html = match.group(1)
                        # Clean HTML from value
                        val = BeautifulSoup(val_html, 'lxml').get_text(strip=True)
                        # Replace non-breaking spaces
                        val = val.replace('\xa0', ' ').strip()
                        if label and val:
                            details[label] = val
            
            data['details'] = details

            # Images from swiper
            images = []
            gallery = soup.find(id='gallery-top-wrapper')
            if gallery:
                for img_link in gallery.find_all('a'):
                    if img_link.get('href'):
                        images.append(urljoin(self.base_url, img_link.get('href')))
            
            if not images:
                og_image = soup.find('meta', property='og:image')
                if og_image:
                    images.append(urljoin(self.base_url, og_image.get('content')))
            
            data['images'] = images
            data['url'] = url

            # NEW: Extract Phone Number
            phone_trigger = soup.find('a', class_='phone-trigger')
            if phone_trigger and phone_trigger.get('data-url'):
                try:
                    p_url = urljoin(self.base_url, phone_trigger.get('data-url'))
                    # Must use AJAX header
                    pr = self.session.get(p_url, headers={'X-Requested-With': 'XMLHttpRequest'}, timeout=10)
                    if pr.status_code == 200:
                        # The response is often JSON: "<a href=\"tel:...\">...</a>"
                        p_html = pr.text.strip('"').replace('\\"', '"')
                        p_soup = BeautifulSoup(p_html, 'lxml')
                        data['phone'] = p_soup.get_text(strip=True)
                except:
                    pass
            
            return data
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return None

    def save_data(self, data, filename):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def download_image(self, url, folder):
        try:
            if not os.path.exists(folder):
                os.makedirs(folder, exist_ok=True)
            filename = os.path.join(folder, url.split('/')[-1])
            if os.path.exists(filename):
                return filename
            r = self.session.get(url, timeout=10)
            if r.status_code == 200:
                with open(filename, 'wb') as f:
                    f.write(r.content)
                return filename
        except Exception as e:
            print(f"Error image {url}: {e}")
        return None

if __name__ == "__main__":
    parser = NelikvidiParser()
    product_url = "https://nelikvidi.com/lipeck/kabel-bc5e-4-lshf-aesp-6019197.html"
    result = parser.scrape_product(product_url)
    if result:
        parser.save_data(result, "sample_debug.json")
