from flask import Flask, jsonify
from extensions import db, jwt
from auth import auth_bp
from orders import order_bp
from users import user_bp
from categories import category_bp
from sub_categories import sub_category_bp
from models import User, TokenBlocklist, Categories, SubCategories, generate_uuid
from flask_cors import CORS
import os


def create_app():
    app = Flask(__name__)
    
    # Configure CORS to allow credentials (cookies) with more permissive settings for development
    CORS(app,
         supports_credentials=True,
         origins=['http://localhost:4200', 'http://127.0.0.1:4200', 'https://flourishing-sherbet-79ac5a.netlify.app'],
         allow_headers=['Content-Type', 'Authorization'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])

    app.config.from_prefixed_env()
    
    # Configure JWT to read tokens from cookies AND headers (fallback)
    app.config['JWT_TOKEN_LOCATION'] = ['cookies', 'headers']
    app.config['JWT_COOKIE_CSRF_PROTECT'] = False  # Disable CSRF for simplicity
    app.config['JWT_ACCESS_COOKIE_NAME'] = 'access_token'
    app.config['JWT_REFRESH_COOKIE_NAME'] = 'refresh_token'
    app.config['JWT_HEADER_NAME'] = 'Authorization'
    app.config['JWT_HEADER_TYPE'] = 'Bearer'

    # initialize exts
    db.init_app(app)
    jwt.init_app(app)

    with app.app_context():
        db.create_all()
        # Create default admin user if not exists
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', email="mohamad.soleman.2016@gmail.com", isAdmin=True, isActive=True,
                         createdBy="admin")
            admin.set_id()
            admin.set_password('moha506090')
            admin.save()
            print("Default admin user created.")
        else:
            print("Admin user already exists.")

        # Create default categories if not exists
        default_categories = [
            'סוגי אירועים',
            'سلطات',
            'سلطات موسمية',
            'سلطات اكسترا',
            'وجبات اولى ساخنة',
            'وجبات مميزة',
            'وجبات اولية',
            'وجبات رئيسية',
            'وجبات رئيسية مميزة',
        ]

        for category_name in default_categories:
            if not Categories.get_by_name(category_name):
                category = Categories(
                    name=category_name,
                    isActive=True,
                    createdBy='admin'
                )
                category.set_id()
                category.save()
                print(f"Default category '{category_name}' created.")
            else:
                print(f"Category '{category_name}' already exists.")

        # Create default sub-categories if not exists
        default_sub_categories = [
            {'name': 'חתונה', 'parent': 'סוגי אירועים'},
            {'name': 'אירוסין', 'parent': 'סוגי אירועים'},
            {'name': 'יום הולדת', 'parent': 'סוגי אירועים'},
            {'name': 'אירוע עסקי', 'parent': 'סוגי אירועים'},
            {'name': 'אחר', 'parent': 'סוגי אירועים'}
        ]
        
        for sub_cat_data in default_sub_categories:
            parent_category = Categories.get_by_name(sub_cat_data['parent'])
            if parent_category and not SubCategories.get_by_name_and_parent(sub_cat_data['name'], parent_category.id):
                sub_category = SubCategories(
                    name=sub_cat_data['name'],
                    parent_category_id=parent_category.id,
                    isActive=True,
                    createdBy='admin'
                )
                sub_category.set_id()
                sub_category.save()
                print(f"Default sub-category '{sub_cat_data['name']}' created under '{sub_cat_data['parent']}'.")
            elif parent_category:
                print(f"Sub-category '{sub_cat_data['name']}' already exists under '{sub_cat_data['parent']}'.")

    # register bluepints
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(user_bp, url_prefix="/users")
    app.register_blueprint(order_bp, url_prefix="/orders")
    app.register_blueprint(category_bp, url_prefix="/categories")
    app.register_blueprint(sub_category_bp, url_prefix="/sub-categories")

    # Add a root route
    @app.route('/')
    def home():
        return jsonify({"message": "Flask API is running", "status": "success"})

    # load user
    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_headers, jwt_data):
        identity = jwt_data["sub"]

        return User.query.filter_by(username=identity).one_or_none()

    # additional claims

    @jwt.additional_claims_loader
    def make_additional_claims(identity):
        if identity == "janedoe123":
            return {"is_staff": True}
        return {"is_staff": False}

    # jwt error handlers

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_data):
        return jsonify({"message": "Token has expired", "error": "token_expired"}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return (
            jsonify(
                {"message": "Signature verification failed", "error": "invalid_token"}
            ),
            401,
        )

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return (
            jsonify(
                {
                    "message": "Request doesnt contain valid token",
                    "error": "authorization_header",
                }
            ),
            401,
        )

    @jwt.token_in_blocklist_loader
    def token_in_blocklist_callback(jwt_header, jwt_data):
        jti = jwt_data['jti']

        token = db.session.query(TokenBlocklist).filter(TokenBlocklist.jti == jti).scalar()

        return token is not None

    return app

app = create_app()

# This is only for development - Gunicorn will use the app variable above
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)