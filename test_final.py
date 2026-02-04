from nelikvidi_parser import NelikvidiParser
import json

def test_final():
    p = NelikvidiParser()
    url = "https://nelikvidi.com/irkutsk/pi505003-realizaciya-truby-novye-5308303.html"
    print(f"Scraping {url}...")
    data = p.scrape_product(url)
    if data:
        print(json.dumps(data, indent=4, ensure_ascii=False))

if __name__ == "__main__":
    test_final()
