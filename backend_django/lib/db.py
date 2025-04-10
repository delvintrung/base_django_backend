import os
from dotenv import load_dotenv
from mongoengine import connect
import sys

load_dotenv()  # Load biến môi trường từ .env

def connect_db():
    try:
        mongo_uri = os.getenv("MONGODB_URI")
        conn = connect(host=mongo_uri)
        print(f"✅ Connected to MongoDB: {mongo_uri}")
        return conn
    except Exception as e:
        print("❌ Failed to connect to MongoDB:", e)
        sys.exit(1)  # 1 là lỗi, 0 là thành công
