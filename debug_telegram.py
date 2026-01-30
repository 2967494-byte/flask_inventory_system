import requests
import sys

# Values from config.py
TOKEN = '8576859315:AAFUsWf2_L2ZaJEE8lUxTgOxK_e2IlOTnD0'
CHAT_ID = '390300'

def check_bot():
    print(f"--- Checking Bot Token ---")
    url = f"https://api.telegram.org/bot{TOKEN}/getMe"
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
        if resp.status_code == 200 and data.get('ok'):
            print(f"[OK] Bot found: @{data['result']['username']} (ID: {data['result']['id']})")
            return True
        else:
            print(f"[FAIL] Bot check failed: {resp.status_code} - {data}")
            return False
    except Exception as e:
        print(f"[ERROR] Connection error: {e}")
        return False

def send_test_msg():
    print(f"\n--- Sending Test Message to ID: {CHAT_ID} ---")
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        'chat_id': CHAT_ID,
        'text': 'Test message from diagnostics'
    }
    try:
        resp = requests.post(url, json=payload, timeout=10)
        data = resp.json()
        if resp.status_code == 200 and data.get('ok'):
            print(f"[OK] Message sent successfully!")
        else:
            print(f"[FAIL] Message sending failed: {resp.status_code} - {data}")
            if resp.status_code == 400 and 'chat not found' in str(data):
                print("[HINT] The CHAT_ID might be wrong. If this is a user, they must start the bot first. If a channel, the bot must be admin.")
    except Exception as e:
        print(f"[ERROR] Sending error: {e}")

if __name__ == "__main__":
    if check_bot():
        send_test_msg()
