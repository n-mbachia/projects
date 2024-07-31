# forms.py

from flask_wtf import FlaskForm
from wtforms import FileField, StringField, PasswordField, SubmitField, TextAreaField, ValidationError
from wtforms.validators import DataRequired, Email, EqualTo
from flask_wtf.file import FileAllowed, FileSize, FileRequired
import uuid

class AdminSignupForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    verification_code = StringField('Verification Code', validators=[DataRequired()])
    submit = SubmitField('Sign Up')

    def validate_verification_code(self, field):
        if field.data != '123456':  # Replace '123456' with your actual verification code
            raise ValidationError('Invalid verification code')
        

class ContentForm(FlaskForm):
    id = StringField('ID', default=lambda: str(uuid.uuid4()))  # Generate a unique ID by default
    title = StringField('Title', validators=[DataRequired()])
    body = TextAreaField('Content', validators=[DataRequired()])  # This will be replaced by CKEditor in the template
    image = FileField('Upload Image', validators=[
        FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Images only!'),
        FileRequired('File was not selected')
    ])
    submit = SubmitField('Submit')
    author = StringField('Author')

class UpdateContentForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    body = TextAreaField('Content', validators=[DataRequired()])  # This will be replaced by CKEditor in the template
    image = FileField('Update Image', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif']), FileSize(max_size=2 * 1024 * 1024)])  # 2 MB limit
    submit = SubmitField('Update')
    author = StringField('Author')



class AdminLoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class CommentForm(FlaskForm):
    body = TextAreaField('Comment', validators=[DataRequired()])
    submit = SubmitField('Post Comment')


class DeleteContentForm(FlaskForm):
    submit = SubmitField('Delete')

class SearchForm(FlaskForm):
    search = StringField('Search', validators=[DataRequired()])
    submit = SubmitField('Search')

class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    message = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Send Message')

class ResetPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Reset Password')

class NewPasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired()])
    confirm_new_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('new_password', message='Passwords must match')])
    submit = SubmitField('Reset Password')

class UpdateProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Update Profile')

class UpdateProfilePictureForm(FlaskForm):
    profile_picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif']), FileSize(max_size=2 * 1024 * 1024)])  # 2 MB limit
    submit = SubmitField('Update Profile Picture')
