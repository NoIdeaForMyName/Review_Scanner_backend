from flask import Blueprint, jsonify, request
from sqlalchemy.exc import SQLAlchemyError
from app.models import User, Product, Review, ReviewMedia
from app.common_functions import get_product_with_stats, get_product_with_stats_by_barcode, product_reviews_to_dict

main_bp = Blueprint('main', __name__)

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
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500


@main_bp.route("/products_barcode/<barcode>", methods=["GET"])
def get_product_barcode(barcode):
    """
    Fetch a product by ID (numeric) or barcode (string).
    """
    try:
        # Determine if the identifier is numeric (ID) or not (barcode)
        result = get_product_with_stats_by_barcode(str(barcode))

        # Handle case where product is not found
        if not result:
            return jsonify({"error": "Product not found"}), 404

        # Serialize and return the product
        return jsonify(product_reviews_to_dict(*result)), 200

    except Exception as e:
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500



@main_bp.route("/register", methods=["POST"])
def register():
    """
    Register user with email, nickname, password, and salt.
    """
    try:
        data = request.json
        check_email = User.query.filter_by(email=data["email"]).first()
        if check_email:
            return jsonify({"error": "Email already in use"}), 400
        
        check_nickname = User.query.filter_by(nickname=data["nickname"]).first()
        if check_nickname:
            return jsonify({"error": "Nickname already in use"}), 400
        
        user = User(
            email=data["email"],
            nickname=data["nickname"],
            password=data["password"],
            salt=data["salt"]
        )
        user.save()
        return jsonify({"message": "User registered successfully"}), 201
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500

