from nelikvidi_parser import NelikvidiParser
import json

def debug_scrape():
    p = NelikvidiParser()
    url = "https://nelikvidi.com/lipeck/kabel-bc5e-4-lshf-aesp-6019197.html"
    print(f"Scraping {url}...")
    r = p.session.get(url)
    print(f"Status: {r.status_code}, Encoding: {r.encoding}, Apparent: {r.apparent_encoding}")
    # print(f"Raw text start: {r.text[:200]}")
    data = p.scrape_product(url)
    if data:
        name = data.get('name', '')
        print(f"Name: {name}")
        # print(f"Name Bytes: {name.encode('utf-8', errors='replace')}")
        print("Details found:")
        print(json.dumps(data.get('details', {}), indent=4, ensure_ascii=False))
        
        # Test cleaning logic
        import re
        details = data.get('details', {})
        author_raw = details.get('Разместил', '')
        author = re.sub(r'<.*?>', '', author_raw).split('\xa0')[0].split('  ')[0].strip()
        author = re.sub(r'\d+$', '', author).strip()
        print(f"Cleaned Author: '{author}'")
        
        org = details.get('Организация', '')
        org = re.sub(r'<.*?>', '', org).strip()
        print(f"Cleaned Org: '{org}'")

if __name__ == "__main__":
    debug_scrape()
