from nelikvidi_parser import NelikvidiParser
import json

def debug_price():
    p = NelikvidiParser()
    url = "https://nelikvidi.com/yakutsk/truba-besshovnaya-goryachedeformirovannaya-127h8h1260-5485396.html"
    data = p.scrape_product(url)
    print(json.dumps(data, indent=4, ensure_ascii=False))

if __name__ == "__main__":
    debug_price()
