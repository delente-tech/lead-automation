from flask import Flask
from src.config.logging_config import setup_logging
from src.routes.webhook import webhook_bp

logger = setup_logging()

def create_app():
    app = Flask(__name__)
    app.register_blueprint(webhook_bp)
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=9000)
