import hashlib
import os
from flask import Blueprint, jsonify, request, send_from_directory, redirect
from sqlalchemy.exc import SQLAlchemyError
from config import UPLOAD_URL
from app.models import db, User, Product, Review, ReviewMedia
from app.common_functions import product_short_to_dict, get_product_with_stats, get_product_with_stats_by_barcode, product_reviews_to_dict, hash_password
from flask_jwt_extended import create_access_token, create_refresh_token, set_access_cookies, set_refresh_cookies, jwt_required, get_jwt_identity

main_bp = Blueprint('main', __name__)

@main_bp.route("/products/get-by-id-list", methods=["GET"])
def get_products_by_id_list():
    """
    Fetch a list of products by ID (numeric).
    """
    try:
        product_ids = request.args.get("ids")

        if not product_ids:
            return jsonify({"error": "Invalid data"}), 400

        product_ids = str(product_ids)
        product_ids = product_ids.split(",")
        product_ids = [int(product_id) for product_id in product_ids]
        result = []
        for product_id in product_ids:
            product_data = get_product_with_stats(product_id)
            if product_data:
                result.append(product_short_to_dict(*product_data))
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@main_bp.route("/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
    """
    Fetch a product by ID (numeric) or barcode (string).
    """
    try:
        # Determine if the identifier is numeric (ID) or not (barcode)
        result = get_product_with_stats(int(product_id))

        # Handle case where product is not found
        if not result:
            return jsonify({"error": "Product not found"}), 404

        # Serialize and return the product
        return jsonify(product_reviews_to_dict(*result)), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@main_bp.route("/products/get-by-barcode", methods=["GET"])
def get_product_barcode():
    """
    Fetch a product by ID (numeric) or barcode (string).
    """
    try:
        # Determine if the identifier is numeric (ID) or not (barcode)
        barcode = request.args.get("barcode")
        result = get_product_with_stats_by_barcode(str(barcode))

        # Handle case where product is not found
        if not result:
            return jsonify({"error": "Product not found"}), 404

        # Serialize and return the product
        return jsonify(product_reviews_to_dict(*result)), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



@main_bp.route("/register", methods=["POST"])
def register():
    """
    Register user with email, nickname, password, and salt.
    """
    try:
        data = request.get_json()
        email = data.get("email").lower()
        nickname = data.get("nickname")
        password_raw = data.get("password")

        if not email or not nickname or not password_raw:
            return jsonify({"error": "Invalid data"}), 400

        check_email = User.query.filter_by(email=email).first()
        if check_email:
            return jsonify({"error": "Email already in use"}), 409
        
        check_nickname = User.query.filter_by(nickname=nickname).first()
        if check_nickname:
            return jsonify({"error": "Nickname already in use"}), 409
        
        salt = os.urandom(32).hex()
        password = hash_password(password_raw, salt)
        
        user = User(
            email=email,
            nickname=nickname,
            password=password,
            salt=salt
        )
        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "User registered successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@main_bp.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        email = data.get("email").lower()
        password_raw = data.get("password")

        if not email or not password_raw:
            return jsonify({"error": "Invalid data"}), 400

        user = User.query.filter_by(email=email).first()
        if not user or user.password != hash_password(password_raw, user.salt):
            return jsonify({"error": "Invalid credentials"}), 401

        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))

        response = jsonify({"email": email, "nickname": user.nickname})
        set_access_cookies(response, access_token)
        set_refresh_cookies(response, refresh_token)
        return response, 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@main_bp.route("/uploads/<path:filename>", methods=["GET"])
def download(filename):
    try:
        absolute_dir= os.path.join(os.getcwd(), "uploads")
        return send_from_directory(absolute_dir, filename, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
