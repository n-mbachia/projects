import os
from flask import Flask, render_template
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_ckeditor import CKEditor
from models import db, User
from blueprint import blueprint
from dotenv import load_dotenv


# Load enviroment variabbles from .env file
load_dotenv()

app = Flask(__name__)

# Configaration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI', 'sqlite:///your_database.db')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your_default_secret_key')
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

if __name__ == '__main__':
    app.run(port=5000, debug=True)
