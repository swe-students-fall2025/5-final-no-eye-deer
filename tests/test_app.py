"""
Unit tests for the Flask application.
Note: You may need to add more tests to achieve 80% code coverage.
"""
import pytest
import os
from unittest.mock import patch, MagicMock
from bson.objectid import ObjectId

# Set test environment variables before importing app
os.environ['MONGODB_URI'] = 'mongodb://localhost:27017/petdiary_test'
os.environ['SECRET_KEY'] = 'test-secret-key'

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from web.backend.app import app


@pytest.fixture
def client():
    """Create a test client for the Flask application."""
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    with app.test_client() as client:
        yield client


@pytest.fixture
def mock_db():
    """Mock database collections."""
    with patch('web.backend.app.users') as mock_users, \
         patch('web.backend.app.pets') as mock_pets, \
         patch('web.backend.app.diary_posts') as mock_diary_posts:
        yield {
            'users': mock_users,
            'pets': mock_pets,
            'diary_posts': mock_diary_posts
        }


def test_index_route(client):
    """Test the index route."""
    response = client.get('/')
    assert response.status_code == 200 or response.status_code == 302


def test_signup_get(client):
    """Test signup page GET request."""
    response = client.get('/signup')
    assert response.status_code == 200


def test_signup_post_missing_fields(client, mock_db):
    """Test signup with missing fields."""
    response = client.post('/signup', data={})
    assert response.status_code == 302  # Redirects on error


def test_signup_post_success(client, mock_db):
    """Test successful signup."""
    mock_db['users'].find_one.return_value = None
    mock_db['users'].insert_one.return_value.inserted_id = ObjectId()
    
    response = client.post('/signup', data={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'testpass123'
    })
    assert response.status_code == 302  # Redirects on success


def test_logout(client):
    """Test logout route."""
    response = client.get('/logout')
    assert response.status_code == 302  # Redirects


def test_profile_requires_login(client):
    """Test that profile page requires login."""
    response = client.get('/profile')
    assert response.status_code == 302  # Redirects to login


def test_add_pet_get_requires_login(client):
    """Test that add pet page requires login."""
    response = client.get('/pets/new')
    assert response.status_code == 302  # Redirects to login


def test_save_image_function():
    """Test the save_image function."""
    from web.backend.app import save_image
    from werkzeug.datastructures import FileStorage
    
    # Test with None
    result = save_image(None)
    assert result is None
    
    # Test with empty filename
    mock_file = MagicMock()
    mock_file.filename = ""
    result = save_image(mock_file)
    assert result is None


def test_current_user_no_session():
    """Test current_user when no session."""
    from web.backend.app import current_user
    
    with app.test_request_context():
        result = current_user()
        assert result is None


def test_db_connection():
    """Test database connection."""
    from web.backend.db import get_db
    
    db = get_db()
    assert db is not None
    assert db.name == 'petdiary_test' or db.name == 'petdiary'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

