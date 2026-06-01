from flask import Blueprint, request, jsonify
from extensions import db, bcrypt
from models import User
import jwt
import datetime
import os

auth = Blueprint("auth", __name__)

@auth.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    if(not email or not password):
        return jsonify({"error": "email and password are required"}), 400

    
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "email already registered"}), 409

    
    hashed = bcrypt.generate_password_hash(password).decode("utf-8")

    user = User(email=email, password_hash=hashed)

    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "user created"}), 201

@auth.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    if(not email or not password):
        return jsonify({"error": "email and password are required"}), 400
    
    user = User.query.filter_by(email=email).first()
    
    if not user or not bcrypt.check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid Credentials"}), 401
    
    payload = {"user_id": user.id, "role": user.role, "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=24)}

    encoded_jwt = jwt.encode(payload, os.environ.get("SECRET_KEY"), algorithm="HS256")

    return jsonify({"token": encoded_jwt}), 200

