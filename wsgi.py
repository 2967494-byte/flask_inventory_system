import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()




from app import create_app, db
from app.models import User, Category, Product

app = create_app()

if __name__ == '__main__':
    app.run()
