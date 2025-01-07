# create real config.py

from datetime import timedelta

RUN_CONFIG = {
    "debug": True,
    "host": "127.0.0.1",
    "port": 5000
}

UPLOAD_DIR = "uploads"
UPLOAD_URL = f"http://{RUN_CONFIG['host']}:{RUN_CONFIG['port']}/uploads/"
MAX_UPLOAD_SIZE = (1024, 1024) # (width, height)
DATETIME_FORMAT = "%d.%m.%Y"

class Config:
    SQLALCHEMY_DATABASE_URI = 'postgresql://username:password@localhost:5432/mydatabase'  # Replace with actual credentials
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = 'your_jwt_secret_key'  # Replace with a real secret
    JWT_TOKEN_LOCATION = ['cookies']
    JWT_COOKIE_CSRF_PROTECT = True
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
