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
from datetime import datetime, timedelta

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

        # Soft delete existing menu items and meta for this order
        print(f"Soft deleting existing menu items for order: {order_id}")
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

        # Handle general notes - check if meta already exists and update, otherwise create
        if general_notes:
            print(f"Handling general notes for order: {order_id}")
            # Check if meta already exists (even if soft-deleted)
            existing_meta = OrderMenuMeta.query.filter_by(order_id=order_id).first()
            if existing_meta:
                print(f"Updating existing menu meta for order: {order_id}")
                existing_meta.general_notes = general_notes
                existing_meta.isActive = True
                existing_meta.updated_at = db.func.now()
                existing_meta.save()
                print(f"Successfully updated existing menu meta for order: {order_id}")
            else:
                print(f"Creating new menu meta for order: {order_id}")
                menu_meta = OrderMenuMeta(
                    order_id=order_id,
                    general_notes=general_notes,
                    createdBy=current_user.username
                )
                menu_meta.set_id()
                menu_meta.save()
                print(f"Successfully created new menu meta for order: {order_id}")
        
        # Commit all changes first
        db.session.commit()
        print(f"Successfully committed all changes for order: {order_id}")
        
        # Now clean up inactive records for this order (hard delete) - AUTOMATIC CLEANUP
        print(f"Starting automatic cleanup for order: {order_id}")
        try:
            # Hard delete inactive menu items for this order
            inactive_menu_items = OrderMenu.query.filter_by(order_id=order_id, isActive=False).all()
            deleted_items_count = 0
            for item in inactive_menu_items:
                db.session.delete(item)
                deleted_items_count += 1
            print(f"Hard deleted {deleted_items_count} inactive menu items for order: {order_id}")
            
            # Hard delete inactive menu meta for this order
            inactive_menu_meta = OrderMenuMeta.query.filter_by(order_id=order_id, isActive=False).all()
            deleted_meta_count = 0
            for meta in inactive_menu_meta:
                db.session.delete(meta)
                deleted_meta_count += 1
            print(f"Hard deleted {deleted_meta_count} inactive menu meta for order: {order_id}")
            
            # Commit the cleanup
            db.session.commit()
            print(f"✅ Automatic cleanup completed for order {order_id}: {deleted_items_count} items, {deleted_meta_count} meta records")
            
            # Optional: Also clean up any orphaned inactive records (records without active counterparts)
            _cleanup_orphaned_inactive_records()
            
        except Exception as cleanup_error:
            print(f"⚠️ Warning: Error during automatic cleanup for order {order_id}: {cleanup_error}")
            # Don't fail the main operation if cleanup fails
            db.session.rollback()
            # Re-commit the main changes
            db.session.commit()

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




def _cleanup_orphaned_inactive_records():
    """Helper function to clean up orphaned inactive records"""
    try:
        print("🧹 Starting orphaned records cleanup...")
        
        # Find inactive menu items that have no active counterparts
        orphaned_items = db.session.query(OrderMenu).filter(
            OrderMenu.isActive == False,
            ~OrderMenu.order_id.in_(
                db.session.query(OrderMenu.order_id).filter(OrderMenu.isActive == True)
            )
        ).all()
        
        # Find inactive menu meta that have no active counterparts
        orphaned_meta = db.session.query(OrderMenuMeta).filter(
            OrderMenuMeta.isActive == False,
            ~OrderMenuMeta.order_id.in_(
                db.session.query(OrderMenuMeta.order_id).filter(OrderMenuMeta.isActive == True)
            )
        ).all()
        
        # Delete orphaned records
        orphaned_items_count = 0
        for item in orphaned_items:
            db.session.delete(item)
            orphaned_items_count += 1
            
        orphaned_meta_count = 0
        for meta in orphaned_meta:
            db.session.delete(meta)
            orphaned_meta_count += 1
        
        if orphaned_items_count > 0 or orphaned_meta_count > 0:
            db.session.commit()
            print(f"🧹 Cleaned up {orphaned_items_count} orphaned menu items and {orphaned_meta_count} orphaned meta records")
        else:
            print("🧹 No orphaned records found")
            
    except Exception as e:
        print(f"⚠️ Error during orphaned records cleanup: {e}")
        db.session.rollback()

