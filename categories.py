from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt, current_user
from models import Categories
from schemas import AddCategorySchema, GetCategorySchema
from marshmallow import ValidationError

category_bp = Blueprint("categories", __name__)


@category_bp.post("/add")
@jwt_required()
def add_category():
    claims = get_jwt()
    if not claims.get('is_admin', False):
        return jsonify(msg="Admins only!"), 403

    schema = AddCategorySchema()
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    # Check if category already exists
    existing_category = Categories.get_by_name(data['name'])
    if existing_category:
        return jsonify({"error": "Category already exists"}), 409

    new_category = Categories(
        name=data['name'],
        isActive=True,
        createdBy=current_user.username
    )

    new_category.set_id()
    new_category.save()

    return jsonify({"message": "Category created successfully"}), 201


@category_bp.get("/all")
@jwt_required()
def get_all_categories():
    claims = get_jwt()
    if not claims.get('is_admin', False):
        return jsonify(msg="Admins only!"), 403

    categories = Categories.get_all_active()
    schema = GetCategorySchema(many=True)
    result = schema.dump(categories)

    return jsonify({"categories": result}), 200


@category_bp.delete("/<category_id>")
@jwt_required()
def delete_category(category_id):
    claims = get_jwt()
    if not claims.get('is_admin', False):
        return jsonify(msg="Admins only!"), 403

    category = Categories.query.get(category_id)
    if not category:
        return jsonify({"error": "Category not found"}), 404

    category.isActive = False
    category.update()

    return jsonify({"message": "Category deleted successfully"}), 200