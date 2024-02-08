# app.py

from logging import DEBUG
from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import secrets
from flask_migrate import Migrate
from forms import ContentForm

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'  # SQLite database URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Turn off Flask-SQLAlchemy event tracking
# Accessing app.config
# upload_folder = app.config.get('UPLOAD_FOLDER', 'flask_app/mn_pikngo_app/static/uploads')
app.config['UPLOAD_FOLDER'] = 'flask_app/mn_pikngo_app/static/uploads'


# app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')  # Set the UPLOAD_FOLDER to static/uploads'path/to/your/upload/folder'
# flask_app/mn_pikngo_app/static/uploads
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    is_superuser = db.Column(db.Boolean, default=False)

@app.route('/admin/register', methods=['GET', 'POST'])
def register():
    from werkzeug.security import generate_password_hash
    import os
    from forms import AdminSignupForm  # Import your WTForms AdminSignupForm
    
    form = AdminSignupForm()  # Create an instance of the form
    
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Check if email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email address already exists. Please use a different email.', 'error')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)

        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('User registered successfully!', 'success')
        return redirect(url_for('admin_login'))

    return render_template('admin_register.html', form=form)  # Pass the form to the template context


# Dummy admin user (for demonstration purposes only)
admin_user = {'username': 'admin', 'password': 'password'}

# Content model
class Content(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    body = db.Column(db.Text, nullable=False)
    image_filename = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# Image upload route

UPLOAD_FOLDER = 'flask_app/mn_pikngo_app/static/uploads'

@app.route('/upload_image', methods=['POST'])
def upload_image():
    if request.method == 'POST':
        # Get the image file from the request
        image_file = request.files['image']
        if image_file:
            # Get the filename
            filename = secure_filename(image_file.filename)
            
            # Construct the file path
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            
            # Check if the directory exists, create if not
            if not os.path.exists(UPLOAD_FOLDER):
                os.makedirs(UPLOAD_FOLDER)
            
            # Save the image file
            image_file.save(file_path)
            
            return 'Image uploaded successfully'
    
    return 'No image file provided'



# Initialize the database
def init_db():
    with app.app_context():
        db.create_all()

# Admin login route
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username == admin_user['username'] and password == admin_user['password']:
            session['admin_logged_in'] = True
            flash('Logged in successfully', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid username or password', 'danger')

    return render_template('admin_login.html')

# Admin dashboard route for content creation
UPLOAD_FOLDER = 'flask_app/mn_pikngo_app/static/uploads'

# Check if the uploads directory exists, if not, create it
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
    
@app.route('/admin/dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    form = ContentForm()

    if form.validate_on_submit():
        title = form.title.data
        body = form.body.data
        
        # Handle image upload
        if 'image' in request.files:
            image = request.files['image']
            if image.filename != '':
                filename = secure_filename(image.filename)
                image.save(os.path.join(UPLOAD_FOLDER, filename))
            else:
                filename = None
        else:
            filename = None

        new_content = Content(title=title, body=body, image_filename=filename)
        db.session.add(new_content)
        db.session.commit()

        flash('Content added successfully', 'success')
        return redirect(url_for('admin_dashboard'))

    contents = Content.query.all()

    return render_template('admin_dashboard.html', form=form, contents=contents)

# Index route
@app.route('/')
def index():
    latest_posts = Content.query.order_by(Content.created_at.desc()).limit(2).all()
    older_posts = Content.query.order_by(Content.created_at.desc()).offset(2).all()

    return render_template('index.html', latest_posts=latest_posts, older_posts=older_posts)

# Admin dashboard route for content creation
@app.route('/admin/edit_content/<int:content_id>', methods=['GET', 'POST'])
def edit_content(content_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    form = ContentForm()
    content = Content.query.get(content_id)

    if form.validate_on_submit():
        content.title = form.title.data
        content.body = form.body.data

        # Handle image upload
        image = form.image.data
        if image:
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            content.image_filename = filename

        db.session.commit()

        flash('Content updated successfully', 'success')
        return redirect(url_for('admin_dashboard'))

    if content:
        form.title.data = content.title
        form.body.data = content.body
        return render_template('edit_content.html', form=form, content_id=content_id)
    else:
        flash('Content not found', 'danger')
        return redirect(url_for('admin_dashboard'))

# Single post route
@app.route('/post/<int:post_id>')
def post(post_id):
    post = Content.query.get(post_id)
    content = post

    if post:
        return render_template('post.html', post=post, content=content)
    else:
        flash('Post not found', 'danger')
        return redirect(url_for('index'))

# Earlier posts route
@app.route('/earlier_posts')
def earlier_posts():
    posts = Content.query.order_by(Content.created_at.desc()).all()

    return render_template('earlier_posts.html', posts=posts)

HOST = 'localhost'  # Replace 'localhost' with the actual host value

PORT = 5000  # Replace with the desired port number

if __name__ == '__main__':
    init_db()
    app.run(debug=DEBUG, host=HOST, port=PORT)
    app.app_context()

# Route to delete a post
UPLOAD_FOLDER = 'flask_app/mn_pikngo_app/static/uploads'

@app.route('/delete_post/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    # Retrieve the post from the database
    post = Content.query.get_or_404(post_id)

    # Check if the post has an associated image file
    if post.image_filename:
        # Construct the path to the image file
        image_path = os.path.join(UPLOAD_FOLDER, post.image_filename)
        
        # Check if the image file exists
        if os.path.exists(image_path):
            # Delete the image file
            os.remove(image_path)

    # Delete the post from the database
    db.session.delete(post)
    db.session.commit()

    # Redirect to the admin dashboard with a success message
    flash('Post deleted successfully', 'success')
    return redirect(url_for('admin_dashboard'))

"""
@app.route('/earlier_posts')
@app.route('/post/<int:post_id>')
@app.route('/admin/edit_content/<int:content_id>', methods=['GET', 'POST'])
@app.route('/')
@app.route('/admin/dashboard', methods=['GET', 'POST'])
@app.route('/admin/login', methods=['GET', 'POST'])
@app.route('/post/<int:post_id>/delete', methods=['POST'])




"""