from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://admin:password@localhost/mn_pikngo_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

import secrets
secret_key = secrets.token_hex(16)
app.secret_key = secret_key

db = SQLAlchemy(app)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"

@app.route('/')
def index():
    posts = Post.query.order_by(Post.date_posted.desc()).all()
    return render_template('index.html', posts=posts)

@app.route('/post/<int:post_id>')
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', post=post)

@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        if not title or not content:
            flash('Please fill out all fields', 'error')
        else:
            new_post = Post(title=title, content=content)
            try:
                db.session.add(new_post)
                db.session.commit()
                flash('Post created successfully', 'success')
                return redirect(url_for('index'))
            except IntegrityError:
                db.session.rollback()
                flash('An error occurred while creating the post', 'error')
    return render_template('create.html')

if __name__ == '__main__':
    app.run(debug=True)
