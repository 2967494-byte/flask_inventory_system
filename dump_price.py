from nelikvidi_parser import NelikvidiParser
from bs4 import BeautifulSoup
import re

def dump_price_html():
    p = NelikvidiParser()
    p.pass_anti_bot()
    url = "https://nelikvidi.com/irkutsk/pi505003-realizaciya-truby-novye-5308303.html"
    r = p.session.get(url)
    r.encoding = 'utf-8'
    soup = BeautifulSoup(r.text, 'lxml')
    
    price_tag = soup.select_one('.formated_price')
    print(f"Price Tag HTML: {price_tag}")
    if price_tag:
        parent = price_tag.find_parent('td')
        print(f"Parent TD Repr: {repr(parent.get_text())}")
    else:
        # Check for Договорная
        alt = soup.find(class_='h3')
        if alt:
            print(f"Alt H3 Tag: {alt}")
            print(f"Alt H3 Text: {repr(alt.get_text())}")

if __name__ == "__main__":
    dump_price_html()
