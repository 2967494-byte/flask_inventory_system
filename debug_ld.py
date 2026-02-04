from nelikvidi_parser import NelikvidiParser
from bs4 import BeautifulSoup
import json

def debug_ld():
    p = NelikvidiParser()
    p.pass_anti_bot()
    url = "https://nelikvidi.com/irkutsk/pi505003-realizaciya-truby-novye-5308303.html"
    r = p.session.get(url)
    r.encoding = 'utf-8'
    soup = BeautifulSoup(r.text, 'lxml')
    
    ld_script = soup.find('script', type='application/ld+json')
    if ld_script:
        print("JSON-LD found:")
        print(ld_script.string.strip())
    else:
        print("No JSON-LD found.")

if __name__ == "__main__":
    debug_ld()
