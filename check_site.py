import requests

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def check_site(url):
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"URL: {url}")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("Successfully fetched content.")
            # Print a bit of content to see if it's the real page
            print(response.text[:500])
        else:
            print(f"Failed to fetch content. Status: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_site("https://nelikvidi.com/")
    check_site("https://nelikvidi.com/yakutsk/truba-besshovnaya-goryachedeformirovannaya-127h8h1260-5485396.html")
