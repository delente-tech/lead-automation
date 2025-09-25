from functools import wraps
from flask import request
from src.config import settings

def require_webhook_secret(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        secret = request.headers.get("X-Webhook-Secret")
        if secret != settings.WEBHOOK_SECRET:
            return "Unauthorized", 401
        return f(*args, **kwargs)
    return wrapper
