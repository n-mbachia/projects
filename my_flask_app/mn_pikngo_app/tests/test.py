import os
import tempfile
import pytest
from mn_pikngo_app import create_app, db
from my_flask_app.mn_pikngo_app.models import Content, User

@pytest.fixture
def client():
    """Create a test client and set up a test database."""
    app = create_app()
    db_fd, db_path = tempfile.mkstemp()
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['TESTING'] = True
    app.config['DEBUG'] = False

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            # Create a test admin user
            admin = User(email='admin@example.com', password='password')
            db.session.add(admin)
            db.session.commit()
        yield client

    os.close(db_fd)
    os.unlink(db_path)

def log_result(test_name, result):
    """Log the result of a test case."""
    print(f"\nRunning {test_name}...")
    print(f"Result: {'Passed' if result else 'Failed'}")

def test_admin_login(client):
    """Test the admin login functionality."""
    result = False
    try:
        response = client.post('/admin/login', data={'email': 'admin@example.com', 'password': 'password'})
        result = b'Login successful!' in response.data
    finally:
        log_result('test_admin_login', result)

def test_admin_login_invalid_credentials(client):
    """Test login with invalid credentials."""
    result = False
    try:
        response = client.post('/admin/login', data={'email': 'admin@example.com', 'password': 'wrongpassword'})
        result = b'Login Unsuccessful' in response.data
    finally:
        log_result('test_admin_login_invalid_credentials', result)

def test_admin_dashboard(client):
    """Test accessing the admin dashboard after logging in."""
    result = False
    try:
        response = client.post('/admin/login', data={'email': 'admin@example.com', 'password': 'password'}, follow_redirects=True)
        result = b'Admin Dashboard' in response.data
    finally:
        log_result('test_admin_dashboard', result)

def test_unauthorized_access(client):
    """Test redirecting unauthorized users."""
    result = False
    try:
        response = client.get('/admin/dashboard', follow_redirects=True)
        result = b'Login' in response.data  # Assuming 'Login' is a part of the login page
    finally:
        log_result('test_unauthorized_access', result)

def test_content_creation(client):
    """Test content creation functionality."""
    result = False
    try:
        client.post('/admin/login', data={'email': 'admin@example.com', 'password': 'password'}, follow_redirects=True)
        response = client.post('/admin/create_content', data={'title': 'Test Content', 'body': 'Test Body'}, follow_redirects=True)
        result = b'Content added successfully' in response.data
    finally:
        log_result('test_content_creation', result)

def test_content_creation_missing_fields(client):
    """Test content creation with missing fields."""
    result = False
    try:
        client.post('/admin/login', data={'email': 'admin@example.com', 'password': 'password'}, follow_redirects=True)
        response = client.post('/admin/create_content', data={'title': ''}, follow_redirects=True)
        result = b'Field must not be empty' in response.data  # Adjust based on your validation message
    finally:
        log_result('test_content_creation_missing_fields', result)

def test_content_edit(client):
    """Test content editing functionality."""
    result = False
    try:
        client.post('/admin/login', data={'email': 'admin@example.com', 'password': 'password'}, follow_redirects=True)
        # Create a dummy content
        content = Content(title='Test Content', body='Test Body')
        db.session.add(content)
        db.session.commit()
        response = client.post(f'/admin/edit_content/{content.id}', data={'title': 'Updated Content', 'body': 'Updated Body'}, follow_redirects=True)
        result = b'Content updated successfully' in response.data
    finally:
        log_result('test_content_edit', result)

def test_content_deletion(client):
    """Test content deletion functionality."""
    result = False
    try:
        client.post('/admin/login', data={'email': 'admin@example.com', 'password': 'password'}, follow_redirects=True)
        # Create a dummy content
        content = Content(title='Test Content', body='Test Body')
        db.session.add(content)
        db.session.commit()
        response = client.post(f'/admin/delete_content/{content.id}', follow_redirects=True)
        result = b'Content deleted successfully' in response.data
        # Ensure the content is actually deleted
        result = result and Content.query.get(content.id) is None
    finally:
        log_result('test_content_deletion', result)

def test_index(client):
    """Test the index page."""
    result = False
    try:
        response = client.get('/')
        result = b'Latest Posts' in response.data
    finally:
        log_result('test_index', result)

def test_post(client):
    """Test viewing a single post."""
    result = False
    try:
        # Create a dummy content
        content = Content(title='Test Content', body='Test Body')
        db.session.add(content)
        db.session.commit()
        response = client.get(f'/post/{content.id}')
        result = b'Test Content' in response.data and b'Test Body' in response.data
    finally:
        log_result('test_post', result)
