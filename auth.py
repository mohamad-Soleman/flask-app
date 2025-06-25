from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt,
    current_user,
    get_jwt_identity,
)
from models import User, TokenBlocklist

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/register")
@jwt_required()
def register_user():
    claims = get_jwt()
    if not claims.get('is_admin', False):
        return jsonify(msg="Admins only!"), 403
    data = request.get_json()

    user = User.get_user_by_username(username=data.get("username"))

    if user is not None:
        return jsonify({"error": "User already exists"}), 409

    new_user = User(username=data.get("username"), email=data.get("email"),isAdmin=data.get("isAdmin"),isActive=True,createdBy=current_user.username)

    new_user.set_id()
    new_user.set_password(password=data.get("password"))

    new_user.save()

    return jsonify({"message": "User created"}), 201


@auth_bp.post("/login")
def login_user():
    data = request.get_json()

    user = User.get_user_by_username(username=data.get("username"))

    if user and (user.check_password(password=data.get("password"))):
        additional_claims = {"is_admin": user.isAdmin}
        access_token = create_access_token(identity=user.username,additional_claims=additional_claims)
        refresh_token = create_refresh_token(identity=user.username,additional_claims=additional_claims)

        return (
            jsonify(
                {
                    "message": "Logged In ",
                    "tokens": {"access": access_token, "refresh": refresh_token},
                }
            ),
            200,
        )

    return jsonify({"error": "Invalid username or password"}), 400


@auth_bp.get("/whoami")
@jwt_required()
def whoami():
    return jsonify(
        {
            "message": "message",
            "user_details": {
                "username": current_user.username,
                "email": current_user.email,
            },
        }
    )

@auth_bp.get("/verify")
@jwt_required()
def verify_token_is_valid():
    return jsonify(
        {
            "message": "token is valid",
        }
    ) , 200


@auth_bp.get("/refresh")
@jwt_required(refresh=True)
def refresh_access():
    identity = get_jwt_identity()
    claims = get_jwt()
    additional_claims = {"is_admin": claims.get('is_admin', False)}

    new_access_token = create_access_token(identity=identity,additional_claims=additional_claims)

    return jsonify({"access_token": new_access_token})


@auth_bp.get('/logout')
@jwt_required(verify_type=False)
def logout_user():
    jwt = get_jwt()

    jti = jwt['jti']
    token_type = jwt['type']

    token_b = TokenBlocklist(jti=jti)

    token_b.save()

    return jsonify({"message": f"{token_type} token revoked successfully"}) , 200

