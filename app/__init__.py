from flask import Flask
from flask_jwt_extended import JWTManager
from config import Config
from app.models import db

jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    with app.app_context():
        db.create_all()
    
    jwt.init_app(app)

    from app.routes_guests import main_bp
    app.register_blueprint(main_bp)

    return app