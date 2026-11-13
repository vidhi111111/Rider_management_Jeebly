import os
from pathlib import Path
from dotenv import load_dotenv

# Search for .env in current folder, backend folder, and workspace root
current_dir = Path(__file__).resolve().parent
backend_dir = current_dir.parent
workspace_dir = backend_dir.parent

for candidate in [backend_dir / ".env", workspace_dir / ".env", Path(".env")]:
    if candidate.is_file():
        load_dotenv(candidate)
        break
else:
    load_dotenv()


class Config:
    """Base application configuration."""

    SECRET_KEY = os.getenv("SECRET_KEY", "default-fallback-dev-key")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    DATABASE_URL = os.getenv("DATABASE_URL")
    if DATABASE_URL:
        if DATABASE_URL.startswith("postgres://"):
            DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg2://", 1)
        elif DATABASE_URL.startswith("postgresql://"):
            DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        SQLALCHEMY_DATABASE_URI = "sqlite:///users.db"

    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:4200")

    # Cloudinary configs if provided
    CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
    CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
    CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")
