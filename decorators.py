from functools import wraps
from flask import request, jsonify
import jwt
import os

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "missing or invalid authorization header"}), 401
        token = auth_header[7:]
        try:
            payload = jwt.decode(token, os.environ.get("SECRET_KEY"), algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "invalid token"}), 401

        
        user_id = payload["user_id"]
        role = payload["role"]

        return f(*args, user_id=user_id, role=role, **kwargs)
    return decorated