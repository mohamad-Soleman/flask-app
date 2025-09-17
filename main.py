from flask import Flask, jsonify
from extensions import db, jwt
from auth import auth_bp
from orders import order_bp
from users import user_bp
from categories import category_bp
from sub_categories import sub_category_bp
from order_menu import order_menu_bp
from models import User, TokenBlocklist, Categories, SubCategories, OrderMenu, generate_uuid
from flask_cors import CORS
import os


def create_app():
    app = Flask(__name__)
    
    # Configure CORS to allow credentials (cookies) with more permissive settings for development
    CORS(app,
         supports_credentials=True,
         origins=['http://localhost:4200', 'http://127.0.0.1:4200', 'https://angular-auth-app-4lnm.onrender.com'],
         allow_headers=['Content-Type', 'Authorization'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
         expose_headers=["Content-Type", "Authorization", "Set-Cookie"])

    app.config.from_prefixed_env()
    
    # Configure JWT to read tokens from cookies AND headers (fallback)
    app.config['JWT_TOKEN_LOCATION'] = ['cookies', 'headers']
    app.config['JWT_COOKIE_CSRF_PROTECT'] = False  # Disable CSRF for simplicity
    app.config['JWT_ACCESS_COOKIE_NAME'] = 'access_token'
    app.config['JWT_REFRESH_COOKIE_NAME'] = 'refresh_token'
    app.config['JWT_HEADER_NAME'] = 'Authorization'
    app.config['JWT_HEADER_TYPE'] = 'Bearer'
    app.config["JWT_COOKIE_SECURE"] = True  # required for HTTPS on Render
    app.config["JWT_COOKIE_SAMESITE"] = "None"  # allow cross-site cookies

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
            {'name': 'אחר', 'parent': 'סוגי אירועים'},

            {"name": "حمص", "parent": "سلطات"},
            {"name": "حمص / طحينة مع مقدونس", "parent": "سلطات"},
            {"name": "تبولة", "parent": "سلطات"},
            {"name": "بابا غنوج يوناني", "parent": "سلطات"},
            {"name": "بابا غنوج مع باذنجان", "parent": "سلطات"},
            {"name": "لبنة زعتر", "parent": "سلطات"},
            {"name": "لبنة مدخنة", "parent": "سلطات"},
            {"name": "ذرة", "parent": "سلطات"},
            {"name": "فلفل آسيوي", "parent": "سلطات"},
            {"name": "شمندر", "parent": "سلطات"},
            {"name": "فتوش", "parent": "سلطات"},
            {"name": "باستا", "parent": "سلطات"},
            {"name": "زيتون", "parent": "سلطات"},
            {"name": "نوجة", "parent": "سلطات"},
            {"name": "سلطة دجاج بونتاي", "parent": "سلطات"},
            {"name": "سلطة مع كسبرات", "parent": "سلطات"},
            {"name": "سلطة سيزر", "parent": "سلطات"},
            {"name": "سلطة كينوا", "parent": "سلطات"},
            {"name": "سلطة كول سلو", "parent": "سلطات"},
            {"name": "باذنجان مغربي حار", "parent": "سلطات"},
            {"name": "باذنجان مع صلصة", "parent": "سلطات"},
            {"name": "باذنجان رومانيا", "parent": "سلطات"},
            {"name": "باذنجان مع صنوبر", "parent": "سلطات"},

            {"name": "بطيخ مع لبنة", "parent": "سلطات موسمية"},
            {"name": "رمان", "parent": "سلطات موسمية"},
            {"name": "أفوكادو", "parent": "سلطات موسمية"},
            {"name": "مانجو", "parent": "سلطات موسمية"},

            {"name": "سلطة شعير ألوان / عادي", "parent": "سلطات اكسترا"},
            {"name": "سوشيما", "parent": "سلطات اكسترا"},
            {"name": "بوراتا", "parent": "سلطات اكسترا"},
            {"name": "فالودا", "parent": "سلطات اكسترا"},
            {"name": "سلطة كانلونس", "parent": "سلطات اكسترا"},
            {"name": "سلطة بير موتزاريلا", "parent": "سلطات اكسترا"},

            {"name": "مقبلات مقرمشة", "parent": "وجبات اولى ساخنة"},
            {"name": "مقلي مشروم إسباني", "parent": "وجبات اولى ساخنة"},
            {"name": "مقلي هامي مطبوخ", "parent": "وجبات اولى ساخنة"},
            {"name": "أرنشيني كرات", "parent": "وجبات اولى ساخنة"},
            {"name": "إغورول سلمون", "parent": "وجبات اولى ساخنة"},
            {"name": "ريفولي مقلي", "parent": "وجبات اولى ساخنة"},
            {"name": "رؤوس كالاماري مقلية", "parent": "وجبات اولى ساخنة"},
            {"name": "صينية موتزاريلا", "parent": "وجبات اولى ساخنة"},
            {"name": "سبانيسكو", "parent": "وجبات اولى ساخنة"},
            {"name": "صدر دجاج إسبانش / بريت", "parent": "وجبات اولى ساخنة"},
            {"name": "كفتة جاج", "parent": "وجبات اولى ساخنة"},
            {"name": "كباب سيخ فرقة", "parent": "وجبات اولى ساخنة"},

            {"name": "سيخ شريحت", "parent": "وجبات اولية"},
            {"name": "سيخ كروف", "parent": "وجبات اولية"},
            {"name": "ضلع كروف", "parent": "وجبات اولية"},
            {"name": "أجنحة دجاج", "parent": "وجبات اولية"},
            {"name": "أنتركوت", "parent": "وجبات اولية"},
            {"name": "فيليه تليو / يسطوري", "parent": "وجبات اولية"},
            {"name": "سيخ سلمون / يسطوري", "parent": "وجبات اولية"},

            {"name": "أضلاع كروف", "parent": "وجبات رئيسية"},
            {"name": "فيليه عجل", "parent": "وجبات رئيسية"},
            {"name": "ستيك تليو", "parent": "وجبات رئيسية"},
            {"name": "أضلاع دجاج", "parent": "وجبات رئيسية"},
            {"name": "أنتركوت", "parent": "وجبات رئيسية"},
            {"name": "فيليه سلمون", "parent": "وجبات رئيسية"},
            {"name": "ستيك عجل", "parent": "وجبات رئيسية"},
            {"name": "فيليه براك", "parent": "وجبات رئيسية"},
            {"name": "صدر دجاج محشي", "parent": "وجبات رئيسية"},
            {"name": "فيليه سمك مقلي", "parent": "وجبات رئيسية"},
            {"name": "سيخ بريت", "parent": "وجبات رئيسية"},

            {"name": "أضلاع كروف تاج", "parent": "وجبات رئيسية مميزة"},
            {"name": "دجاج أورز", "parent": "وجبات رئيسية مميزة"},
            {"name": "دجاج دورة رز", "parent": "وجبات رئيسية مميزة"},
            {"name": "فيليه عجل", "parent": "وجبات رئيسية مميزة"},
            {"name": "ريفة كروف", "parent": "وجبات رئيسية مميزة"},
            {"name": "كتف كروف", "parent": "وجبات رئيسية مميزة"},
            {"name": "كروف كامل محشي", "parent": "وجبات رئيسية مميزة"},

            {"name": "كاماري لينة", "parent": "وجبات مميزة"},
            {"name": "شرمس بيسنو", "parent": "وجبات مميزة"},
            {"name": "شرمس / كاماري", "parent": "وجبات مميزة"},
            {"name": "اسكالوب", "parent": "وجبات مميزة"},
            {"name": "ستيك تليو", "parent": "وجبات مميزة"},
            {"name": "دجاج شيش كباب", "parent": "وجبات مميزة"},
            {"name": "سوسيس سلمون", "parent": "وجبات مميزة"}
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
    app.register_blueprint(order_menu_bp, url_prefix="/order-menu")

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