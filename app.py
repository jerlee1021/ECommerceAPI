from flask import Flask, jsonify
from extensions import db, bcrypt
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///ecommerce.db"

db.init_app(app)
bcrypt.init_app(app)

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

from auth import auth
app.register_blueprint(auth)

from products import products_bp
app.register_blueprint(products_bp)

from cart import cart_bp
app.register_blueprint(cart_bp)

if __name__ == "__main__":
    app.run(debug=True)