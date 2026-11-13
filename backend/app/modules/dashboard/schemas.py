from marshmallow import Schema, fields
from ..riders.schemas import RiderSchema


class OrderSummarySchema(Schema):
    total_orders = fields.Integer()
    delivered_orders = fields.Integer()
    cancelled_orders = fields.Integer()
    in_progress_orders = fields.Integer()


class RiderSummarySchema(Schema):
    total = fields.Integer()
    active = fields.Integer()
    available = fields.Integer()
    busy = fields.Integer()


class RecentOrderItemSchema(Schema):
    id = fields.Integer()
    status = fields.String()
    customer = fields.String()
    created_at = fields.String(allow_none=True)
    rider_id = fields.Integer(allow_none=True)


class DashboardDataSchema(Schema):
    summary = fields.Nested(OrderSummarySchema)
    rider_summary = fields.Nested(RiderSummarySchema)
    recent_orders = fields.List(fields.Nested(RecentOrderItemSchema))
    available_riders = fields.List(fields.Nested(RiderSchema))


dashboard_data_schema = DashboardDataSchema()
