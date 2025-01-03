import hashlib
import base64
import os
import io
import numpy as np
from datetime import datetime
from PIL import Image
from flask import Blueprint, jsonify, request
from sqlalchemy.exc import SQLAlchemyError
from config import MAX_UPLOAD_SIZE, UPLOAD_DIR
from app.models import db, User, Product, Review, ReviewMedia, ScanHistory, Shop
from app.common_functions import get_product_with_stats, get_product_with_stats_by_barcode, product_reviews_to_dict, hash_password, resize_image, review_to_dict, scan_history_product_to_list_dict
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
        scan_histories = ScanHistory.query.filter_by(scan_history_user_fk=current_user_id).order_by(ScanHistory.scan_timestamp.desc()).all()
        scan_dict = [{"id": scan.scan_history_product_fk, "timestamp": scan.scan_timestamp} for scan in scan_histories]

        return jsonify(scan_dict), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@auth_bp.route("/my-reviews", methods=["GET"])
@jwt_required()
def my_reviews():
    current_user_id = int(get_jwt_identity())
    try:
        results = Review.query.filter_by(reviews_user_fk=current_user_id).all()

        if not results:
            return jsonify({"error": "reviews not found"}), 404

        return jsonify([review_to_dict(result) for result in results]), 200
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
            scan_history.scan_timestamp = datetime.now()
            message = "Updated history"
        else:
            scan_history = ScanHistory(
                scan_history_user_fk=current_user_id,
                scan_history_product_fk=result.id,
                scan_timestamp=datetime.now()
            )
            db.session.add(scan_history)
            message = "Added to history"
        db.session.commit()
        return jsonify({"message": message}), 201

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
        image = resize_image(image)
        
        product_db = Product(
            product_barcode=barcode,
            product_name=name,
            product_description=description,
            product_image="place_holder.jpg",
        )

        db.session.add(product_db)
        db.session.flush()
        product_id = product_db.id
        image_filename = f"prod_{product_id}.jpg"
        product_db.product_image = image_filename

        image.save(os.path.join(UPLOAD_DIR, image_filename), "JPEG")
        db.session.commit()
        return jsonify({"message": "Product added successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_bp.route("/add-review", methods=["POST"])
@jwt_required()
def add_review():
    current_user_id = int(get_jwt_identity())
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Invalid data"}), 400

        prod_id = data.get("product_id")
        grade = data.get("grade")
        title = data.get("title")
        description = data.get("description")
        price = data.get("price")
        shop_name = data.get("shop_name")
        images_base64 = data.get("images_base64")

        if not all([prod_id, grade, title, description, price, shop_name, images_base64]):
            return jsonify({"error": "Invalid data"}), 400
        
        prod_id = int(prod_id)
        grade = int(grade)
        price = float(price)
        title = title.strip()
        description = description.strip()
        shop_name = shop_name.strip()
        images_base64 = [str(image) for image in images_base64]

        product = Product.query.filter_by(id=prod_id).first()
        if not product:
            return jsonify({"error": "Product doesnt exist"}), 409
        
        # find review for this product by this user
        review = Review.query.filter_by(reviews_user_fk=current_user_id, review_product_fk=prod_id).first()
        if review:
            return jsonify({"error": "Review already exists"}), 409

        # check if shop name exists
        shop = Shop.query.filter_by(shop_name=shop_name).first()
        if not shop:
            shop = Shop(shop_name=shop_name)
            db.session.add(shop)
            db.session.flush() 
        
        # add review
        review = Review(
            reviews_user_fk=current_user_id,
            review_product_fk=prod_id,
            review_grade=grade,
            review_title=title,
            review_description=description,
            review_price=price,
            review_shop_fk=shop.id
        )
        db.session.add(review)
        db.session.flush()
        # get this review pk
        review_id = review.id
        
        try:
            images_bytes = [base64.b64decode(image_base64) for image_base64 in images_base64]
        except Exception as e:
            return jsonify({"error": f"Base64 decoding failed: {str(e)}"}), 400
        
        for image_bytes in images_bytes:
            image = Image.open(io.BytesIO(image_bytes))
            review_media = ReviewMedia(
                media_review_fk=review_id,
                media_path="place_holder.jpg"
            )
            db.session.add(review_media)
            db.session.flush()
            review_media_id = review_media.id
            image_filename = f"rev_{review_id}_{review_media_id}.jpg"
            image = resize_image(image)
            image.save(os.path.join(UPLOAD_DIR, image_filename), "JPEG")
            review_media.media_path = image_filename

        db.session.commit()
        return jsonify({"message": "Review added successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
