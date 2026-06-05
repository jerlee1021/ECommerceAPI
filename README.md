# ECommerceAPI

A minimal e-commerce REST API built with Flask. Covers user auth, product management, cart operations, and Stripe-powered checkout. Built as a learning project — no frontend, tested entirely via Postman.

---

## Stack

- **Framework:** Flask
- **Database:** SQLite via SQLAlchemy ORM
- **Migrations:** Alembic
- **Auth:** PyJWT + flask-bcrypt
- **Payments:** Stripe Python SDK (test mode)
- **Environment variables:** python-dotenv

---

## Data Model

Four tables:

- **users** — id, email, password_hash, role (user | admin), created_at
- **products** — id, name, price, stock, created_at
- **cart_items** — id, user_id, product_id, quantity
- **orders** — id, user_id, total, status, stripe_payment_id, created_at

---

## Endpoints

### Auth (public)
| Method | Route | Description |
|--------|-------|-------------|
| POST | `/register` | Register a new user, returns 201 |
| POST | `/login` | Returns a JWT |

### Products
| Method | Route | Description |
|--------|-------|-------------|
| POST | `/products` | Create a product (admin only) |
| GET | `/products` | List all products (public) |
| GET | `/products/<id>` | Get a single product (public) |

### Cart (requires JWT)
| Method | Route | Description |
|--------|-------|-------------|
| POST | `/cart` | Add a product to cart (upserts quantity) |
| DELETE | `/cart/<product_id>` | Remove a product from cart |
| GET | `/cart` | View cart items and running total |

### Checkout (requires JWT)
| Method | Route | Description |
|--------|-------|-------------|
| POST | `/checkout` | Create a Stripe PaymentIntent from cart total |
| POST | `/webhook` | Stripe webhook — creates order and clears cart on payment success |
| GET | `/orders` | View past orders |

---

## Auth

- JWT-based, fully stateless — tokens are never stored server-side
- Protected routes use a `@token_required` decorator
- Admin routes use an `@admin_required` decorator
- Send token as: `Authorization: Bearer <token>`
- JWT payload contains: `user_id`, `role`, `exp`

---

## Stripe Integration

- Test mode only — no real money moves
- `POST /checkout` creates a PaymentIntent and returns a `client_secret`
- `POST /webhook` verifies the Stripe signature before processing any event
- On `payment_intent.succeeded`: creates an order record and clears the user's cart
- Local webhook testing uses the Stripe CLI: `stripe listen --forward-to localhost:5000/webhook`

---

## Setup

1. Clone the repo and create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. Create a `.env` file in the project root:
   ```
   SECRET_KEY=your_secret_key
   STRIPE_SECRET_KEY=sk_test_...
   STRIPE_WEBHOOK_SECRET=whsec_...
   ```

3. Run migrations:
   ```bash
   alembic upgrade head
   ```

4. Start the server:
   ```bash
   python app.py
   ```

5. For webhook testing, run in a separate terminal:
   ```bash
   stripe listen --forward-to localhost:5000/webhook
   ```
