from flask import Blueprint
from ...common.middleware import auth_required
from .controllers import RiderController

riders_bp = Blueprint("riders", __name__)
controller = RiderController()


@riders_bp.get("/riders")
@auth_required
def riders():
    """
    Get paginated riders list
    ---
    tags:
      - riders
    summary: Retrieve paginated and filtered riders
    description: Retrieves a paginated list of riders with support for keyword search across name, mobile, email, and vehicle, filtering by status and availability, and field sorting. Requires JWT Bearer authorization.
    operationId: riders_list
    security:
      - Bearer: []
    produces:
      - application/json
    parameters:
      - name: page
        in: query
        type: integer
        required: false
        default: 1
        description: Page number (1-based index, minimum 1)
      - name: pageSize
        in: query
        type: integer
        required: false
        default: 10
        description: Items per page (minimum 1, maximum 100)
      - name: search
        in: query
        type: string
        required: false
        description: Case-insensitive search keyword matching rider name, mobile, email, or vehicle
      - name: status
        in: query
        type: string
        required: false
        enum:
          - active
          - inactive
          - available
          - on_order
          - scheduled_break
          - absent
        description: Filter riders by operational status
      - name: availability
        in: query
        type: string
        required: false
        enum:
          - available
          - busy
          - unavailable
        description: Filter riders by dispatch availability
      - name: sortBy
        in: query
        type: string
        required: false
        default: "id"
        enum:
          - id
          - name
          - email
          - mobile
          - status
          - availability
          - date
          - vehicle
        description: Field to sort results by
      - name: sortOrder
        in: query
        type: string
        required: false
        default: "asc"
        enum:
          - asc
          - desc
        description: Sort direction
    responses:
      200:
        description: Paginated riders retrieved successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: "Riders retrieved successfully."
            data:
              type: object
              properties:
                riders:
                  type: array
                  items:
                    $ref: '#/definitions/Rider'
                page:
                  type: integer
                  example: 1
                pageSize:
                  type: integer
                  example: 10
                totalRecords:
                  type: integer
                  example: 25
                totalPages:
                  type: integer
                  example: 3
      401:
        description: Unauthorized (Missing, invalid, or expired Bearer token)
        schema:
          $ref: '#/definitions/ErrorResponse'
      500:
        description: Internal server or database error
        schema:
          $ref: '#/definitions/ErrorResponse'
    """
    return controller.get_riders()


@riders_bp.get("/riders/available")
@auth_required
def available_riders():
    """
    Get available riders for order assignment
    ---
    tags:
      - riders
    summary: Retrieve all currently available riders
    description: Retrieves all active and available riders who have no currently active orders and can be assigned to new delivery tasks. Refreshes real-time availability before returning. Excludes riders who are inactive, absent, on scheduled break, or already on order. Requires JWT Bearer authorization.
    operationId: riders_available
    security:
      - Bearer: []
    produces:
      - application/json
    responses:
      200:
        description: Available riders retrieved successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: "Available riders retrieved successfully."
            data:
              type: object
              properties:
                riders:
                  type: array
                  items:
                    $ref: '#/definitions/Rider'
      401:
        description: Unauthorized (Missing, invalid, or expired Bearer token)
        schema:
          $ref: '#/definitions/ErrorResponse'
      500:
        description: Internal server or database error
        schema:
          $ref: '#/definitions/ErrorResponse'
    """
    return controller.get_available_riders()


@riders_bp.get("/riders/<int:rider_id>")
@auth_required
def get_rider(rider_id):
    """
    Get rider by ID
    ---
    tags:
      - riders
    summary: Retrieve detailed profile of a single rider
    description: Retrieves the complete profile details of a specific rider by their unique integer ID. Requires JWT Bearer authorization.
    operationId: riders_get_by_id
    security:
      - Bearer: []
    produces:
      - application/json
    parameters:
      - name: rider_id
        in: path
        type: integer
        required: true
        description: Unique integer ID of the rider
    responses:
      200:
        description: Rider details retrieved successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: "Rider retrieved successfully."
            data:
              $ref: '#/definitions/Rider'
      401:
        description: Unauthorized (Missing, invalid, or expired Bearer token)
        schema:
          $ref: '#/definitions/ErrorResponse'
      404:
        description: Rider not found
        schema:
          $ref: '#/definitions/ErrorResponse'
      500:
        description: Internal server or database error
        schema:
          $ref: '#/definitions/ErrorResponse'
    """
    return controller.get_rider(rider_id)


@riders_bp.post("/riders")
@auth_required
def create_rider():
    """
    Create a new rider
    ---
    tags:
      - riders
    summary: Register a new delivery rider
    description: Creates a new rider record in the system. Accepts multipart/form-data (to upload a profile photo file) or application/json. Validates input using Marshmallow RiderInputSchema - name (2-100 chars), mobile (exactly 10 digits), valid email (max 120 chars), vehicle (max 100 chars), and registration date (YYYY-MM-DD format). Requires JWT Bearer authorization.
    operationId: riders_create
    security:
      - Bearer: []
    consumes:
      - multipart/form-data
      - application/json
    produces:
      - application/json
    parameters:
      - name: name
        in: formData
        type: string
        required: true
        description: Rider full name (2 to 100 characters)
      - name: mobile
        in: formData
        type: string
        required: true
        description: Unique 10-digit mobile number
      - name: email
        in: formData
        type: string
        required: true
        description: Unique valid email address (max 120 characters)
      - name: vehicle
        in: formData
        type: string
        required: true
        description: Assigned vehicle description (max 100 characters)
      - name: status
        in: formData
        type: string
        required: false
        default: "active"
        enum:
          - active
          - inactive
          - available
          - on_order
          - scheduled_break
          - absent
        description: Operational status of the rider
      - name: availability
        in: formData
        type: string
        required: false
        default: "available"
        enum:
          - available
          - busy
          - unavailable
        description: Dispatch availability status
      - name: date
        in: formData
        type: string
        format: date
        required: true
        description: Registration date in YYYY-MM-DD format
      - name: profile_image
        in: formData
        type: file
        required: false
        description: Optional profile picture file (JPEG, PNG, GIF, WEBP, max 5MB)
    responses:
      201:
        description: Rider created successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: "Rider created successfully."
            data:
              $ref: '#/definitions/Rider'
      400:
        description: Validation failed or invalid image upload
        schema:
          $ref: '#/definitions/ValidationErrorResponse'
      401:
        description: Unauthorized (Missing, invalid, or expired Bearer token)
        schema:
          $ref: '#/definitions/ErrorResponse'
      409:
        description: Conflict - Mobile number or email already registered
        schema:
          $ref: '#/definitions/ErrorResponse'
      500:
        description: Internal server or database error
        schema:
          $ref: '#/definitions/ErrorResponse'
    """
    return controller.create_rider()


@riders_bp.put("/riders/<int:rider_id>")
@auth_required
def update_rider(rider_id):
    """
    Update an existing rider
    ---
    tags:
      - riders
    summary: Update rider profile details
    description: Updates profile information for an existing rider. Accepts multipart/form-data (to upload a new image or remove the existing image) or application/json. Validates fields using Marshmallow RiderInputSchema. Requires JWT Bearer authorization.
    operationId: riders_update
    security:
      - Bearer: []
    consumes:
      - multipart/form-data
      - application/json
    produces:
      - application/json
    parameters:
      - name: rider_id
        in: path
        type: integer
        required: true
        description: Unique integer ID of rider to update
      - name: name
        in: formData
        type: string
        required: true
        description: Rider full name (2 to 100 characters)
      - name: mobile
        in: formData
        type: string
        required: true
        description: Unique 10-digit mobile number
      - name: email
        in: formData
        type: string
        required: true
        description: Unique valid email address (max 120 characters)
      - name: vehicle
        in: formData
        type: string
        required: true
        description: Assigned vehicle description (max 100 characters)
      - name: status
        in: formData
        type: string
        required: false
        default: "active"
        enum:
          - active
          - inactive
          - available
          - on_order
          - scheduled_break
          - absent
        description: Operational status of the rider
      - name: availability
        in: formData
        type: string
        required: false
        default: "available"
        enum:
          - available
          - busy
          - unavailable
        description: Dispatch availability status
      - name: date
        in: formData
        type: string
        format: date
        required: true
        description: Registration date in YYYY-MM-DD format
      - name: profile_image
        in: formData
        type: file
        required: false
        description: Optional new profile picture file to upload
      - name: remove_photo
        in: formData
        type: boolean
        required: false
        default: false
        description: Set to true to delete current profile image
    responses:
      200:
        description: Rider updated successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: "Rider updated successfully."
            data:
              $ref: '#/definitions/Rider'
      400:
        description: Validation failed or invalid image upload
        schema:
          $ref: '#/definitions/ValidationErrorResponse'
      401:
        description: Unauthorized (Missing, invalid, or expired Bearer token)
        schema:
          $ref: '#/definitions/ErrorResponse'
      404:
        description: Rider not found
        schema:
          $ref: '#/definitions/ErrorResponse'
      409:
        description: Conflict - Mobile number or email already in use by another rider
        schema:
          $ref: '#/definitions/ErrorResponse'
      500:
        description: Internal server or database error
        schema:
          $ref: '#/definitions/ErrorResponse'
    """
    return controller.update_rider(rider_id)


@riders_bp.delete("/riders/<int:rider_id>")
@auth_required
def delete_rider(rider_id):
    """
    Delete a rider
    ---
    tags:
      - riders
    summary: Delete rider by ID
    description: Permanently deletes the rider record, unlinks any active or past orders assigned to this rider, and deletes any stored profile picture file. Requires JWT Bearer authorization.
    operationId: riders_delete
    security:
      - Bearer: []
    produces:
      - application/json
    parameters:
      - name: rider_id
        in: path
        type: integer
        required: true
        description: Unique integer ID of rider to delete
    responses:
      200:
        description: Rider deleted successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: "Rider deleted successfully."
            data:
              type: object
              properties:
                id:
                  type: integer
                  example: 1
      401:
        description: Unauthorized (Missing, invalid, or expired Bearer token)
        schema:
          $ref: '#/definitions/ErrorResponse'
      404:
        description: Rider not found
        schema:
          $ref: '#/definitions/ErrorResponse'
      500:
        description: Internal server or database error
        schema:
          $ref: '#/definitions/ErrorResponse'
    """
    return controller.delete_rider(rider_id)


@riders_bp.get("/rider-uploads/<path:filename>")
def rider_upload(filename):
    """
    Serve uploaded rider profile image
    ---
    tags:
      - riders
    summary: Download or view rider profile image file
    description: Public static file retrieval endpoint that serves uploaded rider profile photos directly from the server uploads directory. This route is public and does not require authentication.
    operationId: riders_upload_file
    security: []
    produces:
      - image/jpeg
      - image/png
      - image/webp
      - image/gif
    parameters:
      - name: filename
        in: path
        type: string
        required: true
        description: Filename of the stored rider image
    responses:
      200:
        description: Image file returned successfully
        schema:
          type: file
      404:
        description: Image file not found
        schema:
          $ref: '#/definitions/ErrorResponse'
    """
    return controller.serve_upload(filename)
