import requests
from nelikvidi_parser import NelikvidiParser
from bs4 import BeautifulSoup
import os

def test_img():
    p = NelikvidiParser()
    p.pass_anti_bot()
    img_url = "https://nelikvidi.com/img/org/14893/5308303/pi505003_realizaciya_1746544182681a26361827c.jpg"
    print(f"Testing direct image download: {img_url}")
    
    # Try with parser session
    try:
        r = p.session.get(img_url, timeout=15)
        print(f"Parser Session - Status: {r.status_code}")
        if r.status_code == 200:
            print(f"Parser Session - Length: {len(r.content)}")
    except Exception as e:
        print(f"Parser Session - Error: {e}")

    # Try raw requests
    try:
        r2 = requests.get(img_url, timeout=15)
        print(f"Raw Requests - Status: {r2.status_code}")
        if r2.status_code == 200:
            print(f"Raw Requests - Length: {len(r2.content)}")
    except Exception as e:
        print(f"Raw Requests - Error: {e}")

if __name__ == "__main__":
    test_img()
