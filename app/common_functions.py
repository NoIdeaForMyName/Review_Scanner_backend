from decimal import Decimal
import hashlib
from typing import Union
from sqlalchemy import Row, func
from sqlalchemy.orm import joinedload
from app.models import db, User, Product, Review, ReviewMedia, Shop
from flask import jsonify
from config import UPLOAD_URL

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
        **product_short_to_dict(product, avg_grade, grade_count),
        'reviews': [review_to_dict(review) for review in product.reviews]
    }

def product_short_to_dict(product: Product, avg_grade: float, grade_count: int) -> dict:
    return {
        'id': int(product.id),
        'name': product.product_name,
        'description': product.product_description,
        'image': UPLOAD_URL + product.product_image,
        'barcode': product.product_barcode,
        'average_grade': float(avg_grade),
        'grade_count': int(grade_count),
    }

def get_product_with_stats(product_id: int) -> Union[None, Row[tuple[Product, float, int]]]:
    return db.session.query(
        Product,
        func.avg(Review.review_grade).label("avg_grade"),
        func.count(Review.review_grade).label("review_count")
    ).outerjoin(Review, Review.review_product_fk == Product.id).filter(Product.id == product_id).group_by(Product.id).first()

def get_product_with_stats_by_barcode(barcode: str) -> Union[None, Row[tuple[Product, float, int]]]:
    """
    Fetch a product by barcode with its average review grade and review count.
    """
    return (
        db.session.query(
            Product,
            func.avg(Review.review_grade).label("avg_grade"),
            func.count(Review.review_grade).label("review_count")
        ).outerjoin(Review, Review.review_product_fk == Product.id)
        .filter(Product.product_barcode == barcode)
        .group_by(Product.id)  # Group by Product to calculate stats
        .first()
    )


def hash_password(password: str, salt: str) -> str:
    """
    Hash a password using a salt.
    """
    return hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000).hex()