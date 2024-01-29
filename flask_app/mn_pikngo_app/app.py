#!/usr/bin/python3 

from flask import Flask, render_template, redirect, url_for, request, session, flash, g
import sqlite3
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['DATABASE'] = 'site.db'

# Dummy admin user (for demonstration purposes only)
admin_user = {'username': 'admin', 'password': 'password'}

def create_content_table():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS content (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            body TEXT NOT NULL
        )
    ''')
    conn.commit()

def create_admin_table():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'db'):
        g.db.close()

class ContentForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    body = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Submit')

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

@app.route('/admin/dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    form = ContentForm()

    if form.validate_on_submit():
        title = form.title.data
        body = form.body.data

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO content (title, body) VALUES (?, ?)', (title, body))
        conn.commit()

        flash('Content added successfully', 'success')
        return redirect(url_for('admin_dashboard'))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM content')
    contents = cursor.fetchall()

    return render_template('admin_dashboard.html', form=form, contents=contents)

@app.route('/')
def index():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM content ORDER BY id DESC')
    posts = cursor.fetchall()

    latest_posts = posts[:2]
    older_posts = posts[2:]

    return render_template('index.html', latest_posts=latest_posts, older_posts=older_posts)

@app.route('/admin/edit_content/<int:content_id>', methods=['GET', 'POST'])
def edit_content(content_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    form = ContentForm()

    if form.validate_on_submit():
        title = form.title.data
        body = form.body.data

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('UPDATE content SET title=?, body=? WHERE id=?', (title, body, content_id))
        conn.commit()

        flash('Content updated successfully', 'success')
        return redirect(url_for('admin_dashboard'))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM content WHERE id=?', (content_id,))
    content = cursor.fetchone()

    if content:
        form.title.data = content[1]
        form.body.data = content[2]
        return render_template('edit_content.html', form=form, content_id=content_id)
    else:
        flash('Content not found', 'danger')
        return redirect(url_for('admin_dashboard'))

@app.route('/post/<int:post_id>')
def post(post_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM content WHERE id = ?', (post_id,))
    post = cursor.fetchone()

    if post:
        return render_template('post.html', post=post)
    else:
        flash('Post not found', 'danger')
        return redirect(url_for('index'))

@app.route('/earlier_posts')
def earlier_posts():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM content ORDER BY id DESC')
    posts = cursor.fetchall()

    return render_template('earlier_posts.html', posts=posts)

if __name__ == '__main__':
    app.run(debug=True)

