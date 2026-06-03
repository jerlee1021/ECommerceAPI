from flask import Blueprint, request, jsonify
from extensions import db
from models import Product
from decorators import admin_required

products_bp = Blueprint("products", __name__)

@products_bp.route("/products", methods=["POST"])
@admin_required
def create_product(user_id, role):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400
    name = data.get("name")
    price = data.get("price")
    stock = data.get("stock")

    if name is None or price is None or stock is None:
        return jsonify({"error":"Product is invalid"}), 400
    
    product = Product(name=name, price=price, stock=stock)

    db.session.add(product)
    db.session.commit()

    return jsonify({"id": product.id, "name": product.name, "price": float(product.price), "stock": product.stock, "createdAt": product.created_at}), 201

@products_bp.route("/products", methods=["GET"])
def get_products():
    products = Product.query.all()
    product_list = []
    for product in products:
        entry = {"id": product.id, "name": product.name, "price": float(product.price), "stock": product.stock, "createdAt": product.created_at}
        product_list.append(entry)

    return jsonify(product_list), 200

@products_bp.route("/products/<id>", methods=["GET"])
def get_product(id):
    product = Product.query.get(id)
    if product is None:
        return jsonify({"error":"Product does not exist"}), 404

    return jsonify({"id": product.id, "name": product.name, "price": float(product.price), "stock": product.stock, "createdAt": product.created_at}), 200