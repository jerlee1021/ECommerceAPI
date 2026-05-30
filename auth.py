from flask import Blueprint, request, jsonify
from extensions import db, bcrypt
from models import User

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