def test_index_pageloads(client):
    """Test that the index page loads successfully."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Event Finder" in response.data

def test_login_page_loads(client):
    """Test that the login page loads."""
    response = client.get('/login')
    assert response.status_code == 200
    assert b"Welcome Back" in response.data
    assert b"Email" in response.data

def test_register_page_loads(client):
    """Test that the registration page loads."""
    response = client.get('/register')
    assert response.status_code == 200
    assert b"Create an Account" in response.data
    assert b"Full Name" in response.data

def test_login_post_mock(client):
    """Test a mock form submission on the login page."""
    response = client.post('/login', data={
        'email': 'test@example.com',
        'password': 'password123'
    }, follow_redirects=True)
    assert response.status_code == 200
    # Flash message for successful mock login
    assert b"Login successful (mock)!" in response.data

def test_register_post_mock(client):
    """Test a mock form submission on the registration page."""
    response = client.post('/register', data={
        'name': 'Test User',
        'email': 'test@example.com',
        'password': 'password123',
        'confirm_password': 'password123'
    }, follow_redirects=True)
    assert response.status_code == 200
    # Flash message for successful test register
    assert b"Registration successful (mock)!" in response.data

def test_logout_mock(client):
    """Test the logout endpoint drops us back cleanly."""
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b"You have been logged out." in response.data
