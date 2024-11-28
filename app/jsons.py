from app.models import User, Product, Review, ReviewMedia, Shop
from flask import jsonify

def review_to_dict(review: Review) -> dict:
    user = review.user
    shop = review.shop
    media = review.media
    return {
        "id": review.id,
        "user": {
            "id": user.id,
            "email": user.email,
            "nickname": user.nickname,
        },
        "product": review.review_product_fk,
        "grade": review.review_grade,
        "title": review.review_title,
        "description": review.review_description,
        "price": review.review_price,
        "shop": {
            "id": shop.id,
            "name": shop.shop_name,
        },
        "media": [
            {
                "id": medium.id,
                "url": medium.media_path,
            }
            for medium in media
        ],
    }

def product_reviews_to_dict(product: Product) -> dict:
    return {
        'id': product.id,
        'name': product.product_name,
        'description': product.product_description,
        'image': product.product_image,
        'barcode': product.product_barcode,
        'reviews': [review_to_dict(review) for review in product.reviews]
    }