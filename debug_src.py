from nelikvidi_parser import NelikvidiParser
from bs4 import BeautifulSoup

def debug_src():
    p = NelikvidiParser()
    url = "https://nelikvidi.com/moskva/himicheskoe-syryo-razlichnoe-iz-5346378.html"
    r = p.session.get(url)
    r.encoding = 'utf-8'
    with open("page_src.html", "w", encoding="utf-8") as f:
        f.write(r.text)
    print("Saved to page_src.html")

if __name__ == "__main__":
    debug_src()
