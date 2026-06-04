from flask import Blueprint, request, jsonify
from extensions import db
from models import Product,CartItem
from decorators import token_required

cart_bp = Blueprint("cart", __name__)

@cart_bp.route("/cart", methods=["POST"])
@token_required
def add_to_cart(user_id, role):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400
    product_id = data.get("product_id")
    quantity = data.get("quantity")
    if not product_id or not quantity:
        return jsonify({"error": "product_id and quantity are required"}), 400
    if Product.query.get(product_id) is None:
        return jsonify({"error": "Product does not exist"}), 404
    cart_item = CartItem.query.filter_by(user_id=user_id,product_id=product_id).first()
    if cart_item is None:
        new_cart_item = CartItem(user_id=user_id, product_id=product_id,quantity=quantity)
        db.session.add(new_cart_item)
    else:
        cart_item.quantity += quantity
    db.session.commit()
    return jsonify({"message": "Added to cart"}), 200

@cart_bp.route("/cart/<int:product_id>", methods=["DELETE"])
@token_required
def remove_from_cart(user_id, role, product_id):
    cart_item = CartItem.query.filter_by(user_id=user_id, product_id=product_id).first()
    if cart_item is None:
        return jsonify({"error": "Item not found in cart"}), 404
    db.session.delete(cart_item)
    db.session.commit()
    return jsonify({"message":"Deleted from cart"}), 200

@cart_bp.route("/cart", methods=["GET"])
@token_required
def get_cart(user_id, role):
    cart_items = CartItem.query.filter_by(user_id=user_id).all()
    items = []
    total = 0
    for cart_item in cart_items:
        product = Product.query.get(cart_item.product_id)
        total += product.price * cart_item.quantity
        items.append({
            "product_id":product.id,
            "name":product.name,
            "price":float(product.price),
            "quantity":cart_item.quantity
        })
    return jsonify({"total":float(total), "items":items}), 200 
    