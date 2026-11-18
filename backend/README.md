# Jeebly RMS - Backend

The backend REST API service for the **Jeebly RMS (Rider Management System)**, built with **Python** and **Flask** using a 5-layer modular architecture, PostgreSQL, SQLAlchemy ORM, Marshmallow validation, and JWT authentication.

---

## 1. Project Overview

The backend serves as the core API engine for logistics and dispatch operations:
- Authenticates users with JWT tokens and bcrypt password hashing.
- Aggregates operational KPIs and fleet availability metrics for the dashboard.
- Manages rider onboarding, status tracking, filters, and profile photo uploads.
- Handles delivery order lifecycles, real-time rider assignments, and dispatch status transitions.
- Provides interactive OpenAPI 2.0 / Swagger documentation at `/docs`.

---

## 2. Tech Stack

| Technology | Exact Version | Purpose |
| :--- | :--- | :--- |
| **Python** | `3.13.15` (3.10+ compatible) | Application runtime environment |
| **Flask** | `2.3.3` | Core web framework and HTTP routing |
| **Flask-SQLAlchemy** | `3.1.1` | SQLAlchemy ORM integration for Flask |
| **SQLAlchemy** | `2.1.0` | Database ORM, query construction, and connection pooling |
| **Flask-Migrate** | `4.1.0` | Alembic database migration management wrapper |
| **Alembic** | `1.20.0` | Database schema migration engine |
| **Marshmallow** | `4.4.0` | Schema validation, serialization, and deserialization |
| **PyJWT** | `2.15.0` | Stateless JSON Web Token creation and verification |
| **Flask-Bcrypt** | `1.0.1` | Password hashing with adaptive salting (`bcrypt 5.0.0`) |
| **Flask-CORS** | `4.0.0` | Cross-Origin Resource Sharing header management |
| **Flasgger** | `0.9.7.1` | Swagger UI and OpenAPI 2.0 specification generation |
| **psycopg2-binary** | `2.9.13` | PostgreSQL database adapter |
| **Gunicorn** | `23.0.0` | Production WSGI HTTP server |
| **python-dotenv** | `1.2.4` | Environment variable management from `.env` |

---

## 3. Features

- **Authentication**: User registration, bcrypt password hashing, login verification, and stateless JWT token issuance (`HS256`).
- **Dashboard**: Real-time KPI counts (total, delivered, in-progress, cancelled), fleet availability breakdown, recent orders, and available riders.
- **Rider Management**: Full CRUD operations, debounced multi-field search, status/availability filtering, column sorting, pagination, and profile photo upload/removal.
- **Order Management**: Order CRUD operations, rider assignment/unassignment with automatic availability sync, status lifecycle progression, and date/status filtering.
- **Profile & Security**: Authenticated profile updates (name, phone) and password changes with current password verification.
- **API Documentation**: Interactive Swagger UI at `/docs` with JWT Bearer token authentication support.

---

## 4. Project Structure

```text
backend/
├── app/
│   ├── common/                   # Shared utilities and cross-cutting concerns
│   │   ├── auth_middleware.py    # @auth_required JWT authentication decorator
│   │   ├── error_handlers.py     # Global JSON error handlers (400, 401, 404, 500)
│   │   └── response_utils.py     # Unified success/error JSON response formatters
│   ├── modules/                  # Domain-driven feature modules
│   │   ├── auth/                 # Registration, login, and token generation
│   │   ├── dashboard/            # KPI metrics and fleet statistics
│   │   ├── orders/               # Order CRUD, assignment, and status transitions
│   │   ├── profile/              # User profile and password management
│   │   ├── riders/               # Rider CRUD, search, pagination, and photos
│   │   └── settings/             # System settings and user preferences
│   ├── static/uploads/riders/    # Stored rider profile avatar images
│   ├── __init__.py               # Application factory (create_app)
│   ├── config.py                 # Development, Testing, and Production configurations
│   ├── extensions.py             # Extension singletons (db, migrate, bcrypt, cors, flasgger)
│   ├── models.py                 # SQLAlchemy database models (User, Rider, Order)
│   └── swagger.py                # Swagger template and OpenAPI specifications
├── migrations/                   # Alembic database migration scripts
│   └── versions/
├── .env.example                  # Environment variable template
├── requirements.txt              # Project dependencies and pinned versions
└── run.py                        # Application entry point
```

---

## 5. Prerequisites

- **Python**: `3.10` or higher (tested with `3.13.15`).
- **PostgreSQL**: `14+` (local server or cloud database such as Neon, Supabase, or Render).
- **pip**: Python package manager.
- **Virtual Environment**: `venv` module.

---

## 6. Setup & Installation

### 1. Navigate to Backend Directory
```powershell
cd backend
```

### 2. Create and Activate Virtual Environment
- **Windows (PowerShell)**:
  ```powershell
  python -m venv .venv
  .\.venv\Scripts\Activate.ps1
  ```
- **Windows (CMD)**:
  ```cmd
  python -m venv .venv
  .\.venv\Scripts\activate.bat
  ```
- **Linux / macOS**:
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```

### 3. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env` and fill in your database credentials:
```powershell
cp .env.example .env
```

### 5. Run Database Migrations
```powershell
flask db upgrade
```

### 6. Start Development Server
```powershell
python run.py
```
The API starts at:
```text
http://127.0.0.1:5000
```

---

## 7. Configuration

Environment variables are loaded from `.env` via `python-dotenv`:

```env
FLASK_APP=run.py
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=your-super-secret-jwt-key-here
DATABASE_URL=postgresql://username:password@localhost:5432/jeebly_db
PORT=5000
UPLOAD_FOLDER=app/static/uploads/riders
MAX_CONTENT_LENGTH=5242880
```

- **`SECRET_KEY`**: Cryptographic secret used for signing JWT access tokens.
- **`DATABASE_URL`**: PostgreSQL connection string. The app automatically normalizes `postgres://` to `postgresql://` for SQLAlchemy 2.0+ compatibility.
- **`MAX_CONTENT_LENGTH`**: Maximum allowed request payload size (set to 5 MB for photo uploads).

---

## 8. API Documentation

Interactive Swagger UI is available at:
```text
http://127.0.0.1:5000/docs
```
OpenAPI specification JSON:
```text
http://127.0.0.1:5000/apispec.json
```

### Core API Endpoints

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/auth/register` | Register a new user account | No |
| `POST` | `/api/auth/login` | Authenticate user and issue JWT | No |
| `GET` | `/api/dashboard/stats` | Operational KPIs and fleet distribution | Yes |
| `GET` | `/api/riders` | Paginated riders with search and filters | Yes |
| `POST` | `/api/riders` | Create new rider with optional photo | Yes |
| `GET` | `/api/riders/<id>` | Retrieve specific rider details | Yes |
| `PUT` | `/api/riders/<id>` | Update rider info or photo | Yes |
| `DELETE` | `/api/riders/<id>` | Delete a rider record | Yes |
| `GET` | `/api/orders` | Paginated orders with multi-criteria filters | Yes |
| `POST` | `/api/orders` | Create a delivery order | Yes |
| `PUT` | `/api/orders/<id>` | Update order status or assign rider | Yes |
| `DELETE` | `/api/orders/<id>` | Delete an order record | Yes |
| `GET` | `/api/profile` | Retrieve authenticated user profile | Yes |
| `PUT` | `/api/profile` | Update profile name and phone | Yes |
| `POST` | `/api/profile/change-password` | Update account password with verification | Yes |

---

## 9. Database

- **Database Engine**: PostgreSQL via `psycopg2-binary`.
- **Migration Engine**: Alembic managed through `Flask-Migrate`.

### Core Tables
1. **`user`**: Stores administrative credentials, roles, and profile information (`id`, `name`, `email` [unique], `password_hash`, `phone`, `role`, `created_at`).
2. **`rider`**: Tracks fleet members, availability, and documents (`id`, `name`, `email` [unique], `phone`, `vehicle_type`, `status`, `availability`, `rating`, `photo_url`, `created_at`). Includes composite index on `(status, availability)`.
3. **`order`**: Manages delivery packages and dispatch assignments (`id`, `order_number` [unique], `customer_name`, `customer_phone`, `delivery_address`, `pickup_address`, `amount`, `status`, `rider_id` [FK -> `rider.id`], `created_at`, `updated_at`). Includes composite index on `(rider_id, status)`.

### Migration Commands
```powershell
flask db migrate -m "Migration description"   # Generate migration script
flask db upgrade                              # Apply pending migrations
flask db downgrade                            # Roll back the most recent migration
```

---

## 10. Implemented Concepts

- **5-Layer Architecture**: Clean separation of responsibilities within each module:
  - `routes.py`: Flask Blueprint route declarations and HTTP method bindings.
  - `controllers.py`: Request payload extraction, schema validation calls, and HTTP status handling.
  - `services.py`: Business rules, validation logic, and transactional orchestration.
  - `repositories.py`: SQLAlchemy database queries, joins, filtering, and persistence.
  - `schemas.py`: Marshmallow schema definitions for input validation and output serialization.
- **Application Factory Pattern**: `create_app()` dynamically registers blueprints, binds database extensions, registers global error handlers, and configures Swagger.
- **JWT Authentication (`@auth_required`)**: Custom decorator validates `Authorization: Bearer <token>`, decodes claims, verifies expiration, and injects the current user into controller functions.
- **Standardized API Responses**: `api_response()` and `error_response()` enforce a consistent JSON structure across all endpoints (`{ "success": true/false, "data": ..., "message": ... }`).
- **Global Error Handling**: Custom handlers catch `400`, `401`, `403`, `404`, and `500` errors, returning structured JSON rather than default HTML pages.

---

## 11. Common Issues & Solutions

### 1. PostgreSQL URI Deprecation
- **Problem**: Cloud providers (like Render) expose `DATABASE_URL` starting with `postgres://`, which SQLAlchemy 2.0+ rejects (`NoSuchModuleError: Can't load plugin: sqlalchemy.dialects:postgres`).
- **Solution**: Implemented URI normalization in `config.py` that automatically transforms `postgres://` to `postgresql://`.

### 2. Transaction Rollback on Error
- **Problem**: If an unhandled exception occurred mid-transaction, subsequent queries on the same session failed with `PendingRollbackError`.
- **Solution**: Encapsulated database operations with explicit `db.session.rollback()` in exception blocks across services and repositories.

### 3. N+1 Query on Order Listing
- **Problem**: Loading orders and then accessing rider names in loops triggered individual SQL queries per record.
- **Solution**: Utilized `joinedload(Order.rider)` in `OrderRepository` for eager SQL join fetching in a single query.

### 4. Upload Directory Permissions on Startup
- **Problem**: File uploads failed with `FileNotFoundError` when deploying to fresh server environments.
- **Solution**: Added `os.makedirs(upload_folder, exist_ok=True)` inside `create_app()` to ensure storage directories exist before receiving requests.
