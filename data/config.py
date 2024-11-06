from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import create_engine
from dotenv import load_dotenv
from os import environ

load_dotenv()

# .env fayl ichidan quyidagilarni o'qiymiz
DATABASE_URL = environ.get("DATABASE_URL")  # PostgreSQL
BOT_TOKEN = environ.get("BOT_TOKEN")  # Bot toekn
ADMINS = environ.get("ADMINS")  # adminlar ro'yxati
IP = environ.get("ip")  # Xosting ip manzili

engine = create_async_engine(environ.get("DATABASE_URL"), echo=True, future=True)
Base = declarative_base()
