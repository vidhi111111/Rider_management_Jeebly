"""
Swagger configuration and initialization for the Delivery Management API.
Centrally configures Flasgger, UI routes, security schemes, and reusable definitions.
"""

from flask import Flask, redirect
from flasgger import Swagger

SWAGGER_CONFIG = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec",
            "route": "/apispec.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs",
}

SWAGGER_TEMPLATE = {
    "swagger": "2.0",
    "info": {
        "title": "Jeebly Rider Management API",
        "description": (
            "API documentation for the Rider Management System,"
            " featuring authentication, dashboard metrics, rider "
            "fleet management, order dispatch, and user profile management."
        ),
        "version": "1.0.0",
        "contact": {
            "name": "API Support Team",
        },
    },
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": (
                "JWT Authorization header using the Bearer scheme. Enter 'Bearer ' followed by "
                "your JWT access token obtained from the POST /login endpoint. Example: "
                "'Bearer eyJhbGciOiJIUzI1Ni...'"
            ),
        }
    },
    "tags": [
        {
            "name": "auth",
            "description": "Authentication and Health Check endpoints (3 endpoints)",
        },
        {
            "name": "dashboard",
            "description": "Dashboard analytics and operational overview endpoints (1 endpoint)",
        },
        {
            "name": "riders",
            "description": "Rider management, filtering, and profile upload endpoints (7 endpoints)",
        },
        {
            "name": "orders",
            "description": "Order management, lifecycle transitions, and rider assignment endpoints (8 endpoints)",
        },
        {
            "name": "profile",
            "description": "User profile retrieval, updates, and password change endpoints (3 endpoints)",
        },
        {
            "name": "settings",
            "description": "User application settings and preferences endpoints (1 endpoint)",
        },
    ],
    "definitions": {
        "SuccessResponse": {
            "type": "object",
            "required": ["success", "message"],
            "properties": {
                "success": {
                    "type": "boolean",
                    "example": True,
                    "description": "Indicates whether the operation succeeded",
                },
                "message": {
                    "type": "string",
                    "example": "Operation completed successfully.",
                    "description": "Human-readable response message",
                },
            },
        },
        "ErrorResponse": {
            "type": "object",
            "required": ["success", "message"],
            "properties": {
                "success": {
                    "type": "boolean",
                    "example": False,
                    "description": "Always false for error responses",
                },
                "message": {
                    "type": "string",
                    "example": "An error occurred while processing the request.",
                    "description": "Error description message",
                },
            },
        },
        "ValidationErrorResponse": {
            "type": "object",
            "required": ["success", "message", "errors"],
            "properties": {
                "success": {
                    "type": "boolean",
                    "example": False,
                },
                "message": {
                    "type": "string",
                    "example": "Validation failed.",
                },
                "errors": {
                    "type": "object",
                    "description": "Key-value mapping of field names to validation error messages",
                    "additionalProperties": {
                        "type": "string",
                    },
                    "example": {
                        "mobile": "Mobile number must contain exactly 10 digits.",
                        "email": "Please provide a valid email address.",
                    },
                },
            },
        },
        "User": {
            "type": "object",
            "properties": {
                "id": {
                    "type": "integer",
                    "example": 1,
                    "description": "Unique user identifier",
                },
                "name": {
                    "type": "string",
                    "example": "John Doe",
                    "description": "User full name",
                },
                "email": {
                    "type": "string",
                    "format": "email",
                    "example": "john.doe@example.com",
                    "description": "Registered email address",
                },
                "mobile": {
                    "type": "string",
                    "example": "9876543210",
                    "description": "10-digit mobile phone number",
                },
            },
        },
        "Rider": {
            "type": "object",
            "properties": {
                "id": {
                    "type": "integer",
                    "example": 1,
                    "description": "Unique rider identifier",
                },
                "name": {
                    "type": "string",
                    "example": "Alex Smith",
                    "description": "Rider full name (2 to 100 characters)",
                },
                "mobile": {
                    "type": "string",
                    "example": "9876543210",
                    "description": "10-digit mobile number",
                },
                "email": {
                    "type": "string",
                    "format": "email",
                    "example": "alex.smith@example.com",
                    "description": "Rider contact email",
                },
                "vehicle": {
                    "type": "string",
                    "example": "Honda PCX 150",
                    "description": "Assigned delivery vehicle",
                },
                "status": {
                    "type": "string",
                    "enum": [
                        "active",
                        "inactive",
                        "available",
                        "on_order",
                        "scheduled_break",
                        "absent",
                    ],
                    "example": "active",
                    "description": "Operational status of rider",
                },
                "availability": {
                    "type": "string",
                    "enum": ["available", "busy", "unavailable"],
                    "example": "available",
                    "description": "Real-time dispatch availability status",
                },
                "date": {
                    "type": "string",
                    "format": "date",
                    "example": "2026-11-17",
                    "description": "Registration date (YYYY-MM-DD)",
                },
                "profile_image": {
                    "type": "string",
                    "x-nullable": True,
                    "example": "http://127.0.0.1:5000/rider-uploads/rider_1.jpg",
                    "description": "URL to profile photo or null if none uploaded",
                },
            },
        },
        "Order": {
            "type": "object",
            "properties": {
                "id": {
                    "type": "integer",
                    "example": 101,
                    "description": "Unique order identifier",
                },
                "customer_name": {
                    "type": "string",
                    "example": "Jane Smith",
                    "description": "Customer full name",
                },
                "mobile": {
                    "type": "string",
                    "x-nullable": True,
                    "example": "0501234567",
                    "description": "Customer contact mobile",
                },
                "pickup": {
                    "type": "string",
                    "x-nullable": True,
                    "example": "Dubai Mall, Downtown",
                    "description": "Pickup location address",
                },
                "delivery": {
                    "type": "string",
                    "x-nullable": True,
                    "example": "Business Bay Tower B, Apt 304",
                    "description": "Delivery destination address",
                },
                "amount": {
                    "type": "number",
                    "format": "float",
                    "x-nullable": True,
                    "example": 75.50,
                    "description": "Order financial amount",
                },
                "currency": {
                    "type": "string",
                    "example": "AED",
                    "description": "Currency code (default: AED)",
                },
                "status": {
                    "type": "string",
                    "enum": [
                        "pending",
                        "accepted",
                        "picked_up",
                        "in_transit",
                        "delivered",
                        "cancelled",
                    ],
                    "example": "pending",
                    "description": "Current order lifecycle status",
                },
                "created_at": {
                    "type": "string",
                    "format": "date-time",
                    "example": "2026-11-17T10:30:00Z",
                    "description": "ISO 8601 UTC creation timestamp",
                },
                "rider_id": {
                    "type": "integer",
                    "x-nullable": True,
                    "example": 1,
                    "description": "Assigned rider identifier or null",
                },
                "rider": {
                    "$ref": "#/definitions/Rider",
                    "description": "Detailed rider object if assigned, else null",
                },
            },
        },
        "DashboardSummary": {
            "type": "object",
            "properties": {
                "total_orders": {"type": "integer", "example": 25},
                "delivered_orders": {"type": "integer", "example": 15},
                "cancelled_orders": {"type": "integer", "example": 2},
                "in_progress_orders": {"type": "integer", "example": 8},
            },
        },
        "DashboardRiderSummary": {
            "type": "object",
            "properties": {
                "total": {"type": "integer", "example": 10},
                "active": {"type": "integer", "example": 7},
                "available": {"type": "integer", "example": 5},
                "busy": {"type": "integer", "example": 2},
            },
        },
        "DashboardRecentOrder": {
            "type": "object",
            "properties": {
                "id": {"type": "integer", "example": 101},
                "status": {"type": "string", "example": "pending"},
                "customer": {"type": "string", "example": "Jane Smith"},
                "created_at": {"type": "string", "example": "2026-11-17T10:30:00Z"},
                "rider_id": {"type": "integer", "x-nullable": True, "example": 1},
            },
        },
        "DashboardData": {
            "type": "object",
            "properties": {
                "summary": {"$ref": "#/definitions/DashboardSummary"},
                "rider_summary": {"$ref": "#/definitions/DashboardRiderSummary"},
                "recent_orders": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/DashboardRecentOrder"},
                },
                "available_riders": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/Rider"},
                },
            },
        },
        "UserPreferences": {
            "type": "object",
            "properties": {
                "notifications": {"type": "boolean", "example": True},
                "dark_mode": {"type": "boolean", "example": True},
            },
        },
        "SettingsData": {
            "type": "object",
            "properties": {
                "user_id": {"type": "integer", "example": 1},
                "settings": {"$ref": "#/definitions/UserPreferences"},
            },
        },
        "RegisterRequest": {
            "type": "object",
            "required": ["name", "email", "mobile", "password"],
            "properties": {
                "name": {
                    "type": "string",
                    "minLength": 2,
                    "maxLength": 100,
                    "example": "John Doe",
                    "description": "Full name (2-100 characters)",
                },
                "email": {
                    "type": "string",
                    "format": "email",
                    "maxLength": 120,
                    "example": "john.doe@example.com",
                    "description": "Valid email address",
                },
                "mobile": {
                    "type": "string",
                    "pattern": "^[0-9]{10}$",
                    "example": "9876543210",
                    "description": "Exactly 10 digits",
                },
                "password": {
                    "type": "string",
                    "format": "password",
                    "minLength": 8,
                    "example": "Password123!",
                    "description": "Password (minimum 8 characters)",
                },
            },
        },
        "LoginRequest": {
            "type": "object",
            "required": ["email", "password"],
            "properties": {
                "email": {
                    "type": "string",
                    "format": "email",
                    "example": "john.doe@example.com",
                    "description": "Registered email",
                },
                "password": {
                    "type": "string",
                    "format": "password",
                    "example": "Password123!",
                    "description": "Account password",
                },
            },
        },
        "OrderCreateRequest": {
            "type": "object",
            "required": ["customer_name"],
            "properties": {
                "customer_name": {
                    "type": "string",
                    "maxLength": 100,
                    "example": "Jane Smith",
                    "description": "Customer full name (required, max 100 chars)",
                },
                "mobile": {
                    "type": "string",
                    "maxLength": 20,
                    "example": "0501234567",
                    "description": "Customer mobile (optional, max 20 chars)",
                },
                "pickup": {
                    "type": "string",
                    "maxLength": 255,
                    "example": "Downtown Dubai Mall",
                    "description": "Pickup location (optional, max 255 chars)",
                },
                "delivery": {
                    "type": "string",
                    "maxLength": 255,
                    "example": "Business Bay Tower A",
                    "description": "Delivery address (optional, max 255 chars)",
                },
                "amount": {
                    "type": "number",
                    "format": "float",
                    "minimum": 0,
                    "example": 75.50,
                    "description": "Order amount (optional, non-negative float)",
                },
                "currency": {
                    "type": "string",
                    "maxLength": 10,
                    "default": "AED",
                    "example": "AED",
                    "description": "Currency code (optional, default: AED)",
                },
            },
        },
        "OrderStatusUpdateRequest": {
            "type": "object",
            "required": ["status"],
            "properties": {
                "status": {
                    "type": "string",
                    "enum": [
                        "pending",
                        "accepted",
                        "picked_up",
                        "in_transit",
                        "delivered",
                        "cancelled",
                    ],
                    "example": "accepted",
                    "description": "Target status in the allowed lifecycle transition",
                },
            },
        },
        "OrderAssignRiderRequest": {
            "type": "object",
            "properties": {
                "rider_id": {
                    "type": "integer",
                    "x-nullable": True,
                    "example": 1,
                    "description": "Integer ID of available rider, or null to unassign rider",
                },
            },
        },
        "UpdateProfileRequest": {
            "type": "object",
            "required": ["name", "mobile"],
            "properties": {
                "name": {
                    "type": "string",
                    "maxLength": 100,
                    "example": "John Doe",
                    "description": "Full name (required, max 100 chars)",
                },
                "mobile": {
                    "type": "string",
                    "pattern": "^[0-9]{10}$",
                    "example": "9876543210",
                    "description": "10-digit mobile number (required, exactly 10 digits)",
                },
            },
        },
        "ChangePasswordRequest": {
            "type": "object",
            "required": ["current_password", "new_password"],
            "properties": {
                "current_password": {
                    "type": "string",
                    "format": "password",
                    "example": "CurrentPassword123!",
                    "description": "Current account password",
                },
                "new_password": {
                    "type": "string",
                    "format": "password",
                    "minLength": 8,
                    "example": "NewSecurePassword456!",
                    "description": "New account password (min 8 chars)",
                },
            },
        },
    },
}


def init_swagger(app: Flask) -> Swagger:

    swagger = Swagger(app, config=SWAGGER_CONFIG, template=SWAGGER_TEMPLATE)

    # Provide automatic redirect from /docs/ to /docs for seamless browser navigation
    @app.route("/docs/")
    def docs_trailing_slash_redirect():
        return redirect("/docs")

    return swagger
