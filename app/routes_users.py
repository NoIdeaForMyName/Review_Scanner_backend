import hashlib
import base64
import os
import io
import numpy as np
from PIL import Image
from flask import Blueprint, jsonify, request
from sqlalchemy.exc import SQLAlchemyError
from config import MAX_UPLOAD_SIZE, UPLOAD_DIR
from app.models import db, User, Product, Review, ReviewMedia, ScanHistory
from app.common_functions import get_product_with_stats, get_product_with_stats_by_barcode, product_reviews_to_dict, hash_password, get_user_scan_history, scan_history_product_to_list_dict
from flask_jwt_extended import create_access_token, create_refresh_token, set_access_cookies, set_refresh_cookies, jwt_required, get_jwt_identity, unset_jwt_cookies

auth_bp = Blueprint('auth', __name__)


#TODO: add product, add review, my revious

@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    try:
        current_user_id = int(get_jwt_identity())
        new_access_token = create_access_token(identity=current_user_id)
        response = jsonify({"message": "Token refreshed"})
        set_access_cookies(response, new_access_token)
        return response, 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_bp.route("/user-data", methods=["GET"])
@jwt_required()
def user_data():
    current_user_id = int(get_jwt_identity())
    try:
        user = User.query.filter_by(id=current_user_id).first()
        return jsonify({"email": user.email, "nickname": user.nickname}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    response = jsonify({"message": "Logout successful"})
    unset_jwt_cookies(response)
    return response, 200

@auth_bp.route("/scan-history", methods=["GET"])
@jwt_required()
def scan_history():
    current_user_id = int(get_jwt_identity())
    try:
        result = get_user_scan_history(current_user_id)

        if not result:
            return jsonify({"error": "history not found"}), 404

        return jsonify(scan_history_product_to_list_dict(result)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@auth_bp.route("/add-to-history", methods=["POST"])
@jwt_required()
def add_to_history():
    try:
        current_user_id = int(get_jwt_identity())
        # Determine if the identifier is numeric (ID) or not (barcode)
        data = request.get_json()
        barcode = data.get("barcode")
        prod_id = data.get("id")

        if barcode:
            result = Product.query.filter_by(product_barcode=str(barcode)).first()
        elif prod_id:
            result = Product.query.filter_by(id=int(prod_id)).first()
        else:
            return jsonify({"error": "Invalid data"}), 400        

        # Handle case where product is not found
        if not result:
            return jsonify({"error": "Product not found"}), 404
        
        # find if the product is already in the history
        scan_history = ScanHistory.query.filter_by(scan_history_user_fk=current_user_id, scan_history_product_fk=result.id).first()
        if scan_history:
            return jsonify({"error": "Product already in history"}), 409

        scan_history = ScanHistory(
            scan_history_user_fk=current_user_id,
            scan_history_product_fk=result.id
        )
        db.session.add(scan_history)
        db.session.commit()
        return jsonify({"message": "Product added to history"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@auth_bp.route("/add-product", methods=["POST"])
@jwt_required()
def add_product():
    current_user_id = int(get_jwt_identity())
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Invalid data"}), 400
        
        barcode = data.get("barcode")
        name = data.get("name")
        description = data.get("description")
        image_base64 = data.get("image_base64")

        if not barcode or not name or not description or not image_base64:
            return jsonify({"error": "Invalid data"}), 400
        
        product = Product.query.filter_by(product_barcode=barcode).first()
        if product:
            return jsonify({"error": "Product already exists"}), 409
        
        try:
            image_bytes = base64.b64decode(image_base64)
        except Exception as e:
            return jsonify({"error": f"Base64 decoding failed: {str(e)}"}), 400
        
        image = Image.open(io.BytesIO(image_bytes))

        ratios = np.array(image.size) / np.array(MAX_UPLOAD_SIZE)
        if max(ratios) > 1.0:
            max_ratio  = max(ratios)
            new_size = tuple((np.array(image.size) / max_ratio).astype(int))
            image = image.resize(new_size, Image.Resampling.LANCZOS)
        
        product_db = Product(
            product_barcode=barcode,
            product_name=name,
            product_description=description,
            product_image="place_holder.jpg",
        )

        db.session.add(product_db)
        db.session.commit()
        product_id = product_db.id
        image_filename = f"prod_{product_id}.jpg"
        product_db.product_image = image_filename
        db.session.commit()

        image.save(os.path.join(UPLOAD_DIR, image_filename), "JPEG")
        return jsonify({"message": "Product added successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
