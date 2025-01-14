from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Users table
class User(db.Model):
    __tablename__ = "Users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    nickname = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    salt = db.Column(db.String(255), unique=True, nullable=False)  

    scan_history_products = db.relationship("ScanHistory", back_populates="user", lazy="subquery")
    reviews = db.relationship("Review", back_populates="user", lazy="subquery")

# Products table
class Product(db.Model):
    __tablename__ = "Products"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_barcode = db.Column(db.String(255), unique=True, nullable=False)
    product_name = db.Column(db.String(255), unique=True, nullable=False)
    product_description = db.Column(db.Text, nullable=False)
    product_image = db.Column(db.String(255), nullable=False)

    reviews = db.relationship("Review", back_populates="product", lazy="subquery")
    scan_history_users = db.relationship("ScanHistory", back_populates="product", lazy="subquery")


# Shops table
class Shop(db.Model):
    __tablename__ = "Shops"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    shop_name = db.Column(db.String(255), unique=True, nullable=False)

    reviews = db.relationship("Review", back_populates="shop", lazy="subquery")


# Reviews table
class Review(db.Model):
    __tablename__ = "Reviews"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    reviews_user_fk = db.Column(db.Integer, db.ForeignKey("Users.id", onupdate="CASCADE", ondelete="SET NULL"))
    review_product_fk = db.Column(db.Integer, db.ForeignKey("Products.id", onupdate="CASCADE", ondelete="RESTRICT"), nullable=False)
    review_grade = db.Column(db.Integer, nullable=False)
    review_title = db.Column(db.String(255), nullable=False)
    review_description = db.Column(db.Text, nullable=False)
    review_price = db.Column(db.Numeric(precision=10, scale=2), nullable=False)
    review_shop_fk = db.Column(db.Integer, db.ForeignKey("Shops.id", onupdate="CASCADE", ondelete="RESTRICT"))
    review_timestamp = db.Column(db.DateTime, nullable=False, server_default=db.func.now())

    product = db.relationship("Product", back_populates="reviews", lazy="joined")
    media = db.relationship("ReviewMedia", back_populates="review", lazy="joined")
    shop = db.relationship("Shop", back_populates="reviews", lazy="joined")
    user = db.relationship("User", back_populates="reviews", lazy="joined")


# Review Media table
class ReviewMedia(db.Model):
    __tablename__ = "Review_media"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    media_review_fk = db.Column(db.Integer, db.ForeignKey("Reviews.id", onupdate="CASCADE", ondelete="RESTRICT"), nullable=False)
    media_path = db.Column(db.String(255), nullable=False)

    review = db.relationship("Review", back_populates="media", lazy="joined")


# Scan History table - we are storing only the last scan of a specific product in DB (if such product was already scanned - its timestamp is updated)
class ScanHistory(db.Model):
    __tablename__ = "Scan_history"
    scan_history_user_fk = db.Column(db.Integer, db.ForeignKey("Users.id", onupdate="CASCADE", ondelete="RESTRICT"), primary_key=True, nullable=False)
    scan_history_product_fk = db.Column(db.Integer, db.ForeignKey("Products.id", onupdate="CASCADE", ondelete="RESTRICT"), primary_key=True, nullable=False)
    scan_timestamp = db.Column(db.DateTime, nullable=False, server_default=db.func.now())

    product = db.relationship("Product", back_populates="scan_history_users", lazy="joined")
    user = db.relationship("User", back_populates="scan_history_products", lazy="subquery")
    
