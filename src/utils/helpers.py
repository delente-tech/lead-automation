import json
from flask import Response
import hashlib
from bson import ObjectId
from datetime import datetime

def make_json_serializable(doc):
    """
    Recursively convert MongoDB-specific types (ObjectId, datetime) to strings
    so they can be JSON-serialized for caching in Redis.
    """
    if isinstance(doc, dict):
        return {k: make_json_serializable(v) for k, v in doc.items()}
    elif isinstance(doc, list):
        return [make_json_serializable(i) for i in doc]
    elif isinstance(doc, ObjectId):
        return str(doc)
    elif isinstance(doc, datetime):
        return doc.isoformat()
    else:
        return doc

def hashed_key(key: str) -> str:
    """Return SHA-256 hashed version of the cache key."""
    return hashlib.sha256(key.encode("utf-8")).hexdigest()

def json_response(data, status=200):
    return Response(
        json.dumps(data, indent=2),
        status=status,
        mimetype="application/json"
    )
