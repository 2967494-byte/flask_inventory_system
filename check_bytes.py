import requests
url = "https://nelikvidi.com/lipeck/kabel-bc5e-4-lshf-aesp-6019197.html"
r = requests.get(url)
print(f"Headers: {r.headers.get('Content-Type')}")
print(f"Apparent: {r.apparent_encoding}")
print(f"Raw bytes preview: {r.content[:200]}")
# Try to find some Russian text in raw bytes
# 'Кабель' in UTF-8: \xd0\x9a\xd0\xb0\xd0\xb1\xd0\xb5\xd0\xbb\xd1\x8c
# 'Кабель' in cp1251: \xca\xe0\xe1\xe5\xeb\xfc
if b'\xd0\x9a' in r.content: print("Found UTF-8 indicator")
if b'\xca\xe0' in r.content: print("Found cp1251 indicator")
