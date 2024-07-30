#!/usr/bin/env python
import os
from flask import (
    current_app,
    jsonify,
    redirect,
    session,
    url_for,
    flash,
    request,
    render_template
)
from flask_login import login_user, login_required, current_user, logout_user
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from mn_pikngo_app.models import db, User, Content
from mn_pikngo_app.blueprint import blueprint
from mn_pikngo_app.forms import (
    AdminSignupForm,
    AdminLoginForm,
    ContentForm,
    UpdateContentForm,
    DeleteContentForm,
    SearchForm,
    ContactForm,
    ResetPasswordForm,
    NewPasswordForm,
    UpdateProfileForm,
    UpdateProfilePictureForm
)

from flask import send_from_directory
@blueprint.route('/media/<filename>')
def media(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

@blueprint.route("/admin/create_post", methods=["GET", "POST"])
@login_required
def create_post():
    form = ContentForm()
    if form.validate_on_submit():
        title = form.title.data
        body = form.body.data

        filename = None
        if form.image.data:
            image = form.image.data
            filename = secure_filename(image.filename)
            upload_folder = os.path.join(current_app.config["UPLOAD_FOLDER"], 'uploads')

            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)

            file_path = os.path.join(upload_folder, filename)
            image.save(file_path)

        new_content = Content(title=title, body=body, image_filename=filename, author=form.author.data)
        db.session.add(new_content)
        db.session.commit()

        flash("Post created successfully!", "success")
        return redirect(url_for("mn_pikngo_app.admin_dashboard"))

    return render_template('create_post.html', form=form)


# Define the upload route for CKEditor
@blueprint.route('/upload', methods=['POST'])
def upload():
    if 'upload' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['upload']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    if file:
        filename = secure_filename(file.filename)
        upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'ckeditor/uploads')

        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)

        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)

        url = url_for('static', filename='ckeditor/uploads/' + filename)
        return jsonify({'url': url, 'filename': filename})


@blueprint.route("/admin/register", methods=["GET", "POST"])
def admin_register():
    form = AdminSignupForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email address already exists. Please use a different email.", "error")
            return redirect(url_for("mn_pikngo_app.admin_login"))

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash("User registered successfully! You can now log in.", "success")
        return redirect(url_for("mn_pikngo_app.admin_login"))

    return render_template("admin_register.html", form=form)

@blueprint.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    form = AdminLoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash("Login successful!", "success")
            next_page = request.args.get("next") or url_for("mn_pikngo_app.admin_dashboard")
            return redirect(next_page)
        else:
            flash("Login Unsuccessful. Please check email and password", "error")
    return render_template("admin_login.html", form=form)

@blueprint.route("/admin/dashboard", methods=["GET", "POST"])
@login_required
def admin_dashboard():
    form = ContentForm()
    if form.validate_on_submit():
        title = form.title.data
        body = form.body.data

        filename = None
        if "image" in request.files:
            image = request.files["image"]
            if image.filename != "":
                filename = secure_filename(image.filename)
                upload_folder = os.path.join(current_app.config["UPLOAD_FOLDER"])

                # Ensure the directory exists
                if not os.path.exists(upload_folder):
                    try:
                        os.makedirs(upload_folder)
                    except PermissionError:
                        flash("Failed to create the directory. Permission denied.", "error")
                        return redirect(url_for("mn_pikngo_app.admin_dashboard"))

                file_path = os.path.join(upload_folder, filename)
                try:
                    image.save(file_path)
                except PermissionError:
                    flash("Failed to save the image. Permission denied.", "error")
                    return redirect(url_for("mn_pikngo_app.admin_dashboard"))

        new_content = Content(title=title, body=body, image_filename=filename)
        db.session.add(new_content)
        db.session.commit()

        flash("Content created successfully!", "success")
        return redirect(url_for("mn_pikngo_app.admin_dashboard"))

    contents = Content.query.all()
    return render_template('admin_dashboard.html', form=form, contents=contents)


@blueprint.route("/admin/logout")
@login_required
def admin_logout():
    session.clear()
    flash("You have been logged out", "info")
    return redirect(url_for("mn_pikngo_app.admin_login"))


@blueprint.route("/admin/edit_content/<int:content_id>", methods=["GET", "POST"])
@blueprint.route("/admin/create_content", methods=["GET", "POST"])
@login_required
def edit_content(content_id):
    if not session.get("admin_logged_in"):
        return redirect(url_for("mn_pikngo_app.admin_login"))

    form = UpdateContentForm()
    
    if content_id:
        content = session.get(Content, content_id)
    else:
        content = None

    if form.validate_on_submit():
        if content:
            content.title = form.title.data
            content.body = form.body.data

            image = form.image.data
            if image:
                filename = secure_filename(image.filename)
                file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)

                # Ensure upload directory exists
                if not os.path.exists(current_app.config["UPLOAD_FOLDER"]):
                    os.makedirs(current_app.config["UPLOAD_FOLDER"])

                try:
                    image.save(file_path)
                    content.image_filename = filename
                except PermissionError:
                    flash("Failed to save the image. Permission denied.", "error")
                    return redirect(url_for("mn_pikngo_app.edit_content", content_id=content_id))

            db.session.commit()
            flash("Content updated successfully", "success")
            return redirect(url_for("mn_pikngo_app.admin_dashboard"))

    if content:
        form.title.data = content.title
        form.body.data = content.body
        return render_template("edit_content.html", form=form, content_id=content_id)
    else:
        flash("Content not found", "danger")
        return redirect(url_for("mn_pikngo_app.admin_dashboard"))
@blueprint.route("/admin/delete_content/<int:content_id>", methods=["POST"])
def delete_content(content_id):
    if not session.get("admin_logged_in"):
        return redirect(url_for("mn_pikngo_app.admin_login"))

    content = Content.query.get_or_404(content_id)
    db.session.delete(content)
    db.session.commit()
    flash("Post deleted successfully", "success")
    return redirect(url_for("admin_dashboard"))


@blueprint.route("/delete_post/<int:post_id>", methods=["POST"])
def delete_post(post_id):
    post = Content.query.get_or_404(post_id)
    if post.image_filename:
        image_path = os.path.join(app.config["UPLOAD_FOLDER"], post.image_filename)
        if os.path.exists(image_path):
            os.remove(image_path)
    db.session.delete(post)
    db.session.commit()
    flash("Post deleted successfully", "success")
    return redirect(url_for("admin_dashboard"))


@blueprint.route("/")
def index():
    return render_template("index.html")


@blueprint.route("/menu")
def download_menu():
    menu_path = "static/pikngo_menu.pdf"
    filename = "pikngo_menu.pdf"
    return send_file(menu_path, as_attachment=True)


@blueprint.route("/post/<int:post_id>")
def post(post_id):
    post = Content.query.get(post_id)
    if post:
        return render_template("post.html", post=post)
    else:
        flash("Post not found", "danger")
        return redirect(url_for("mn_pikngo_app.index"))


@blueprint.route("/earlier_posts")
def earlier_posts():
    posts = Content.query.order_by(Content.created_at.desc()).all()
    return render_template("earlier_posts.html", posts=posts)



@blueprint.route("/search", methods=["GET", "POST"])
def search():
    form = SearchForm()
    if form.validate_on_submit():
        query = form.query.data
        results = Content.query.filter(
            Content.title.contains(query) | Content.body.contains(query)
        ).all()
        return render_template("search_results.html", form=form, results=results)
    return render_template("search.html", form=form)


@blueprint.route("/contact", methods=["GET", "POST"])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        # Handle contact form submission (e.g., send email)
        flash("Message sent successfully!", "success")
        return redirect(url_for("mn_pikngo_app.index"))
    return render_template("contact.html", form=form)


@blueprint.route("/reset_password", methods=["GET", "POST"])
def reset_password():
    form = ResetPasswordForm()
    if form.validate_on_submit():
        email = form.email.data
        user = User.query.filter_by(email=email).first()
        if user:
            # Send reset password email
            flash("Password reset email sent!", "success")
        else:
            flash("Email not found", "danger")
    return render_template("reset_password.html", form=form)


@blueprint.route("/update_profile", methods=["GET", "POST"])
def update_profile():
    if not session.get("admin_logged_in"):
        return redirect(url_for("mn_pikngo_app.admin_login"))

    form = UpdateProfileForm()
    user = User.query.get(session["user_id"])

    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        db.session.commit()
        flash("Profile updated successfully", "success")
        return redirect(url_for("admin_dashboard"))

    form.username.data = user.username
    form.email.data = user.email
    return render_template("update_profile.html", form=form)


@blueprint.route("/admin/update_profile_picture", methods=["GET", "POST"])
def update_profile_picture():
    if not session.get("admin_logged_in"):
        return redirect(url_for("mn_pikngo_app.admin_login"))

    form = UpdateProfilePictureForm()
    user = User.query.get(session["user_id"])

    if form.validate_on_submit():
        if "picture" in request.files:
            picture = request.files["picture"]
            if picture.filename != "":
                filename = secure_filename(picture.filename)
                picture.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
                user.profile_picture = filename
                db.session.commit()
                flash("Profile picture updated successfully", "success")
                return redirect(url_for("admin_dashboard"))

    return render_template("update_profile_picture.html", form=form)


@blueprint.route("/admin/delete_account", methods=["POST"])
@login_required
def delete_account():
    # Check if a user is logged in
    if not current_user.is_authenticated:
        flash("You need to log in first.", "warning")
        return redirect(url_for("mn_pikngo_app.admin_login"))

    # Proceed with account deletion
    user = User.query.get(current_user.id)
    if user:
        db.session.delete(user)
        db.session.commit()
        logout_user()  # Log out the user after deletion
        flash("Account deleted successfully", "success")
        return redirect(url_for("mn_pikngo_app.admin_login"))
    else:
        flash("User not found", "danger")
        return redirect(url_for("mn_pikngo_app.admin_dashboard"))


@blueprint.route("/admin/reset_password", methods=["GET", "POST"])
def reset_password_request():
    form = ResetPasswordForm()
    if form.validate_on_submit():
        email = form.email.data
        # Handle password reset logic here (e.g., send reset email)
        flash("Password reset instructions have been sent to your email.", "info")
        return redirect(url_for("mn_pikngo_app.index"))
    return render_template("reset_password_request.html", form=form)


@blueprint.route("/admin/set_new_password/<token>", methods=["GET", "POST"])
def set_new_password(token):
    form = NewPasswordForm()
    if form.validate_on_submit():
        current_password = form.current_password.data
        new_password = form.new_password.data
        # Handle password change logic here (e.g., verify token and update password)
        flash("Your password has been updated.", "success")
        return redirect(url_for("mn_pikngo_app.index"))
    return render_template(
        "new_password.html", form=form
    )  # Render a template for setting new password
