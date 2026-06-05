import stripe
import os
from flask import Blueprint, request, jsonify
from extensions import db
from models import CartItem, Product, Order
from decorators import token_required

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")

checkout_bp = Blueprint("checkout", __name__)

@checkout_bp.route("/checkout", methods=["POST"])
@token_required
def checkout(user_id, role):
    cart_items = CartItem.query.filter_by(user_id=user_id).all()
    if not cart_items:
        return jsonify({"error": "Cart is empty"}), 400
    total = 0
    for cart_item in cart_items:
        product = Product.query.get(cart_item.product_id)
        total += product.price * cart_item.quantity
    intent = stripe.PaymentIntent.create(
        amount=int(total * 100),
        currency="usd",
        metadata={"user_id": user_id},
        automatic_payment_methods={"enabled": True, "allow_redirects": "never"}
    )

    return jsonify({"client_secret": intent.client_secret}), 200

@checkout_bp.route("/webhook", methods=["POST"])
def webhook():
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")
    webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET")
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    if event["type"] == "payment_intent.succeeded":
        intent = event["data"]["object"]
        user_id = int(intent["metadata"]["user_id"])
        total = intent["amount"] / 100
        order = Order(
            user_id=user_id,
            total=total,
            status="paid",
            stripe_payment_id=intent["id"]
        )
        db.session.add(order)
        CartItem.query.filter_by(user_id=user_id).delete()
        db.session.commit()

    return jsonify({"status": "ok"}), 200

@checkout_bp.route("/orders", methods=["GET"])
@token_required
def get_order(user_id, role):
    orders = Order.query.filter_by(user_id=user_id).all()
    order_list = []
    for order in orders:
        order_list.append({
            "id": order.id,
            "total": float(order.total),
            "status": order.status,
            "created_at": str(order.created_at)
        })

    return jsonify(order_list), 200