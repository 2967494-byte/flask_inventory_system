import requests
import json
import os

# Hardcoded key from config.py to test
API_KEY = os.environ.get('DADATA_API_KEY') or '101eb3d6682561b0db5bf155c592a3f8dad52dcf'
INN_TO_TEST = '7707083893' # Sberbank

def test_inn():
    url = "https://suggestions.dadata.ru/suggestions/api/4_1/rs/findById/party"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Token {API_KEY}"
    }
    payload = {"query": INN_TO_TEST}
    
    print(f"--- Testing INN Search with Key: {API_KEY[:5]}... ---")
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            suggestions = data.get('suggestions', [])
            if suggestions:
                print(f"[SUCCESS] Found: {suggestions[0]['value']}")
                return True
            else:
                print("[WARNING] No suggestions found for known INN")
                return False
        else:
            print(f"[ERROR] API Request Failed: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")
        return False

if __name__ == "__main__":
    test_inn()
