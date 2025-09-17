from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt , current_user

from models import Orders
from schemas import AddOrderSchema, GetOrderSchema, GetOrderByDatesInputSchema, GetOrderNonAdminSchema, \
    UpdateOrderSchema, DeactivateOrderSchema
from marshmallow import ValidationError


order_bp = Blueprint("orders", __name__)


@order_bp.post("/addorder")
@jwt_required()
def add_new_order():
    claims = get_jwt()
    if not claims.get('is_admin', False):
        return jsonify(msg="Admins only!"), 403

    schema = AddOrderSchema()
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    new_order = Orders(
        full_name=data['fullName'],
        phone=data['phone'],
        another_phone=data.get('anotherPhone'),
        price=data['price'],
        min_guests=data['minGuests'],
        max_guests=data['maxGuests'],
        date=data['date'],
        start_time=data['startTime'],
        end_time=data['endTime'],
        order_amount=data['orderAmount'],
        paid_amount=data['paidAmount'],
        order_type=data['orderType'],
        comments=data.get('comments'),
        createdBy=current_user.username,
        isActive=True
    )

    new_order.set_id()
    new_order.save()

    return jsonify({
        "message": "Order created",
        "success": True,
        "order_id": new_order.id
    }), 201

@order_bp.get("/<order_id>")
@jwt_required()
def get_order_by_id(order_id):
    claims = get_jwt()
    order = Orders.query.get(order_id)
    
    if not order or not order.isActive:
        return jsonify({"success": False, "message": "Order not found"}), 404
    
    # Use appropriate schema based on admin status
    order_schema = GetOrderNonAdminSchema()
    if claims.get("is_admin") == True:
        order_schema = GetOrderSchema()
    
    result = order_schema.dump(order)
    return jsonify({"success": True, "message": "Order found", "data": result}), 200

@order_bp.get("/getorders")
@jwt_required()
def get_all_orders():
    claims = get_jwt()
    orders = Orders.query.filter_by(isActive=True).all()
    order_schema = GetOrderNonAdminSchema(many=True)
    if claims.get("is_admin") == True:
        order_schema = GetOrderSchema(many=True)
    result = order_schema.dump(orders)
    return jsonify(result), 200

@order_bp.post("/getorders")
@jwt_required()
def get_orders_by_dates():
    claims = get_jwt()
    schema = GetOrderByDatesInputSchema()
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
    orders = Orders.query.filter(
        Orders.date.between(data["startDate"], data["endDate"]),
        Orders.isActive == True
    ).all()
    order_schema = GetOrderNonAdminSchema(many=True)
    if claims.get("is_admin") == True:
        order_schema = GetOrderSchema(many=True)
    result = order_schema.dump(orders)
    return jsonify(result), 200

@order_bp.put("/editorder")
@jwt_required()
def edit_order():
    claims = get_jwt()
    if not claims.get('is_admin', False):
        return jsonify(msg="Admins only!"), 403

    schema = UpdateOrderSchema()
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    order = Orders.query.get(data["id"])
    if order:
        order.full_name = data['fullName']
        order.phone = data['phone']
        order.another_phone = data.get('anotherPhone')
        order.price = data['price']
        order.min_guests = data['minGuests']
        order.max_guests = data['maxGuests']
        order.date = data['date']
        order.start_time = data['startTime']
        order.end_time = data['endTime']
        order.order_amount = data['orderAmount']
        order.paid_amount = data['paidAmount']
        order.order_type = data['orderType']
        order.comments = data.get('comments')
    else:
        return {"message": "Order not found"}, 404

    order.update()

    return jsonify({"message": "Order Updated"}), 200

@order_bp.put("/deactivateorder")
@jwt_required()
def deactivate_order():
    claims = get_jwt()
    if not claims.get('is_admin', False):
        return jsonify(msg="Admins only!"), 403

    schema = DeactivateOrderSchema()
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    order = Orders.query.get(data["id"])
    if order:
        order.isActive = False
    else:
        return {"message": "Order not found"}, 404

    order.update()

    return jsonify({"message": "Order Updated"}), 200
