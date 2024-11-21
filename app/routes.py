from flask import Blueprint, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.models import db, User

main_bp = Blueprint('main', __name__)

@main_bp.route("/get_users", methods=["GET"])
def register():
    # select all users
    users = User.query.all()
    return jsonify(users)

# @main_bp.route("/login", methods=["POST"])
# def login():
#     pass

