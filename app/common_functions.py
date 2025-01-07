from decimal import Decimal
import hashlib
import numpy as np
from PIL import Image
from config import DATETIME_FORMAT, MAX_UPLOAD_SIZE
from typing import Tuple, Union
from sqlalchemy import Row, func
from sqlalchemy.sql.functions import coalesce
from sqlalchemy.orm import joinedload
from app.models import db, User, Product, Review, ReviewMedia, Shop, ScanHistory
from flask import jsonify
from config import UPLOAD_URL
from datetime import datetime

def review_to_dict(review: Review) -> dict:
    user = review.user
    shop = review.shop
    media = review.media or []
    return {
        "id": review.id,
        "user": {
            "id": user.id,
            "email": user.email,
            "nickname": user.nickname,
        },
        "product_id": review.review_product_fk,
        "product_name": review.product.product_name,
        "grade": review.review_grade,
        "title": review.review_title,
        "description": review.review_description,
        "price": Decimal(review.review_price),
        "shop": {
            "id": shop.id,
            "name": shop.shop_name,
        },
        "media": [
            {
                "id": medium.id,
                "url": UPLOAD_URL + medium.media_path,
            }
            for medium in media
        ],
    }

def product_reviews_to_dict(product: Product, avg_grade: float, grade_count: int) -> dict:
    return {
        'id': int(product.id),
        'name': product.product_name,
        'description': product.product_description,
        'image': UPLOAD_URL + product.product_image,
        'barcode': product.product_barcode,
        'average_grade': float(avg_grade),
        'grade_count': int(grade_count),
        'reviews': [review_to_dict(review) for review in product.reviews]
    }

def get_product_with_stats(product_id: int) -> Union[None, Row[tuple[Product, float, int]]]:
    return db.session.query(
        Product,
        coalesce(func.avg(Review.review_grade), 0.0).label("avg_grade"),
        func.count(Review.review_grade).label("review_count")
    ).outerjoin(Review, Review.review_product_fk == Product.id).filter(Product.id == product_id).group_by(Product.id).first()

def get_product_with_stats_by_barcode(barcode: str) -> Union[None, Row[tuple[Product, float, int]]]:
    """
    Fetch a product by barcode with its average review grade and review count.
    """
    return (
        db.session.query(
            Product,
            coalesce(func.avg(Review.review_grade), 0.0).label("avg_grade"),
            func.count(Review.review_grade).label("review_count")
        )
        .outerjoin(Review, Review.review_product_fk == Product.id)
        .filter(Product.product_barcode == barcode)
        .group_by(Product.id)  # Group by Product to calculate stats
        .first()
    )

# def get_user_scan_history(user_id: int) -> Union[None, list[tuple[Product, float, int, datetime]]]:
#     """
#     Fetch specific user scan history with product details.
#     """
#     return (
#         db.session.query(
#             Product,
#             coalesce(func.avg(Review.review_grade), 0.0).label("avg_grade"),
#             func.count(Review.review_grade).label("review_count"),
#             ScanHistory.scan_timestamp #.label("scan_timestamp")
#         )
#         .outerjoin(ScanHistory, ScanHistory.scan_history_product_fk == Product.id)
#         .outerjoin(Review, Review.review_product_fk == Product.id)
#         .filter(ScanHistory.scan_history_user_fk == user_id)
#                 .group_by(
#             Product.id,  # Group by Product primary key
#             ScanHistory.scan_timestamp,  # Group by ScanHistory timestamp
#         )
#         .all()
#     )

def scan_history_product_to_dict(prod: Product, avg_g: float, avg_c: int, scan_timestamp: datetime) -> dict:
    return {**product_reviews_to_dict(prod, avg_g, avg_c), "scan_timestamp": scan_timestamp}

def add_to_scan_history(entry, current_user_id) -> Tuple[dict, int]:
    """
    Add a product to the scan history of a user.
    """
    barcode = entry.get("barcode")
    prod_id = entry.get("id")
    timestamp = entry.get("timestamp")

    if barcode and timestamp:
        result = Product.query.filter_by(product_barcode=str(barcode)).first()
    elif prod_id and timestamp:
        result = Product.query.filter_by(id=int(prod_id)).first()
    else:
        return {"error": "Invalid data"}, 400

    # Handle case where product is not found
    if not result:
        return {"error": "Product not found"}, 404
    
    # find if the product is already in the history
    scan_history = ScanHistory.query.filter_by(scan_history_user_fk=current_user_id, scan_history_product_fk=result.id).first()
    
    timestamp_datetime = datetime.strptime(timestamp, DATETIME_FORMAT)
    if scan_history:
        scan_history.scan_timestamp = timestamp
        message = "Updated history"
    else:
        scan_history = ScanHistory(
            scan_history_user_fk=current_user_id,
            scan_history_product_fk=result.id,
            scan_timestamp=timestamp_datetime
        )
        db.session.add(scan_history)
        message = "Added to history"
    return {"message": message}, 201

def scan_history_product_to_list_dict(product_timestamp_list):
    return [scan_history_product_to_dict(*e) for e in product_timestamp_list]

def model_to_dict(model):
    return {c.name: getattr(model, c.name) for c in model.__table__.columns}

def hash_password(password: str, salt: str) -> str:
    """
    Hash a password using a salt.
    """
    return hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000).hex()

def resize_image(image: Image.Image) -> Image.Image:
    """
    Resize an image to a specific size.
    """
    ratios = np.array(image.size) / np.array(MAX_UPLOAD_SIZE)

    if max(ratios) > 1.0:
        max_ratio  = max(ratios)
        new_size = tuple((np.array(image.size) / max_ratio).astype(int))
        image = image.resize(new_size, Image.Resampling.LANCZOS)
    return image