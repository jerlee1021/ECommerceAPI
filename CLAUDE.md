# CLAUDE.md

This file provides context for Claude Code sessions working on this project.
Read this before writing or suggesting any code.

---

## What this project is

A minimal e-commerce REST API built for learning backend development.
The priority is clarity and understanding over completeness or production-readiness.
Do not over-engineer. Do not add features not listed here.

---

## Stack — do not deviate from these

- **Framework:** Flask (not FastAPI, not Django)
- **Database:** SQLite via SQLAlchemy ORM (do not suggest PostgreSQL until explicitly asked)
- **Auth:** PyJWT + flask-bcrypt (do not suggest flask-jwt-extended or any other auth library)
- **Payments:** Stripe Python SDK in test mode only
- **Migrations:** Alembic
- **Testing:** Postman — there is no frontend, no pytest suite (yet)
- **Environment variables:** python-dotenv with a `.env` file

---

## Data model — four tables only

```
users
  id, email, password_hash, role (user | admin), created_at

products
  id, name, price, stock, created_at

cart_items
  id, user_id (FK → users), product_id (FK → products), quantity

orders
  id, user_id (FK → users), total, status, stripe_payment_id, created_at
```

Do not add tables or columns unless the user explicitly asks.

---

## Endpoints — full list

### Auth (public)
- POST /register — email + password, returns 201
- POST /login — email + password, returns JWT

### Products
- POST /products — admin only, creates a product
- GET /products — public, lists all products
- GET /products/<id> — public, single product

### Cart (authenticated users)
- POST /cart — add product to cart
- DELETE /cart/<product_id> — remove product from cart
- GET /cart — view cart and running total

### Checkout (authenticated users)
- POST /checkout — create Stripe PaymentIntent from cart total
- POST /webhook — Stripe calls this on payment confirmation; create order, clear cart
- GET /orders — view past orders

---

## Auth implementation

- All protected routes use a `@token_required` decorator
- Admin-only routes use a `@admin_required` decorator (or a role check inside token_required)
- JWT payload contains: `user_id`, `role`, `exp`
- Client sends token as: `Authorization: Bearer <token>`
- The server never stores tokens — fully stateless

---

## Stripe notes

- Test mode only — never real keys, never real cards
- Test card: 4242 4242 4242 4242
- Use Stripe CLI to forward webhooks locally during development
- `/webhook` must verify the Stripe signature header before processing
- On successful payment: create order record, clear user's cart

---

## Coding guidelines

- Keep route files thin — move business logic into separate helper functions or service modules
- Always validate request body fields before processing — return 400 if required fields are missing
- Return consistent JSON error responses: `{ "error": "message" }`
- Use environment variables for all secrets — SECRET_KEY, STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET
- Never hardcode secrets anywhere in the codebase

---

## What NOT to do

- Do not build a frontend — Postman is used for all testing
- Do not add email verification, refresh tokens, or OAuth
- Do not switch to PostgreSQL unless asked
- Do not add product search/filtering unless asked
- Do not add pytest unless asked
- Do not suggest Docker or containerisation
- Do not add rate limiting or caching
- Do not generate large blocks of boilerplate unprompted — explain concepts first, write code when asked

---

## Recommended build order

1. Flask app initialisation — confirm `/health` returns JSON
2. SQLAlchemy models — define all four tables before any routes
3. Alembic setup and initial migration
4. `/register` and `/login`
5. `@token_required` and `@admin_required` decorators
6. Product endpoints
7. Cart endpoints
8. Stripe checkout + webhook

---

## Current status

Track progress here as the project develops. Update this section as each phase is completed.

- [x] Flask app initialised
- [x] Database models defined
- [x] Alembic configured
- [x] Auth endpoints working (`/register` and `/login` both done and tested in Postman)
- [x] Auth decorators working (`@token_required` and `@admin_required` both tested in Postman)
- [x] Product endpoints working
- [x] Cart endpoints working
- [ ] Stripe integration working

## Session notes — where we left off

### Completed this session
- Wrote and tested all three cart endpoints in `cart.py`
  - `POST /cart` — `@token_required`, upsert logic (create or increment quantity), returns 200
  - `DELETE /cart/<product_id>` — `@token_required`, scoped to authenticated user, returns 200
  - `GET /cart` — `@token_required`, returns item list and running total, Decimal cast to float
- All three tested and confirmed working in Postman including upsert edge case

### In progress
- Stripe integration — not started yet

### Up next
1. Install Stripe SDK and add keys to `.env`
2. Write `POST /checkout` — create a Stripe PaymentIntent from the cart total
3. Write `POST /webhook` — verify Stripe signature, create order, clear cart
4. Write `GET /orders` — return past orders for the authenticated user

### Key decisions made
- `extensions.py` pattern used to avoid circular imports — always import `db` and `bcrypt` from there, never from `app`
- Alembic `sqlalchemy.url` set to absolute path: `sqlite:////Users/jeremylee/Desktop/ECommerceAPI/instance/ecommerce.db`
- `stripe_payment_id` on `Order` set to `nullable=True` — won't exist until Stripe confirms payment
- Decorators pass `user_id` and `role` as keyword arguments — route functions must declare them as parameters
- Generic error messages used on auth failures — never reveal whether email or password was the issue

### Mentoring context
- Treat the user as a junior developer fresh out of college — explain the "why" behind every decision before writing any code
- Do NOT write code directly into files — guide the user to write it themselves; only paste short inline snippets in chat to illustrate concepts
- The user understands syntax but lacks production experience — connect patterns to real-world engineering reasoning
