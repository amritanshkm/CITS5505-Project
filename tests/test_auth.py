import pytest
import io
from app.models import User
from app import db
from bs4 import BeautifulSoup

def test_password_hashing(app):
    """UNIT TEST 1: Test that the password hashing mathematical logic is robust and unique."""
    u = User(nickname='TestUser', email='test@test.com')
    u.set_password('my_secure_password')
    # Assert hash is created and is not plaintext
    assert u.password_hash is not None
    assert u.password_hash != 'my_secure_password'
    
    # Assert verification logic works
    assert u.check_password('my_secure_password') is True
    assert u.check_password('wrong_password') is False

def test_register_commits_to_db(client, app):
    """UNIT TEST 2: Test that successful registration pushes an entity to the live ORM database."""
    response = client.post('/register', data={
        'nickname': 'NewUser',
        'email': 'new@user.com',
        'password': 'password123',
        'confirm_password': 'password123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    
    # Check DB directly!
    with app.app_context():
        u = User.query.filter_by(email='new@user.com').first()
        assert u is not None
        assert u.nickname == 'NewUser'

def test_register_duplicate_email_fails(client, app):
    """UNIT TEST 3: Test that the WTF Form explicitly rejects a duplicated email via ValidationError intercept."""
    # Pre-inject a user
    with app.app_context():
        u = User(nickname='Alpha', email='alpha@test.com')
        u.set_password('mypassword')
        db.session.add(u)
        db.session.commit()
        
    # Attempt duplicate registration
    response = client.post('/register', data={
        'nickname': 'Beta',
        'email': 'alpha@test.com', # Duplicate email
        'password': 'password123',
        'confirm_password': 'password123'
    })
    
    # Because of fail, it should NOT redirect, but render template with error
    assert b'Please use a different email address.' in response.data
    
    with app.app_context():
        users_count = User.query.count()
        assert users_count == 1  # Still only 1 user!

def test_login_success_handles_session(client, app):
    """UNIT TEST 4: Test that a valid login successfully returns redirect and auth session info."""
    with app.app_context():
        u = User(nickname='LoginGuy', email='loginguy@test.com')
        u.set_password('mypassword')
        db.session.add(u)
        db.session.commit()
    
    response = client.post('/login', data={
        'email': 'loginguy@test.com',
        'password': 'mypassword'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Login successful!' in response.data

def test_login_failure_bad_password(client, app):
    """UNIT TEST 5: Test that invalid passwords intercept the request correctly."""
    with app.app_context():
        u = User(nickname='LoginGuy2', email='loginguy2@test.com')
        u.set_password('mypassword')
        db.session.add(u)
        db.session.commit()
    
    response = client.post('/login', data={
        'email': 'loginguy2@test.com',
        'password': 'WRONG_PASSWORD_123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Invalid email or password' in response.data

def test_avatar_upload_success(client, app):
    """UNIT TEST 6: Test that a valid avatar image is successfully uploaded and saved to DB."""
    with app.app_context():
        u = User(nickname='AvatarGuy', email='avatar@test.com')
        u.set_password('mypassword')
        db.session.add(u)
        db.session.commit()
    
    # Login first
    client.post('/login', data={'email': 'avatar@test.com', 'password': 'mypassword'}, follow_redirects=True)
    
    # Create a dummy image
    image_data = b'fake_image_data'
    data = {
        'profile-nickname': 'AvatarGuy',
        'profile-email': 'avatar@test.com',
        'profile-avatar': (io.BytesIO(image_data), 'test_avatar.jpg'),
        'profile-submit_profile': 'Update Profile'
    }
    
    response = client.post('/profile', data=data, content_type='multipart/form-data', follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Profile information updated successfully!' in response.data
    
    with app.app_context():
        u = User.query.filter_by(email='avatar@test.com').first()
        assert u.avatar == image_data

def test_avatar_upload_too_large(client, app):
    """UNIT TEST 7: Test that an avatar file larger than 2MB is rejected by the backend."""
    with app.app_context():
        u = User(nickname='BigAvatarGuy', email='bigavatar@test.com')
        u.set_password('mypassword')
        db.session.add(u)
        db.session.commit()
    
    client.post('/login', data={'email': 'bigavatar@test.com', 'password': 'mypassword'}, follow_redirects=True)
    
    # Create a 2.1MB dummy image
    large_image_data = b'0' * (2 * 1024 * 1024 + 100)
    data = {
        'profile-nickname': 'BigAvatarGuy',
        'profile-email': 'bigavatar@test.com',
        'profile-avatar': (io.BytesIO(large_image_data), 'large_avatar.jpg'),
        'profile-submit_profile': 'Update Profile'
    }
    
    response = client.post('/profile', data=data, content_type='multipart/form-data', follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Avatar file is too large!' in response.data
    
    with app.app_context():
        u = User.query.filter_by(email='bigavatar@test.com').first()
        assert u.avatar is None
