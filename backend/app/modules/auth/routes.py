from flask import Blueprint
from .controllers import AuthController

auth_bp = Blueprint("auth", __name__)
controller = AuthController()


@auth_bp.get("/health")
def health():
    """
    Service health check endpoint
    ---
    tags:
      - auth
    summary: Check API health status
    description: Verifies that the Flask application backend is online, healthy, and accessible. Public endpoint that does not require authentication.
    operationId: auth_health
    security: []
    produces:
      - application/json
    responses:
      200:
        description: API is online and healthy
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: "Flask API is running."
    """
    return controller.health()


@auth_bp.post("/register")
def register():
    """
    Register a new user account
    ---
    tags:
      - auth
    summary: Register new user
    description: Registers a new user in the system with name, email, mobile number, and password. Marshmallow validation enforces name between 2-100 characters, a valid email address (max 120 characters), exactly 10-digit mobile number, and password minimum 8 characters. Passwords are securely hashed using bcrypt. Public endpoint.
    operationId: auth_register
    security: []
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        description: User registration data
        schema:
          $ref: '#/definitions/RegisterRequest'
    responses:
      201:
        description: User successfully registered
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: "Registration successful."
            data:
              $ref: '#/definitions/User'
      400:
        description: Validation failed (e.g. invalid fields, missing fields, or empty JSON)
        schema:
          $ref: '#/definitions/ValidationErrorResponse'
      409:
        description: Conflict - Email or mobile number already registered
        schema:
          $ref: '#/definitions/ErrorResponse'
      415:
        description: Unsupported Media Type (Content-Type must be application/json)
        schema:
          $ref: '#/definitions/ErrorResponse'
      500:
        description: Database error occurred
        schema:
          $ref: '#/definitions/ErrorResponse'
    """
    return controller.register()


@auth_bp.post("/login")
def login():
    """
    User login and authentication
    ---
    tags:
      - auth
    summary: Authenticate user & issue JWT token
    description: Authenticates existing user with email and password credentials. On success, returns user details and a signed JWT Bearer access token valid for 2 hours with HS256 algorithm. Public endpoint.
    operationId: auth_login
    security: []
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        description: User login credentials
        schema:
          $ref: '#/definitions/LoginRequest'
    responses:
      200:
        description: Authentication successful
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: "Login successful."
            token:
              type: string
              example: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            user:
              $ref: '#/definitions/User'
      400:
        description: Bad request (missing email or password, invalid JSON)
        schema:
          $ref: '#/definitions/ErrorResponse'
      401:
        description: Unauthorized (Invalid email or password)
        schema:
          $ref: '#/definitions/ErrorResponse'
      415:
        description: Unsupported Media Type (Content-Type must be application/json)
        schema:
          $ref: '#/definitions/ErrorResponse'
    """
    return controller.login()


@auth_bp.post("/google")
def google_login():
    """
    Authenticate user via Google ID Token
    ---
    tags:
      - auth
    summary: Authenticate user using Google Sign-In & issue JWT token
    description: Verifies Google OAuth2 ID token, finds or creates user account, and returns signed JWT token.
    operationId: auth_google_login
    security: []
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        description: Google credential token
        schema:
          type: object
          required:
            - credential
          properties:
            credential:
              type: string
    responses:
      200:
        description: Google authentication successful
      400:
        description: Invalid token
    """
    return controller.google_login()
