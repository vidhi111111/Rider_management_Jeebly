from flask import Blueprint
from ...common.middleware import auth_required
from .controllers import OrderController

orders_bp = Blueprint("orders", __name__)
controller = OrderController()


@orders_bp.get("/orders/export")
@auth_required
def export_orders():
    return controller.export()


@orders_bp.get("/orders")
@auth_required
def orders():
    """
    Get paginated orders list
    ---
    tags:
      - orders
    summary: Retrieve paginated and filtered orders
    description: Retrieves a paginated list of delivery orders. Supports filtering by search keyword across customer name, mobile, pickup, or delivery location, status filter, assigned rider filter, order date filter (YYYY-MM-DD), and sorting. Requires JWT Bearer authorization.
    operationId: orders_list
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
        description: Search keyword matching customer name, mobile, pickup, or delivery
      - name: status
        in: query
        type: string
        required: false
        enum:
          - pending
          - accepted
          - picked_up
          - in_transit
          - delivered
          - cancelled
        description: Filter orders by current status
      - name: rider_id
        in: query
        type: integer
        required: false
        description: Filter orders assigned to a specific rider ID
      - name: order_date
        in: query
        type: string
        format: date
        required: false
        description: Filter orders created on a specific date in YYYY-MM-DD format
      - name: sortBy
        in: query
        type: string
        required: false
        default: "newest"
        enum:
          - newest
          - oldest
          - amount_high
          - amount_low
          - customer_name
        description: Ordering sort criteria
    responses:
      200:
        description: Orders retrieved successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: "Orders retrieved successfully."
            data:
              type: object
              properties:
                orders:
                  type: array
                  items:
                    $ref: '#/definitions/Order'
                page:
                  type: integer
                  example: 1
                pageSize:
                  type: integer
                  example: 10
                totalRecords:
                  type: integer
                  example: 50
                totalPages:
                  type: integer
                  example: 5
      400:
        description: Bad request (e.g. invalid order_date format)
        schema:
          $ref: '#/definitions/ErrorResponse'
      401:
        description: Unauthorized (Missing, invalid, or expired Bearer token)
        schema:
          $ref: '#/definitions/ErrorResponse'
      500:
        description: Internal server or database error
        schema:
          $ref: '#/definitions/ErrorResponse'
    """
    return controller.get_orders()


@orders_bp.post("/orders")
@auth_required
def create_order():
    """
    Create a new order
    ---
    tags:
      - orders
    summary: Create a delivery order
    description: Creates a new delivery order. Customer name is required (max 100 characters). Mobile (max 20 chars), pickup address (max 255 chars), delivery address (max 255 chars), amount (non-negative float), and currency (defaults to 'AED') are optional. The new order starts with 'pending' status. Requires JWT Bearer authorization.
    operationId: orders_create
    security:
      - Bearer: []
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        description: Order creation payload
        schema:
          $ref: '#/definitions/OrderCreateRequest'
    responses:
      201:
        description: Order created successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: "Order created successfully."
            data:
              $ref: '#/definitions/Order'
      400:
        description: Validation failed (e.g. missing customer_name or negative amount)
        schema:
          $ref: '#/definitions/ErrorResponse'
      401:
        description: Unauthorized (Missing, invalid, or expired Bearer token)
        schema:
          $ref: '#/definitions/ErrorResponse'
      500:
        description: Internal server or database error
        schema:
          $ref: '#/definitions/ErrorResponse'
    """
    return controller.create_order()


@orders_bp.get("/orders/<int:order_id>")
@auth_required
def get_order(order_id):
    """
    Get order by ID
    ---
    tags:
      - orders
    summary: Retrieve details of a specific order
    description: Retrieves full details of a single order by its unique integer ID, including assigned rider information if a rider has been assigned. Requires JWT Bearer authorization.
    operationId: orders_get_by_id
    security:
      - Bearer: []
    produces:
      - application/json
    parameters:
      - name: order_id
        in: path
        type: integer
        required: true
        description: Unique integer ID of the order
    responses:
      200:
        description: Order details retrieved successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: "Order details retrieved successfully."
            data:
              $ref: '#/definitions/Order'
      401:
        description: Unauthorized (Missing, invalid, or expired Bearer token)
        schema:
          $ref: '#/definitions/ErrorResponse'
      404:
        description: Order not found
        schema:
          $ref: '#/definitions/ErrorResponse'
      500:
        description: Internal server or database error
        schema:
          $ref: '#/definitions/ErrorResponse'
    """
    return controller.get_order(order_id)


@orders_bp.put("/orders/<int:order_id>")
@auth_required
def update_order(order_id):
    """
    Update an existing order
    ---
    tags:
      - orders
    summary: Update delivery order details
    description: Updates customer, address, and amount details of an existing order. Orders in terminal status ('delivered', 'cancelled', 'completed') cannot be edited. Requires JWT Bearer authorization.
    operationId: orders_update
    security:
      - Bearer: []
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - name: order_id
        in: path
        type: integer
        required: true
        description: Unique integer ID of the order to update
      - in: body
        name: body
        required: true
        description: Order update payload
        schema:
          $ref: '#/definitions/OrderCreateRequest'
    responses:
      200:
        description: Order updated successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: "Order updated successfully."
            data:
              $ref: '#/definitions/Order'
      400:
        description: Validation failed
        schema:
          $ref: '#/definitions/ErrorResponse'
      401:
        description: Unauthorized (Missing, invalid, or expired Bearer token)
        schema:
          $ref: '#/definitions/ErrorResponse'
      404:
        description: Order not found
        schema:
          $ref: '#/definitions/ErrorResponse'
      409:
        description: Conflict - Delivered or cancelled orders cannot be edited
        schema:
          $ref: '#/definitions/ErrorResponse'
      500:
        description: Internal server or database error
        schema:
          $ref: '#/definitions/ErrorResponse'
    """
    return controller.update_order(order_id)


@orders_bp.patch("/orders/<int:order_id>/status")
@auth_required
def update_order_status(order_id):
    """
    Update order status
    ---
    tags:
      - orders
    summary: Advance order through lifecycle transitions
    description: Advances the status of an order along the strictly permitted lifecycle transitions (pending -> accepted -> picked_up -> in_transit -> delivered, or cancelled from any active state). Delivered and cancelled orders cannot be altered. Automatically sets assigned rider to available when order reaches a terminal state. Requires JWT Bearer authorization.
    operationId: orders_update_status
    security:
      - Bearer: []
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - name: order_id
        in: path
        type: integer
        required: true
        description: Unique integer ID of the order
      - in: body
        name: body
        required: true
        description: Status transition payload
        schema:
          $ref: '#/definitions/OrderStatusUpdateRequest'
    responses:
      200:
        description: Order status updated successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: "Order status updated successfully."
            data:
              $ref: '#/definitions/Order'
      400:
        description: Bad request (invalid status or missing body)
        schema:
          $ref: '#/definitions/ErrorResponse'
      401:
        description: Unauthorized (Missing, invalid, or expired Bearer token)
        schema:
          $ref: '#/definitions/ErrorResponse'
      404:
        description: Order not found
        schema:
          $ref: '#/definitions/ErrorResponse'
      409:
        description: Conflict - Invalid status transition or order is in a terminal status
        schema:
          $ref: '#/definitions/ErrorResponse'
      500:
        description: Internal server or database error
        schema:
          $ref: '#/definitions/ErrorResponse'
    """
    return controller.update_order_status(order_id)


@orders_bp.post("/orders/<int:order_id>/assign-rider")
@orders_bp.patch("/orders/<int:order_id>/assign-rider")
@auth_required
def assign_rider(order_id):
    """
    Assign or unassign rider to order
    ---
    tags:
      - orders
    summary: Assign or unassign a delivery rider (POST & PATCH)
    description: Assigns an eligible available rider to the order, or unassigns the rider when rider_id is null. Validates that the rider is available and not currently assigned to another active order. Updates the newly assigned rider's status to 'on_order' and availability to 'busy'. Automatically refreshes the availability status of any previously assigned rider. Both POST and PATCH HTTP methods are supported at this exact URL. Delivered or cancelled orders cannot be assigned a rider. Requires JWT Bearer authorization.
    operationId: orders_assign_rider
    security:
      - Bearer: []
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - name: order_id
        in: path
        type: integer
        required: true
        description: Unique integer ID of the order
      - in: body
        name: body
        required: true
        description: Assignment payload containing rider_id integer or null
        schema:
          $ref: '#/definitions/OrderAssignRiderRequest'
    responses:
      200:
        description: Order rider assignment updated successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: "Order assignment updated successfully."
            data:
              $ref: '#/definitions/Order'
      400:
        description: Bad request (invalid rider ID or missing rider_id field)
        schema:
          $ref: '#/definitions/ErrorResponse'
      401:
        description: Unauthorized (Missing, invalid, or expired Bearer token)
        schema:
          $ref: '#/definitions/ErrorResponse'
      404:
        description: Order or Rider not found
        schema:
          $ref: '#/definitions/ErrorResponse'
      409:
        description: Conflict - Rider not eligible, unavailable, already busy with another order, or order terminal
        schema:
          $ref: '#/definitions/ErrorResponse'
      500:
        description: Internal server or database error
        schema:
          $ref: '#/definitions/ErrorResponse'
    """
    return controller.assign_rider(order_id)


@orders_bp.delete("/orders/<int:order_id>")
@auth_required
def delete_order(order_id):
    """
    Delete an order
    ---
    tags:
      - orders
    summary: Delete order by ID
    description: Permanently deletes the order and recalculates the availability status of the previously assigned rider if one was assigned. Requires JWT Bearer authorization.
    operationId: orders_delete
    security:
      - Bearer: []
    produces:
      - application/json
    parameters:
      - name: order_id
        in: path
        type: integer
        required: true
        description: Unique integer ID of the order to delete
    responses:
      200:
        description: Order deleted successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: "Order deleted successfully."
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
        description: Order not found
        schema:
          $ref: '#/definitions/ErrorResponse'
      500:
        description: Internal server or database error
        schema:
          $ref: '#/definitions/ErrorResponse'
    """
    return controller.delete_order(order_id)
