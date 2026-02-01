#!/usr/bin/env python3
import requests
import json

# URL приложения
BASE_URL = "http://127.0.0.1:5005"

def test_api():
    print("Тестирование API сообщений...")
    
    # Сначала проверяем главную страницу
    try:
        response = requests.get(BASE_URL)
        print(f"Главная страница: {response.status_code}")
    except Exception as e:
        print(f"Ошибка главной страницы: {e}")
        return
    
    # Пробуем получить страницу входа
    try:
        response = requests.get(f"{BASE_URL}/login")
        print(f"Страница входа: {response.status_code}")
    except Exception as e:
        print(f"Ошибка страницы входа: {e}")
        return
    
    # Пробуем API без авторизации
    try:
        response = requests.get(f"{BASE_URL}/api/conversations")
        print(f"API без авторизации: {response.status_code}")
        if response.status_code == 200:
            print("Ответ:", response.text[:100])
    except Exception as e:
        print(f"Ошибка API: {e}")

if __name__ == "__main__":
    test_api()
