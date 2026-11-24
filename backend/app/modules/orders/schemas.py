import math
from typing import Dict, Any, Optional, Tuple
from marshmallow import Schema, fields, validate, validates, validates_schema, ValidationError
from ...common.utils import format_marshmallow_errors
from ..riders.schemas import RiderSchema, serialize_rider

ORDER_STATUSES = [
    "pending", "accepted", "picked_up", "in_transit",
    "delivered", "cancelled"
]

TERMINAL_STATUSES = {"delivered", "cancelled", "completed"}

ALLOWED_STATUS_TRANSITIONS = {
    "pending": {"accepted", "cancelled"},
    "accepted": {"picked_up", "cancelled"},
    "picked_up": {"in_transit", "cancelled"},
    "in_transit": {"delivered", "cancelled"},
}


class OrderCreateSchema(Schema):
    customer_name = fields.String(
        required=True,
        error_messages={"required": "Customer name is required."}
    )
    mobile = fields.String(
        required=True,
        error_messages={"required": "Customer mobile number is required."}
    )
    pickup = fields.String(
        required=True,
        error_messages={"required": "Pickup location is required."}
    )
    delivery = fields.String(
        required=True,
        error_messages={"required": "Delivery destination is required."}
    )
    amount = fields.Raw(
        required=True,
        error_messages={"required": "Order amount is required."}
    )
    currency = fields.String(load_default="AED")

    @validates("customer_name")
    def validate_customer_name(self, value, **kwargs):
        stripped = str(value or "").strip()
        if not stripped:
            raise ValidationError("Customer name is required.")
        if len(stripped) > 100:
            raise ValidationError("Customer name cannot exceed 100 characters.")

    @validates("mobile")
    def validate_mobile(self, value, **kwargs):
        stripped = str(value or "").strip()
        if not stripped:
            raise ValidationError("Customer mobile number is required.")
        digits = "".join(filter(str.isdigit, stripped))
        if len(digits) < 7 or len(stripped) > 20:
            raise ValidationError("Mobile number must be a valid contact number (10 digits).")

    @validates("pickup")
    def validate_pickup(self, value, **kwargs):
        stripped = str(value or "").strip()
        if not stripped:
            raise ValidationError("Pickup location is required.")
        if len(stripped) > 255:
            raise ValidationError("Pickup address must not exceed 255 characters.")

    @validates("delivery")
    def validate_delivery(self, value, **kwargs):
        stripped = str(value or "").strip()
        if not stripped:
            raise ValidationError("Delivery destination is required.")
        if len(stripped) > 255:
            raise ValidationError("Delivery address must not exceed 255 characters.")

    @validates("currency")
    def validate_currency(self, value, **kwargs):
        stripped = str(value or "").strip().upper()
        if not stripped or len(stripped) > 10:
            raise ValidationError("Invalid currency.")

    @validates_schema(skip_on_field_errors=True)
    def clean_payload(self, data, **kwargs):
        data["customer_name"] = str(data.get("customer_name", "")).strip()
        data["mobile"] = str(data.get("mobile", "")).strip()
        data["pickup"] = str(data.get("pickup", "")).strip()
        data["delivery"] = str(data.get("delivery", "")).strip()

        currency = data.get("currency", "AED")
        data["currency"] = str(currency or "AED").strip().upper()

        amount_raw = data.get("amount")
        if amount_raw is not None and str(amount_raw).strip() != "":
            try:
                amt = float(amount_raw)
                if not math.isfinite(amt) or amt <= 0:
                    raise ValidationError("Amount must be greater than 0.", field_name="amount")
                data["amount"] = amt
            except (TypeError, ValueError):
                raise ValidationError("Amount must be a valid positive number.", field_name="amount")
        else:
            raise ValidationError("Order amount is required.", field_name="amount")


class OrderAssignRiderSchema(Schema):
    rider_id = fields.Integer(
        required=True,
        error_messages={"required": "rider_id is required."},
        validate=validate.Range(min=1, error="A valid rider ID is required.")
    )


class OrderStatusUpdateSchema(Schema):
    status = fields.String(
        required=True,
        validate=validate.OneOf(ORDER_STATUSES, error="Invalid order status.")
    )


class OrderSchema(Schema):
    id = fields.Integer(dump_only=True)
    customer_name = fields.String(dump_only=True)
    mobile = fields.String(dump_only=True)
    pickup = fields.String(dump_only=True)
    delivery = fields.String(dump_only=True)
    amount = fields.Method("get_amount", dump_only=True)
    currency = fields.String(dump_only=True)
    status = fields.String(dump_only=True)
    created_at = fields.Method("get_created_at", dump_only=True)
    rider_id = fields.Integer(dump_only=True)
    rider = fields.Nested(RiderSchema, dump_only=True)

    def get_amount(self, obj) -> Optional[float]:
        if hasattr(obj, "amount") and obj.amount is not None:
            return float(obj.amount)
        return None

    def get_created_at(self, obj) -> Optional[str]:
        if hasattr(obj, "created_at") and obj.created_at:
            return obj.created_at.isoformat()
        return None


# Singletons
order_create_schema = OrderCreateSchema()
order_assign_schema = OrderAssignRiderSchema()
order_status_schema = OrderStatusUpdateSchema()
order_schema = OrderSchema()
orders_list_schema = OrderSchema(many=True)


def serialize_order(order) -> Optional[Dict[str, Any]]:
    """Serialize an Order model instance using Marshmallow."""
    if order is None:
        return None
    return order_schema.dump(order)


def validate_order_payload(data: Dict[str, Any], is_update: bool = False, existing_order=None) -> Tuple[bool, Optional[str], Dict[str, Any]]:
    """
    Validate order payload with Marshmallow OrderCreateSchema.
    Maintains exact error signature expected by callers: (is_valid, error_message, cleaned_dict).
    """
    if not isinstance(data, dict):
        return False, "A valid JSON object is required.", {}

    merged = dict(data)
    if is_update and existing_order is not None:
        if "customer_name" not in merged or merged["customer_name"] is None:
            merged["customer_name"] = existing_order.customer_name
        if "mobile" not in merged or merged["mobile"] is None:
            merged["mobile"] = existing_order.mobile or ""
        if "pickup" not in merged or merged["pickup"] is None:
            merged["pickup"] = existing_order.pickup or ""
        if "delivery" not in merged or merged["delivery"] is None:
            merged["delivery"] = existing_order.delivery or ""
        if "amount" not in merged or merged["amount"] is None:
            merged["amount"] = existing_order.amount if existing_order.amount is not None else 1.0
        if "currency" not in merged or merged["currency"] is None:
            merged["currency"] = existing_order.currency or "AED"

    try:
        cleaned = order_create_schema.load(merged)
        return True, None, cleaned
    except ValidationError as err:
        formatted = format_marshmallow_errors(err.messages)
        # Return first error string for the simple error_response pattern
        first_error = next(iter(formatted.values())) if formatted else "Validation failed."
        return False, first_error, {}
