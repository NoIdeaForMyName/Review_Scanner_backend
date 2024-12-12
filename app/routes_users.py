import hashlib
import os
from flask import Blueprint, jsonify, request
from sqlalchemy.exc import SQLAlchemyError
from app.models import db, User, Product, Review, ReviewMedia
from app.common_functions import get_product_with_stats, get_product_with_stats_by_barcode, product_reviews_to_dict, hash_password, get_user_scan_history, scan_history_product_to_list_dict
from flask_jwt_extended import create_access_token, create_refresh_token, set_access_cookies, set_refresh_cookies, jwt_required, get_jwt_identity, unset_jwt_cookies

auth_bp = Blueprint('auth', __name__)


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    current_user_id = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user_id)
    response = jsonify({"message": "Token refreshed"})
    set_access_cookies(response, new_access_token)
    return response, 200

@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    response = jsonify({"message": "Logout successful"})
    unset_jwt_cookies(response)
    return response, 200

# historia zeskanowanych produktow (/history) -> (scan_history, product info)
@auth_bp.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    current_user_id = int(get_jwt_identity())
    current_user = User.query.get(current_user_id)
    return jsonify({"message": f"Hello, {current_user.nickname}!"}), 200

@auth_bp.route("/scan-history", methods=["GET"])
@jwt_required()
def scan_history():
    current_user_id = int(get_jwt_identity())
    result = get_user_scan_history(current_user_id)

    if not result:
        return jsonify({"error": "Product not found"}), 404

    return jsonify(scan_history_product_to_list_dict(result)), 200
