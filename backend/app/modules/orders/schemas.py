import math
from typing import Dict, Any, Optional, Tuple
from ..riders.schemas import serialize_rider

ORDER_STATUSES = {
    "pending", "accepted", "picked_up", "in_transit",
    "delivered", "cancelled"
}

TERMINAL_STATUSES = {"delivered", "cancelled", "completed"}

ALLOWED_STATUS_TRANSITIONS = {
    "pending": {"accepted", "cancelled"},
    "accepted": {"picked_up", "cancelled"},
    "picked_up": {"in_transit", "cancelled"},
    "in_transit": {"delivered", "cancelled"},
}


def serialize_order(order) -> Optional[Dict[str, Any]]:
    if order is None:
        return None

    return {
        "id": order.id,
        "customer_name": order.customer_name,
        "mobile": order.mobile,
        "pickup": order.pickup,
        "delivery": order.delivery,
        "amount": float(order.amount) if order.amount is not None else None,
        "currency": order.currency,
        "status": order.status,
        "created_at": (
            order.created_at.isoformat()
            if order.created_at else None
        ),
        "rider_id": order.rider_id,
        "rider": serialize_rider(order.rider) if order.rider else None
    }


def validate_order_payload(data: Dict[str, Any], is_update: bool = False, existing_order = None) -> Tuple[bool, Optional[str], Dict[str, Any]]:
    if not isinstance(data, dict):
        return False, "A valid JSON object is required.", {}

    if is_update and existing_order is not None:
        customer_name = str(data.get("customer_name", existing_order.customer_name) or "").strip()
        mobile = str(data.get("mobile", existing_order.mobile) or "").strip()
        pickup = str(data.get("pickup", existing_order.pickup) or "").strip()
        delivery = str(data.get("delivery", existing_order.delivery) or "").strip()
        currency = str(data.get("currency", existing_order.currency or "AED") or "").strip().upper()
        amount_raw = data.get("amount", existing_order.amount)
    else:
        customer_name = str(data.get("customer_name", "")).strip()
        mobile = str(data.get("mobile") or "").strip()
        pickup = str(data.get("pickup") or "").strip()
        delivery = str(data.get("delivery") or "").strip()
        currency = str(data.get("currency") or "AED").strip().upper()
        amount_raw = data.get("amount")

    if not customer_name:
        return False, "Customer name is required.", {}
    if len(customer_name) > 100:
        return False, "Customer name cannot exceed 100 characters.", {}
    if len(mobile) > 20:
        return False, "Mobile number cannot exceed 20 characters.", {}
    if len(pickup) > 255 or len(delivery) > 255:
        return False, "Pickup and delivery must not exceed 255 characters.", {}
    if not currency or len(currency) > 10:
        return False, "Invalid currency.", {}

    amount = None
    if amount_raw is not None:
        try:
            amount = float(amount_raw)
            if not math.isfinite(amount) or amount < 0:
                raise ValueError
        except (TypeError, ValueError):
            return False, "Amount must be a valid non-negative number.", {}

    return True, None, {
        "customer_name": customer_name,
        "mobile": mobile or None,
        "pickup": pickup or None,
        "delivery": delivery or None,
        "amount": amount,
        "currency": currency
    }
