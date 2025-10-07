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
import logging


def create_app():
    app = Flask(__name__)
    app.config.from_prefixed_env()

    # Get domain from environment variable with fallback
    cookie_domain = os.getenv('JWT_COOKIE_DOMAIN', '.dunyazad.site')
    cors_origins = os.getenv('CORS_ORIGINS', 'http://localhost:4200,http://127.0.0.1:4200,https://angular-auth-app-4lnm.onrender.com,https://dunyazad.site')
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Log domain configuration for debugging
    logger.info(f"JWT Cookie Domain: {cookie_domain}")
    logger.info(f"CORS Origins: {cors_origins}")
    logger.info(f"Environment: {os.getenv('FLASK_ENV', 'development')}")

    # Configure JWT to read tokens from cookies AND headers (fallback)
    app.config['JWT_TOKEN_LOCATION'] = ['cookies', 'headers']
    app.config['JWT_COOKIE_CSRF_PROTECT'] = False  # Disable CSRF for simplicity
    app.config['JWT_ACCESS_COOKIE_NAME'] = 'access_token'
    app.config['JWT_REFRESH_COOKIE_NAME'] = 'refresh_token'
    app.config['JWT_HEADER_NAME'] = 'Authorization'
    app.config['JWT_HEADER_TYPE'] = 'Bearer'
    app.config["JWT_COOKIE_SECURE"] = True  # required for HTTPS on Render
    app.config["JWT_COOKIE_SAMESITE"] = "None"  # allow cross-site cookies
    app.config["JWT_COOKIE_DOMAIN"] = cookie_domain


    # Configure CORS to allow credentials (cookies) with more permissive settings for development
    cors_origins_list = [origin.strip() for origin in cors_origins.split(',')]
    CORS(app,
         supports_credentials=True,
         origins=cors_origins_list,
         allow_headers=['Content-Type', 'Authorization'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
         expose_headers=["Content-Type", "Authorization", "Set-Cookie"])

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
            'سلطات',
            'سلطات خضراء',
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
            {'name': 'حمص', 'parent': 'سلطات'},
            {'name': 'طحينة', 'parent': 'سلطات'},
            {'name': 'طحينة مع بقدونس', 'parent': 'سلطات'},
            {'name': 'تركي', 'parent': 'سلطات'},
            {'name': 'باذنجان يوناني', 'parent': 'سلطات'},
            {'name': 'بابا غنوج مع طحينة', 'parent': 'سلطات'},
            {'name': 'لبنة مثومة', 'parent': 'سلطات'},
            {'name': 'ذرة', 'parent': 'سلطات'},
            {'name': 'جزر', 'parent': 'سلطات'},
            {'name': 'فلفل أسيوي', 'parent': 'سلطات'},
            {'name': 'شمندر', 'parent': 'سلطات'},
            {'name': 'باستا', 'parent': 'سلطات'},
            {'name': 'زيتون', 'parent': 'سلطات'},
            {'name': 'تونة', 'parent': 'سلطات'},
            {'name': 'باذنجان مغربي حار', 'parent': 'سلطات'},
            {'name': 'باذنجان مع سيلان', 'parent': 'سلطات'},
            {'name': 'باذنجان روماني', 'parent': 'سلطات'},
            {'name': 'باذنجان متبل', 'parent': 'سلطات'},

            {'name': 'جرجير', 'parent': 'سلطات خضراء'},
            {'name': 'فتوش', 'parent': 'سلطات خضراء'},
            {'name': 'تبولة', 'parent': 'سلطات خضراء'},
            {'name': 'سلطة دنيازاد', 'parent': 'سلطات خضراء'},
            {'name': 'شمير مع مكسرات', 'parent': 'سلطات خضراء'},
            {'name': 'سلطة حبق', 'parent': 'سلطات خضراء'},
            {'name': 'سلطة كينوا', 'parent': 'سلطات خضراء'},

            {'name': 'بطيخ مع لبنة', 'parent': 'سلطات موسمية'},
            {'name': 'رمان', 'parent': 'سلطات موسمية'},
            {'name': 'أفوكادو', 'parent': 'سلطات موسمية'},
            {'name': 'مانجو', 'parent': 'سلطات موسمية'},

            {'name': 'سلطة شيري ألوان', 'parent': 'سلطات اكسترا'},
            {'name': 'سلطة شيري عادي', 'parent': 'سلطات اكسترا'},
            {'name': 'سوريمي', 'parent': 'سلطات اكسترا'},
            {'name': 'بوراتا', 'parent': 'سلطات اكسترا'},
            {'name': 'فالدوف', 'parent': 'سلطات اكسترا'},
            {'name': 'سلطة كابانوس', 'parent': 'سلطات اكسترا'},
            {'name': 'سلطة بيبي موزاريلا', 'parent': 'سلطات اكسترا'},
            {'name': 'باذنجان دنيازاد', 'parent': 'سلطات اكسترا'},
            {'name': 'سلطة ستي', 'parent': 'سلطات اكسترا'},
            {'name': 'سلطة فواكه', 'parent': 'سلطات اكسترا'},
            {'name': 'سلطة فريكة', 'parent': 'سلطات اكسترا'},
            {'name': 'سلطة شيري لبنة', 'parent': 'سلطات اكسترا'},
            {'name': 'طبق - لوز / جبنة / حامض / جزر', 'parent': 'سلطات اكسترا'},
            {'name': 'سلطة شيري فيتا', 'parent': 'سلطات اكسترا'},

            {'name': 'فقع موكرام', 'parent': 'وجبات اولى ساخنة'},
            {'name': 'فقع محشي أجبان', 'parent': 'وجبات اولى ساخنة'},
            {'name': 'فقع حامي مطبوخ', 'parent': 'وجبات اولى ساخنة'},
            {'name': 'أرنشيني كرات', 'parent': 'وجبات اولى ساخنة'},
            {'name': 'إغرول سلمون', 'parent': 'وجبات اولى ساخنة'},
            {'name': 'جبنة مقلية', 'parent': 'وجبات اولى ساخنة'},
            {'name': 'رؤوس كلماري مقلية', 'parent': 'وجبات اولى ساخنة'},
            {'name': 'صفيحة فوكاتشا', 'parent': 'وجبات اولى ساخنة'},
            {'name': 'سلسيسو', 'parent': 'وجبات اولى ساخنة'},
            {'name': 'صدر دجاج أسياتي / برجيت', 'parent': 'وجبات اولى ساخنة'},
            {'name': 'كباب حلبي', 'parent': 'وجبات اولى ساخنة'},
            {'name': 'كباب سيخ قرفة', 'parent': 'وجبات اولى ساخنة'},

            {'name': 'كلماري لبنة', 'parent': 'وجبات مميزة'},
            {'name': 'شرمس بيستو', 'parent': 'وجبات مميزة'},
            {'name': 'شرمس / كلماري', 'parent': 'وجبات مميزة'},
            {'name': 'لسانات', 'parent': 'وجبات مميزة'},
            {'name': 'مخ عبور', 'parent': 'وجبات مميزة'},
            {'name': 'كبدة أوز', 'parent': 'وجبات مميزة'},
            {'name': 'حليات - שקדי עגל', 'parent': 'وجبات مميزة'},
            {'name': 'سوشي سلمون', 'parent': 'وجبات مميزة'},

            {'name': 'سيخ برجيت', 'parent': 'وجبات اولية'},
            {'name': 'سيخ خروف', 'parent': 'وجبات اولية'},
            {'name': 'ضلع خروف', 'parent': 'وجبات اولية'},
            {'name': 'ستيك فيليه', 'parent': 'وجبات اولية'},
            {'name': 'سيخ فيليه / יקטורי', 'parent': 'وجبات اولية'},
            {'name': 'سيخ سلمون / יקטורי', 'parent': 'وجبات اولية'},

            {'name': 'أضلاع خروف', 'parent': 'وجبات رئيسية'},
            {'name': 'فيليه عجل', 'parent': 'وجبات رئيسية'},
            {'name': 'سينتا عجل', 'parent': 'وجبات رئيسية'},
            {'name': '2 سيخ خروف', 'parent': 'وجبات رئيسية'},
            {'name': 'أنتريكوت', 'parent': 'وجبات رئيسية'},
            {'name': 'فيليه سلمون', 'parent': 'وجبات رئيسية'},
            {'name': 'سمك عجاج', 'parent': 'وجبات رئيسية'},
            {'name': 'سمك لبراك', 'parent': 'وجبات رئيسية'},
            {'name': 'طبة جاج محشية', 'parent': 'وجبات رئيسية'},
            {'name': 'فيليه سمك / لبراك', 'parent': 'وجبات رئيسية'},
            {'name': 'ستيك برجيت', 'parent': 'وجبات رئيسية'},
            {'name': 'شنيتسل', 'parent': 'وجبات رئيسية'},
            {'name': 'صدر جاج', 'parent': 'وجبات رئيسية'},

            {'name': 'أضلاع خروف تاج', 'parent': 'وجبات رئيسية مميزة'},
            {'name': 'كبدة أوز', 'parent': 'وجبات رئيسية مميزة'},
            {'name': 'موزة خروف / رز', 'parent': 'وجبات رئيسية مميزة'},
            {'name': 'كدرة خروف', 'parent': 'وجبات رئيسية مميزة'},
            {'name': 'فيليه عجل ( خردل / صويا / كستناء / برتقال )', 'parent': 'وجبات رئيسية مميزة'},
            {'name': 'طورنادو', 'parent': 'وجبات رئيسية مميزة'},
            {'name': 'رقبة خروف', 'parent': 'وجبات رئيسية مميزة'},
            {'name': 'كتف خروف', 'parent': 'وجبات رئيسية مميزة'},
            {'name': 'خروف كامل محشي', 'parent': 'وجبات رئيسية مميزة'},
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