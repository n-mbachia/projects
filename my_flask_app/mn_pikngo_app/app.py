import os
from flask import Flask, render_template
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_ckeditor import CKEditor
from mn_pikngo_app.models import db, User
from mn_pikngo_app.blueprint import blueprint

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///your_database.db'
app.config['SECRET_KEY'] = 'ae029fda8be2694c92b0c226e240669b5621a4b1fb47873d0bdd29070c2b18d45c0427aea11c19ca3fb21cc4ac2031d37aabd575536d117c8b23235c51f0bbbf'
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'media/uploads')
app.config['CKEDITOR_SERVE_LOCAL'] = True

# Initialize extensions
ckeditor = CKEditor(app)
csrf = CSRFProtect(app)
db.init_app(app)

# Configure login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'mn_pikngo_app.admin_login'  # Redirect to login if user is not authenticated

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Exempt CSRF protection for blueprint routes if necessary
csrf.exempt(blueprint)  # Use with caution

# Register the Blueprint
app.register_blueprint(blueprint, url_prefix='/')

########################
#### error handlers ####
########################


@app.errorhandler(401)
def unauthorized_page(error):
    return render_template("errors/401.html"), 401


@app.errorhandler(404)
def page_not_found(error):
    return render_template("errors/404.html"), 404


@app.errorhandler(500)
def server_error_page(error):
    return render_template("errors/500.html"), 500


if __name__ == '__main__':
    app.run(port=5000, debug=True)
