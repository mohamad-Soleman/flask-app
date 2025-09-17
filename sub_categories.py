from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt, current_user
from models import SubCategories, Categories
from schemas import AddSubCategorySchema, GetSubCategorySchema
from marshmallow import ValidationError

sub_category_bp = Blueprint("sub_categories", __name__)


@sub_category_bp.post("/add")
@jwt_required()
def add_sub_category():
    claims = get_jwt()
    if not claims.get('is_admin', False):
        return jsonify(msg="Admins only!"), 403

    schema = AddSubCategorySchema()
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    # Check if parent category exists
    parent_category = Categories.query.get(data['parent_category_id'])
    if not parent_category or not parent_category.isActive:
        return jsonify({"error": "Parent category not found or inactive"}), 404

    # Check if sub-category already exists for this parent
    existing_sub_category = SubCategories.get_by_name_and_parent(
        data['name'], data['parent_category_id']
    )
    if existing_sub_category:
        return jsonify({"error": "Sub-category already exists for this parent category"}), 409

    new_sub_category = SubCategories(
        name=data['name'],
        parent_category_id=data['parent_category_id'],
        isActive=True,
        createdBy=current_user.username
    )

    new_sub_category.set_id()
    new_sub_category.save()

    return jsonify({"message": "Sub-category created successfully"}), 201


@sub_category_bp.get("/all")
@jwt_required()
def get_all_sub_categories():
    claims = get_jwt()
    if not claims.get('is_admin', False):
        return jsonify(msg="Admins only!"), 403

    sub_categories = SubCategories.get_all_active()
    result = []
    
    for sub_cat in sub_categories:
        sub_cat_data = {
            'id': sub_cat.id,
            'name': sub_cat.name,
            'parent_category_id': sub_cat.parent_category_id,
            'parent_category_name': sub_cat.parent_category.name if sub_cat.parent_category else 'Unknown',
            'isActive': sub_cat.isActive,
            'createdBy': sub_cat.createdBy,
            'created_at': sub_cat.created_at
        }
        result.append(sub_cat_data)

    return jsonify({"sub_categories": result}), 200


@sub_category_bp.get("/by-parent/<parent_category_id>")
@jwt_required()
def get_sub_categories_by_parent(parent_category_id):
    claims = get_jwt()
    if not claims.get('is_admin', False):
        return jsonify(msg="Admins only!"), 403

    sub_categories = SubCategories.get_by_parent_category(parent_category_id)
    schema = GetSubCategorySchema(many=True)
    result = schema.dump(sub_categories)

    return jsonify({"sub_categories": result}), 200


@sub_category_bp.delete("/<sub_category_id>")
@jwt_required()
def delete_sub_category(sub_category_id):
    claims = get_jwt()
    if not claims.get('is_admin', False):
        return jsonify(msg="Admins only!"), 403

    sub_category = SubCategories.query.get(sub_category_id)
    if not sub_category:
        return jsonify({"error": "Sub-category not found"}), 404

    sub_category.isActive = False
    sub_category.update()

    return jsonify({"message": "Sub-category deleted successfully"}), 200