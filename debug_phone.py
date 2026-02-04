from nelikvidi_parser import NelikvidiParser
import json
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin

def debug_phone():
    p = NelikvidiParser()
    p.pass_anti_bot()
    url = "https://nelikvidi.com/irkutsk/pi505003-realizaciya-truby-novye-5308303.html"
    print(f"Scraping {url}...")
    r = p.session.get(url)
    r.encoding = 'utf-8'
    if r.status_code != 200:
        print(f"Error: {r.status_code}")
        return

    soup = BeautifulSoup(r.text, 'lxml')
    
    # 1. Find regions and other details
    details = {}
    for pg in soup.find_all('p'):
        b = pg.find('b')
        if b:
            label = b.get_text(strip=True).replace(':', '').strip()
            raw_p = str(pg)
            match = re.search(r'</b>(.*?)</p>', raw_p, re.DOTALL | re.IGNORECASE)
            if match:
                val_html = match.group(1)
                val = BeautifulSoup(val_html, 'lxml').get_text(strip=True).replace('\xa0', ' ').strip()
                details[label] = val
    
    print(f"Region found: {details.get('Регион')}")
    
    # 2. Find phone trigger
    phone_trigger = soup.find('a', class_='phone-trigger')
    if phone_trigger and phone_trigger.get('data-url'):
        phone_url = urljoin(p.base_url, phone_trigger.get('data-url'))
        print(f"Fetching phone from: {phone_url}")
        
        # Add X-Requested-With header
        pr = p.session.get(phone_url, headers={'X-Requested-With': 'XMLHttpRequest'})
        print(f"Phone response status: {pr.status_code}")
        print(f"Phone response: {pr.text}")
    else:
        print("No phone trigger found.")

if __name__ == "__main__":
    debug_phone()
