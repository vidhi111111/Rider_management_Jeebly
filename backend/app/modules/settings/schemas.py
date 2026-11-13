from marshmallow import Schema, fields


class UserPreferencesSchema(Schema):
    notifications = fields.Boolean(load_default=True, dump_default=True)
    dark_mode = fields.Boolean(load_default=True, dump_default=True)


class SettingsResponseSchema(Schema):
    user_id = fields.Integer(dump_only=True)
    settings = fields.Nested(UserPreferencesSchema, dump_only=True)


settings_response_schema = SettingsResponseSchema()
