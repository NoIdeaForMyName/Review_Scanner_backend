from flask import Blueprint, jsonify, request
from app.models import User, Product, Review, ReviewMedia
from app.jsons import product_reviews_to_dict

main_bp = Blueprint('main', __name__)

@main_bp.route("/get_product_info", methods=["GET"])
def get_product_info():
    barcode = request.args.get("barcode")
    product = Product.query.filter_by(product_barcode=barcode).first()
    if product is None:
        return jsonify({"error": "Product not found"})
    else:
        return jsonify(product_reviews_to_dict(product))

# @main_bp.route("/login", methods=["POST"])
# def login():
#     pass

