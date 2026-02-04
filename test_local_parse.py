from bs4 import BeautifulSoup
import json
import re

def test_local():
    with open("product_sample.html", "rb") as f:
        content = f.read()
        
    # Try multiple ways to parse
    for parser in ['html.parser', 'lxml']:
        print(f"--- PARSER: {parser} ---")
        soup = BeautifulSoup(content, parser)
        h1 = soup.find('h1')
        print(f"H1: {h1.get_text(strip=True) if h1 else 'None'}")
        
    # Check details
    soup = BeautifulSoup(content, 'lxml')
    details = {}
    for p in soup.find_all('p'):
        b = p.find('b')
        if b:
            label = b.get_text(strip=True).replace(':', '')
            val = p.get_text(strip=True).replace(b.get_text(strip=True), '', 1).strip()
            details[label] = val
    
    print("Details Labels:")
    print(list(details.keys()))

if __name__ == "__main__":
    test_local()
