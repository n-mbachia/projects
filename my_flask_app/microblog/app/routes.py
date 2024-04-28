# app/routes.py

from flask import render_template, flash, redirect, url_for
from app import app
from app.forms import LoginForm

# Home route
@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Home')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}, remeber_me{}'.format(
            form.username.data, form.remember_me.data))
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)
