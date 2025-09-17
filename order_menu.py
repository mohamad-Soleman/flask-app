from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt, current_user
from models import OrderMenu, Orders, SubCategories, Categories, OrderMenuMeta
from schemas import (
    UpdateOrderMenuSchema, 
    GetOrderMenuSchema, 
    GetOrderMenuItemSchema,
    DeleteOrderMenuItemSchema
)
from marshmallow import ValidationError
from extensions import db

order_menu_bp = Blueprint("order_menu", __name__)


@order_menu_bp.post("/update")
@jwt_required()
def update_order_menu():
    """Create or update order menu for a specific order"""
    claims = get_jwt()
    if not claims.get('is_admin', False):
        return jsonify({"success": False, "message": "Admins only!"}), 403

    try:
        request_data = request.get_json()
        print(f"Received request data: {request_data}")  # Debug log
        
        # Handle both possible request formats
        if 'items' in request_data:
            # Angular service sends {items: [...], general_notes: "..."}
            menu_items = request_data['items']
            general_notes = request_data.get('general_notes', '')
            # Extract order_id from first item
            if menu_items and len(menu_items) > 0:
                order_id = menu_items[0]['order_id']
            else:
                return jsonify({"success": False, "message": "No menu items provided"}), 400
        elif 'order_id' in request_data and 'menu_items' in request_data:
            # Schema format {order_id: "...", menu_items: [...]}
            order_id = request_data['order_id']
            menu_items = request_data['menu_items']
            general_notes = request_data.get('general_notes', '')
        else:
            return jsonify({"success": False, "message": "Invalid request format"}), 400

        # Check if order exists
        order = Orders.query.get(order_id)
        if not order or not order.isActive:
            return jsonify({"success": False, "message": "Order not found"}), 404

        # Delete existing menu items and meta for this order
        OrderMenu.delete_by_order_id(order_id)
        OrderMenuMeta.delete_by_order_id(order_id)

        # Add new menu items
        created_items = []
        for item_data in menu_items:
            # Verify sub-category exists
            sub_category = SubCategories.query.get(item_data['sub_category_id'])
            if not sub_category or not sub_category.isActive:
                return jsonify({"success": False, "message": f"Sub-category {item_data['sub_category_id']} not found"}), 404

            # Create new item (simplified - no individual quantity/notes)
            menu_item = OrderMenu(
                order_id=order_id,
                sub_category_id=item_data['sub_category_id'],
                quantity=1,  # Default quantity of 1
                notes=None,  # No individual notes
                createdBy=current_user.username
            )
            menu_item.set_id()
            menu_item.save()
            created_items.append(menu_item)

        # Save general notes if provided
        if general_notes:
            menu_meta = OrderMenuMeta(
                order_id=order_id,
                general_notes=general_notes,
                createdBy=current_user.username
            )
            menu_meta.set_id()
            menu_meta.save()

        return jsonify({
            "success": True,
            "message": "Order menu updated successfully",
            "data": {
                "items_count": len(created_items)
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        print(f"Error updating order menu: {str(e)}")  # Debug log
        return jsonify({
            "success": False,
            "message": f"Database error: {str(e)}",
            "data": None
        }), 500


@order_menu_bp.get("/<order_id>")
@jwt_required()
def get_order_menu(order_id):
    """Get order menu for a specific order"""
    try:
        # Check if order exists
        order = Orders.query.get(order_id)
        if not order or not order.isActive:
            return jsonify({
                "success": False,
                "message": "Order not found",
                "data": []
            }), 404

        # Get menu items for this order
        menu_items = OrderMenu.get_by_order_id(order_id)
        menu_meta = OrderMenuMeta.get_by_order_id(order_id)
        
        # Prepare response data
        items_data = []
        for item in menu_items:
            item_dict = item.to_dict()
            items_data.append(item_dict)

        response_data = {
            "items": items_data,
            "general_notes": menu_meta.general_notes if menu_meta else ""
        }

        return jsonify({
            "success": True,
            "message": "Order menu loaded successfully",
            "data": response_data
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error loading order menu: {str(e)}",
            "data": []
        }), 500


@order_menu_bp.get("/categories-with-subcategories")
@jwt_required()
def get_categories_with_subcategories():
    """Get all categories with their active sub-categories for menu selection"""
    try:
        categories = Categories.get_all_active()
        result = []
        
        for category in categories:
            # Exclude "סוגי אירועים" (Event Types) category from menu selection
            if category.name == "סוגי אירועים":
                continue
                
            active_subcategories = [
                {
                    "id": sub.id,
                    "name": sub.name,
                    "created_at": sub.created_at.isoformat() if sub.created_at else None
                }
                for sub in category.sub_categories if sub.isActive
            ]
            
            if active_subcategories:  # Only include categories that have active sub-categories
                category_data = {
                    "id": category.id,
                    "name": category.name,
                    "sub_categories": active_subcategories
                }
                result.append(category_data)
        
        return jsonify({
            "success": True,
            "message": "Categories loaded successfully",
            "data": result
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error loading categories: {str(e)}",
            "data": []
        }), 500


@order_menu_bp.delete("/item/<item_id>")
@jwt_required()
def delete_menu_item(item_id):
    """Delete a specific menu item"""
    claims = get_jwt()
    if not claims.get('is_admin', False):
        return jsonify(msg="Admins only!"), 403

    menu_item = OrderMenu.query.get(item_id)
    if not menu_item or not menu_item.isActive:
        return jsonify({"error": "Menu item not found"}), 404

    menu_item.delete()
    return jsonify({"message": "Menu item deleted successfully"}), 200


@order_menu_bp.get("/check/<order_id>")
@jwt_required()
def check_order_has_menu(order_id):
    """Check if an order has any menu items"""
    try:
        menu_items = OrderMenu.get_by_order_id(order_id)
        has_menu = len(menu_items) > 0
        
        return jsonify({
            "success": True,
            "message": "Order menu status checked",
            "data": {
                "has_menu_items": has_menu,
                "item_count": len(menu_items)
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error checking order menu: {str(e)}",
            "data": {
                "has_menu_items": False,
                "item_count": 0
            }
        }), 500