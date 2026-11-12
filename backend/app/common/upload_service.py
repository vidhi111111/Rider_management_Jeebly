import os
import uuid
from pathlib import Path
from flask import current_app, url_for
from werkzeug.utils import secure_filename

ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
MAX_IMAGE_SIZE = 5 * 1024 * 1024


def cloudinary_enabled() -> bool:
    return bool(
        current_app.config.get("CLOUDINARY_CLOUD_NAME")
        or os.getenv("CLOUDINARY_CLOUD_NAME")
    )


def upload_rider_image(file):
    if not file or not file.filename:
        return None, None

    safe_name = secure_filename(file.filename)
    if not safe_name or "." not in safe_name:
        return None, "Invalid image filename."

    extension = safe_name.rsplit(".", 1)[1].lower()
    if extension not in ALLOWED_IMAGE_EXTENSIONS:
        return None, "Only JPG, JPEG, PNG and WEBP images are allowed."

    file.stream.seek(0, os.SEEK_END)
    size = file.stream.tell()
    file.stream.seek(0)

    if size == 0:
        return None, "The selected image is empty."
    if size > MAX_IMAGE_SIZE:
        return None, "Image size must not exceed 5 MB."

    if cloudinary_enabled():
        try:
            import cloudinary
            import cloudinary.uploader

            cloudinary.config(
                cloud_name=(
                    current_app.config.get("CLOUDINARY_CLOUD_NAME")
                    or os.getenv("CLOUDINARY_CLOUD_NAME")
                ),
                api_key=(
                    current_app.config.get("CLOUDINARY_API_KEY")
                    or os.getenv("CLOUDINARY_API_KEY")
                ),
                api_secret=(
                    current_app.config.get("CLOUDINARY_API_SECRET")
                    or os.getenv("CLOUDINARY_API_SECRET")
                ),
                secure=True
            )

            result = cloudinary.uploader.upload(
                file,
                folder="jeebly/riders",
                resource_type="image"
            )
            return {
                "url": result["secure_url"],
                "public_id": result["public_id"],
                "storage": "cloudinary"
            }, None

        except Exception:
            current_app.logger.exception("Cloudinary upload failed.")
            return None, "Unable to upload image to Cloudinary."

    # Local fallback when Cloudinary credentials are not configured.
    folder = Path(current_app.root_path) / "uploads"
    folder.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid.uuid4().hex}.{extension}"

    try:
        file.save(str(folder / filename))
    except OSError:
        current_app.logger.exception("Local image upload failed.")
        return None, "Unable to save uploaded image."

    # Attempt to resolve URL with routes.rider_upload or riders.rider_upload
    try:
        download_url = url_for("riders.rider_upload", filename=filename, _external=True)
    except Exception:
        download_url = url_for("routes.rider_upload", filename=filename, _external=True)

    return {
        "url": download_url,
        "public_id": filename,
        "storage": "local"
    }, None


def delete_rider_image(image_value):
    if not image_value:
        return

    # Existing records may contain a Cloudinary URL or local filename.
    value = str(image_value)

    if "res.cloudinary.com/" in value:
        try:
            import cloudinary
            import cloudinary.uploader

            cloudinary.config(
                cloud_name=(
                    current_app.config.get("CLOUDINARY_CLOUD_NAME")
                    or os.getenv("CLOUDINARY_CLOUD_NAME")
                ),
                api_key=(
                    current_app.config.get("CLOUDINARY_API_KEY")
                    or os.getenv("CLOUDINARY_API_KEY")
                ),
                api_secret=(
                    current_app.config.get("CLOUDINARY_API_SECRET")
                    or os.getenv("CLOUDINARY_API_SECRET")
                ),
                secure=True
            )

            current_app.logger.info(
                "Cloudinary image retained; store public_id to enable deletion."
            )
        except Exception:
            current_app.logger.exception("Cloudinary cleanup failed.")
        return

    filename = os.path.basename(value)
    folder = Path(current_app.root_path) / "uploads"

    try:
        path = folder / filename
        if path.is_file():
            path.unlink()
    except OSError:
        current_app.logger.exception("Unable to delete local rider image.")
