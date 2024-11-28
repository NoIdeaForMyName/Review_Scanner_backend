from app import create_app
from config import run_config

app = create_app()

if __name__ == "__main__":
    app.run(**run_config)