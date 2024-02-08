# app.py

from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileSize
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import secrets
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'  # SQLite database URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Turn off Flask-SQLAlchemy event tracking
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')  # Set the UPLOAD_FOLDER to static/uploads'path/to/your/upload/folder'
app.config['GALLERY_UPLOAD_FOLDER'] = os.path.join('static', 'gallery_uploads')

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Define allowed file types
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Dummy admin user (for demonstration purposes only)
admin_user = {'username': 'admin', 'password': 'password'}

# Content model
class Content(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    body = db.Column(db.Text, nullable=False)
    image_filename = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Example Form for Content Creation
class ContentForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    body = TextAreaField('Content', validators=[DataRequired()])
    image = FileField('Upload Image', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif']), FileSize(max_size=2 * 1024 * 1024)])  # 2 MB limit
    submit = SubmitField('Submit')

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
@app.route('/admin/dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    form = ContentForm()

    if form.validate_on_submit():
        title = form.title.data
        body = form.body.data
        
        # Handle image upload
        image = form.image.data
        if image:
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
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

# Function to check if the file extension is allowed
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Modify route to handle gallery image upload
@app.route('/admin/upload_image', methods=['POST'])
def upload_image():
    if request.method == 'POST':
        if 'gallery_uploads' not in request.files:
            flash('No file part', 'error')
            return redirect(request.url)
        file = request.files['gallery_uploads']
        if file.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash('File uploaded successfully', 'success')
            return redirect(request.url)
        else:
            flash('Invalid file type', 'error')
            return redirect(request.url)
    else:
        flash('Method not allowed', 'error')
        return redirect(request.url)
    

@app.route('/admin/delete_image/<filename>', methods=['GET'])
def delete_image(filename):
    try:
        os.remove(os.path.join(app.config['GALLERY_UPLOAD_FOLDER'], filename))
        flash('Image deleted successfully', 'success')
    except FileNotFoundError:
        flash('Image not found', 'error')
    return redirect(request.referrer)

# Single post route
@app.route('/post/<int:post_id>')
def post(post_id):
    post = Content.query.get(post_id)

    if post:
        return render_template('post.html', post=post)
    else:
        flash('Post not found', 'danger')
        return redirect(url_for('index'))

# Earlier posts route
@app.route('/earlier_posts')
def earlier_posts():
    posts = Content.query.order_by(Content.created_at.desc()).all()

    return render_template('earlier_posts.html', posts=posts)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)


"""
# Admin Signup Logic and form
from app import db
from werkzeug.security import generate_password_hash

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, ValidationError
from wtforms.validators import DataRequired, EqualTo
from wtforms import StringField, PasswordField, SubmitField, ValidationError, TextAreaField, IntegerField, FileField, RadioField, BooleanField

class AdminSignupForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    verification_code = StringField('Verification Code', validators=[DataRequired()])
    submit = SubmitField('Sign Up')

    def validate_verification_code(self, field):
        if field.data != '123456':  # Replace '123456' with your actual verification code
            raise ValidationError('Invalid verification code')


# class AdminUser(db.Model):
#     extend_existing=True
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(255), unique=True, nullable=False)
#     password = db.Column(db.String(255), nullable=False)

#     def __repr__(self):
#         return f"AdminUser(username='{self.username}')"


# # Admin Signup
# class AdminSignupForm(FlaskForm):
#     username = StringField('Username', validators=[DataRequired()])
#     password = PasswordField('Password', validators=[DataRequired()])
#     confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
#     verification_code = StringField('Verification Code', validators=[DataRequired()])
#     submit = SubmitField('Sign Up')

#     def validate_verification_code(self, field):
#         if field.data != '123456':  # Replace '123456' with your actual verification code
#             raise ValidationError('Invalid verification code')

# @app.route('/admin/signup', methods=['GET', 'POST'])
# def admin_signup():
#     form = AdminSignupForm()

#     if form.validate_on_submit():
#         username = form.username.data
#         password = form.password.data
#         confirm_password = form.confirm_password.data
#         verification_code = form.verification_code.data

#         # Check if the verification code is valid
#         if verification_code != '123456':  # Replace '123456' with your actual verification code
#             flash('Invalid verification code', 'danger')
#             return redirect(url_for('admin_signup'))

#         # Check if the password and confirm_password match
#         if password != confirm_password:
#             flash('Passwords do not match', 'danger')
#         else:
#             # Save the admin user to the database or perform any other necessary actions
#             hashed_password = generate_password_hash(password, method='sha256')
#             admin_user = AdminUser(username=username, password=hashed_password)
#             db.session.add(admin_user)
#             db.session.commit()
            
#             flash('Admin user created successfully', 'success')
#             return redirect(url_for('admin_login'))

#     return render_template('admin_signup.html', form=form)


"""