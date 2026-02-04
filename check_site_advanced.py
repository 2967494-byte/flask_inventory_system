import requests
import time

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'Referer': 'https://nelikvidi.com/',
    'Origin': 'https://nelikvidi.com',
}

def check_site_advanced():
    session = requests.Session()
    session.headers.update(headers)
    
    # 1. First request to get initial cookies/session if any
    print("Step 1: Initial GET to nelikvidi.com")
    r1 = session.get("https://nelikvidi.com/")
    print(f"Status: {r1.status_code}")
    # print(r1.text[:200]) # Look for the splash page hints

    # 2. Try to get the pass-cookie (emulating the button click)
    print("\nStep 2: POST to /a9f3-get-pass-cookie")
    try:
        r2 = session.post("https://nelikvidi.com/a9f3-get-pass-cookie")
        print(f"Status: {r2.status_code}")
        print(f"Cookies after POST: {session.cookies.get_dict()}")
    except Exception as e:
        print(f"POST error: {e}")

    # 3. Try to get the main page again
    print("\nStep 3: GET home page with cookies")
    r3 = session.get("https://nelikvidi.com/")
    print(f"Status: {r3.status_code}")
    if r3.status_code == 200:
        print("Success! Got home page.")
        # print(r3.text[:1000])
    
    # 4. Try to get the product page
    print("\nStep 4: GET product page")
    product_url = "https://nelikvidi.com/yakutsk/truba-besshovnaya-goryachedeformirovannaya-127h8h1260-5485396.html"
    r4 = session.get(product_url)
    print(f"Status: {r4.status_code}")
    if r4.status_code == 200:
        print("Success! Got product page.")
        with open("product_sample.html", "w", encoding="utf-8") as f:
            f.write(r4.text)
        print("Saved to product_sample.html")
    else:
        print("Still blocked.")

    # 5. Check sitemap
    print("\nStep 5: Check Sitemap")
    r5 = session.get("https://nelikvidi.com/sitemap.xml")
    print(f"Sitemap Status: {r5.status_code}")
    if r5.status_code == 200:
        print("Sitemap found!")
        print(r5.text[:500])

if __name__ == "__main__":
    check_site_advanced()
