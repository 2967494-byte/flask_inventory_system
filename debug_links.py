from nelikvidi_parser import NelikvidiParser
import re

p = NelikvidiParser()
p.pass_anti_bot()
r = p.session.get("https://nelikvidi.com/sitemap-6.xml")
links = re.findall(r'<loc>(.*?)</loc>', r.text)
print(f"Total links: {len(links)}")
if links:
    print("First 5 links:")
    for l in links[:5]:
        print(l)
