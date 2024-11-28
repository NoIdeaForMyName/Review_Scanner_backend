# create real config.py

run_config = {
    "debug": True,
    "host": "127.0.0.1",
    "port": 5000
}

class Config:
    SQLALCHEMY_DATABASE_URI = 'postgresql://username:password@localhost:5432/mydatabase'  # Replace with actual credentials
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = 'your_jwt_secret_key'  # Replace with a real secret