from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///wishlist.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

class WishlistItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    price = db.Column(db.Float, nullable=True)
    category = db.Column(db.String(150), nullable=True)
    description = db.Column(db.Text, nullable=True)
    link = db.Column(db.String(300), nullable=True)
    image_filename = db.Column(db.String(300), nullable=True)
    purchased = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

if __name__ == '__main__':
    with app.app_context():
        if not os.path.exists('migrations'):
            from flask_migrate import init, migrate, upgrade
            init()
            migrate(message="Initial migration.")
            upgrade()
        else:
            from flask_migrate import migrate, upgrade
            migrate(message="Database schema update.")
            upgrade()
