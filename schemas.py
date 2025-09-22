from marshmallow import fields, Schema, validate, validates_schema, ValidationError, EXCLUDE


class UserSchema(Schema):
    id = fields.String()
    username = fields.String()
    email = fields.String()

class AddOrderSchema(Schema):
    id = fields.Int(dump_only=True)
    fullName = fields.Str(required=True, validate=validate.Length(min=5))
    phone = fields.Str(required=True, validate=validate.Length(min=10))
    anotherPhone = fields.Str(required=False, allow_none=True)
    anotherName = fields.Str(required=False, allow_none=True)
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
    extras = fields.List(fields.Str(), required=False, allow_none=True)

    @validates_schema
    def validate_guests(self, data, **kwargs):
        if data['minGuests'] > data['maxGuests']:
            raise ValidationError("minGuests cannot be greater than maxGuests", field_name="minGuests")

class GetOrderSchema(Schema):
    id = fields.String()
    full_name = fields.String()
    phone = fields.String()
    another_phone = fields.String(allow_none=True)
    another_name = fields.String(allow_none=True)
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
    extras = fields.Method("get_extras")
    
    def get_extras(self, obj):
        if obj.extras:
            print(f"DEBUG SCHEMA - Raw extras from DB: {repr(obj.extras)}")
            try:
                import json
                # First try normal JSON parsing
                parsed = json.loads(obj.extras)
                print(f"DEBUG SCHEMA - Successfully parsed: {parsed}")
                return parsed if isinstance(parsed, list) else []
            except (json.JSONDecodeError, TypeError, ValueError) as e:
                print(f"DEBUG SCHEMA - JSON parse failed: {e}")
                # If JSON parsing fails, try to fix malformed JSON
                try:
                    # Handle malformed JSON like '{"עיצוב וקישוט",צילום,אבטחה}'
                    extras_str = str(obj.extras).strip()
                    print(f"DEBUG SCHEMA - Processing malformed JSON: {extras_str}")
                    
                    # Remove outer braces if present
                    if extras_str.startswith('{') and extras_str.endswith('}'):
                        extras_str = extras_str[1:-1]
                    
                    # Split by comma and clean up
                    items = []
                    for item in extras_str.split(','):
                        item = item.strip()
                        # Remove quotes if present
                        if item.startswith('"') and item.endswith('"'):
                            item = item[1:-1]
                        elif item.startswith("'") and item.endswith("'"):
                            item = item[1:-1]
                        if item:
                            items.append(item)
                    
                    print(f"DEBUG SCHEMA - Fixed items: {items}")
                    return items
                except Exception as e:
                    print(f"DEBUG SCHEMA - Fix failed: {e}")
                    return []
        return []

class GetOrderNonAdminSchema(Schema):
    id = fields.String()
    full_name = fields.String()
    phone = fields.String()
    another_phone = fields.String(allow_none=True)
    another_name = fields.String(allow_none=True)
    min_guests = fields.Integer()
    max_guests = fields.Integer()
    date = fields.Date()
    start_time = fields.String()
    end_time = fields.String()
    order_type = fields.String()
    comments = fields.String(allow_none=True)
    extras = fields.Method("get_extras")
    
    def get_extras(self, obj):
        if obj.extras:
            try:
                import json
                # First try normal JSON parsing
                parsed = json.loads(obj.extras)
                return parsed if isinstance(parsed, list) else []
            except (json.JSONDecodeError, TypeError, ValueError):
                # If JSON parsing fails, try to fix malformed JSON
                try:
                    # Handle malformed JSON like '{"עיצוב וקישוט",צילום,אבטחה}'
                    extras_str = str(obj.extras).strip()
                    
                    # Remove outer braces if present
                    if extras_str.startswith('{') and extras_str.endswith('}'):
                        extras_str = extras_str[1:-1]
                    
                    # Split by comma and clean up
                    items = []
                    for item in extras_str.split(','):
                        item = item.strip()
                        # Remove quotes if present
                        if item.startswith('"') and item.endswith('"'):
                            item = item[1:-1]
                        elif item.startswith("'") and item.endswith("'"):
                            item = item[1:-1]
                        if item:
                            items.append(item)
                    
                    return items
                except Exception:
                    return []
        return []

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
    anotherPhone = fields.Str(required=False, allow_none=True)
    anotherName = fields.Str(required=False, allow_none=True)
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
    extras = fields.List(fields.Str(), required=False, allow_none=True)

    @validates_schema
    def validate_guests(self, data, **kwargs):
        if data['minGuests'] > data['maxGuests']:
            raise ValidationError("minGuests cannot be greater than maxGuests", field_name="minGuests")


class AddCategorySchema(Schema):
    id = fields.String(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    
    class Meta:
        unknown = EXCLUDE


class GetCategorySchema(Schema):
    id = fields.String()
    name = fields.String()
    isActive = fields.Boolean()
    createdBy = fields.String()
    created_at = fields.DateTime()


class AddSubCategorySchema(Schema):
    id = fields.String(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    parent_category_id = fields.Str(required=True)
    
    class Meta:
        unknown = EXCLUDE


class GetSubCategorySchema(Schema):
    id = fields.String()
    name = fields.String()
    parent_category_id = fields.String()
    parent_category_name = fields.String()
    isActive = fields.Boolean()
    createdBy = fields.String()
    created_at = fields.DateTime()


class AddOrderMenuItemSchema(Schema):
    sub_category_id = fields.Str(required=True)
    quantity = fields.Int(required=True, validate=validate.Range(min=1))
    notes = fields.Str(allow_none=True)
    
    class Meta:
        unknown = EXCLUDE


class UpdateOrderMenuSchema(Schema):
    order_id = fields.Str(required=True)
    menu_items = fields.List(fields.Nested(AddOrderMenuItemSchema), required=True)
    
    class Meta:
        unknown = EXCLUDE


class GetOrderMenuItemSchema(Schema):
    id = fields.String()
    order_id = fields.String()
    sub_category_id = fields.String()
    sub_category_name = fields.String()
    parent_category_name = fields.String()
    quantity = fields.Integer()
    notes = fields.String(allow_none=True)
    created_at = fields.DateTime()
    updated_at = fields.DateTime()


class GetOrderMenuSchema(Schema):
    order_id = fields.String()
    order_info = fields.Dict()  # Will contain basic order details
    menu_items = fields.List(fields.Nested(GetOrderMenuItemSchema))
    total_items = fields.Integer()


class DeleteOrderMenuItemSchema(Schema):
    id = fields.String(required=True)
    
    class Meta:
        unknown = EXCLUDE