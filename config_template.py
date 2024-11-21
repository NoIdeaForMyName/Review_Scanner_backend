# create real config.py

class Config:
    SQLALCHEMY_DATABASE_URI = 'postgresql://username:password@localhost:5432/mydatabase'  # Replace with actual credentials
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = 'your_jwt_secret_key'  # Replace with a real secret