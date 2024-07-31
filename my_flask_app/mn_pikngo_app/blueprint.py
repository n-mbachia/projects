from flask import Blueprint
from flask_ckeditor import CKEditor

blueprint = Blueprint('mn_pikngo_app', __name__)
ckeditor_bp = CKEditor()  # Initialize CKEditor Blueprint

# Import views here to avoid circular import issues
import views
