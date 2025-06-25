from marshmallow import fields, Schema, validate, validates_schema, ValidationError, EXCLUDE


class UserSchema(Schema):
    id = fields.String()
    username = fields.String()
    email = fields.String()

class AddOrderSchema(Schema):
    id = fields.Int(dump_only=True)
    fullName = fields.Str(required=True, validate=validate.Length(min=5))
    phone = fields.Str(required=True, validate=validate.Length(min=10))
    anotherPhone = fields.Str(required=True)
    price = fields.Float(required=True)
    minGuests = fields.Int(required=True)
    maxGuests = fields.Int(required=True)
    date = fields.Date(required=True, format='iso')
    startTime = fields.Str(required=True)
    endTime = fields.Str(required=True)
    orderAmount = fields.Float(required=True)
    paidAmount = fields.Float(required=True)
    orderType = fields.Str(required=True)
    comments = fields.Str(allow_none=True)

    @validates_schema
    def validate_guests(self, data, **kwargs):
        if data['minGuests'] > data['maxGuests']:
            raise ValidationError("minGuests cannot be greater than maxGuests", field_name="minGuests")

class GetOrderSchema(Schema):
    id = fields.String()
    full_name = fields.String()
    phone = fields.String()
    another_phone = fields.String(allow_none=True)
    price = fields.Float()
    min_guests = fields.Integer()
    max_guests = fields.Integer()
    date = fields.Date()
    start_time = fields.String()
    end_time = fields.String()
    order_amount = fields.Float()
    paid_amount = fields.Float()
    order_type = fields.String()
    comments = fields.String(allow_none=True)

class GetOrderNonAdminSchema(Schema):
    id = fields.String()
    full_name = fields.String()
    phone = fields.String()
    another_phone = fields.String(allow_none=True)
    min_guests = fields.Integer()
    max_guests = fields.Integer()
    date = fields.Date()
    start_time = fields.String()
    end_time = fields.String()
    order_type = fields.String()
    comments = fields.String(allow_none=True)

class GetOrderByDatesInputSchema(Schema):
    startDate = fields.Date()
    endDate = fields.Date()

class DeactivateOrderSchema(Schema):
    id = fields.String(required=True)
    class Meta:
        unknown = EXCLUDE

class UpdateOrderSchema(Schema):
    id = fields.String(required=True)
    fullName = fields.Str(required=True, validate=validate.Length(min=5))
    phone = fields.Str(required=True, validate=validate.Length(min=10))
    anotherPhone = fields.Str(required=True)
    price = fields.Float(required=True)
    minGuests = fields.Int(required=True)
    maxGuests = fields.Int(required=True)
    date = fields.Date(required=True, format='iso')
    startTime = fields.Str(required=True)
    endTime = fields.Str(required=True)
    orderAmount = fields.Float(required=True)
    paidAmount = fields.Float(required=True)
    orderType = fields.Str(required=True)
    comments = fields.Str(allow_none=True)

    @validates_schema
    def validate_guests(self, data, **kwargs):
        if data['minGuests'] > data['maxGuests']:
            raise ValidationError("minGuests cannot be greater than maxGuests", field_name="minGuests")