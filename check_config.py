import os
from dotenv import load_dotenv

# Load .env
load_dotenv()

print(f"DATABASE_URL from env: {os.environ.get('DATABASE_URL')}")

if os.path.exists('config.py'):
    from config import Config
    print(f"Config.SQLALCHEMY_DATABASE_URI: {Config.SQLALCHEMY_DATABASE_URI}")
else:
    print("config.py not found in current directory")
