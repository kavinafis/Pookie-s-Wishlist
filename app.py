from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
@app.before_first_request
def create_tables():
    db.create_all()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
import os

DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///wishlist.db')
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'

db = SQLAlchemy(app)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Wishlist item model
class WishlistItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    link = db.Column(db.String(300), nullable=True)
    image_filename = db.Column(db.String(300), nullable=True)
    purchased = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@app.route('/')
def index():
    items = WishlistItem.query.all()
    user_id = session.get('user_id')
    return render_template('wishlist.html', items=items, user_id=user_id)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            flash('Logged in successfully.', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logged out successfully.', 'success')
    return redirect(url_for('index'))

@app.route('/add', methods=['GET', 'POST'])
def add_item():
    if 'user_id' not in session:
        flash('Please login to add items.', 'warning')
        return redirect(url_for('login'))
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        link = request.form['link']
        image = request.files.get('image')
        image_filename = None
        if image and image.filename != '':
            image_filename = image.filename
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
        new_item = WishlistItem(
            name=name,
            description=description,
            link=link,
            image_filename=image_filename,
            user_id=session['user_id']
        )
        db.session.add(new_item)
        db.session.commit()
        flash('Item added to wishlist.', 'success')
        return redirect(url_for('index'))
    return render_template('add_item.html')

@app.route('/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_item(item_id):
    if 'user_id' not in session:
        flash('Please login to edit items.', 'warning')
        return redirect(url_for('login'))
    item = WishlistItem.query.get_or_404(item_id)
    if item.user_id != session['user_id']:
        flash('You do not have permission to edit this item.', 'danger')
        return redirect(url_for('index'))
    if request.method == 'POST':
        item.name = request.form['name']
        item.description = request.form['description']
        item.link = request.form['link']
        image = request.files.get('image')
        if image and image.filename != '':
            image_filename = image.filename
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
            item.image_filename = image_filename
        db.session.commit()
        flash('Item updated successfully.', 'success')
        return redirect(url_for('index'))
    return render_template('edit_item.html', item=item)

@app.route('/delete/<int:item_id>', methods=['POST'])
def delete_item(item_id):
    if 'user_id' not in session:
        flash('Please login to delete items.', 'warning')
        return redirect(url_for('login'))
    item = WishlistItem.query.get_or_404(item_id)
    if item.user_id != session['user_id']:
        flash('You do not have permission to delete this item.', 'danger')
        return redirect(url_for('index'))
    db.session.delete(item)
    db.session.commit()
    flash('Item deleted successfully.', 'success')
    return redirect(url_for('index'))

@app.route('/toggle_purchased/<int:item_id>', methods=['POST'])
def toggle_purchased(item_id):
    if 'user_id' not in session:
        flash('Please login to update items.', 'warning')
        return redirect(url_for('login'))
    item = WishlistItem.query.get_or_404(item_id)
    if item.user_id != session['user_id']:
        flash('You do not have permission to update this item.', 'danger')
        return redirect(url_for('index'))
    item.purchased = not item.purchased
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        if not os.path.exists('wishlist.db'):
            db.create_all()
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)
