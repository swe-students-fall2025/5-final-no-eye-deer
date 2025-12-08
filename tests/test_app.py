"""
Unit tests for the Flask application.
Note: You may need to add more tests to achieve 80% code coverage.
"""
import pytest
import os
from unittest.mock import patch, MagicMock
from bson.objectid import ObjectId
from datetime import datetime
import web.backend.app as backend_app
from werkzeug.security import generate_password_hash


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


def test_index_redirect_when_logged_in(client):
    """Index should redirect to profile when user is logged in."""
    with client.session_transaction() as sess:
        sess['user_id'] = str(ObjectId())
    resp = client.get('/')
    assert resp.status_code == 302
    assert '/profile' in resp.headers['Location']


def test_login_missing_fields(client):
    """Login with missing fields should redirect back to index."""
    resp = client.post('/login', data={})
    assert resp.status_code == 302
    assert '/' in resp.headers['Location']


def test_login_invalid_credentials(client, mock_db):
    """Login with invalid credentials."""
    mock_db['users'].find_one.return_value = None
    resp = client.post('/login', data={
        'email': 'nosuch@example.com',
        'password': 'wrong'
    })
    assert resp.status_code == 302
    assert '/' in resp.headers['Location']


def test_login_success_with_email(client, mock_db):
    """Successful login via email."""
    user_id = ObjectId()
    password = 'secret123'
    password_hash = generate_password_hash(password)
    user_doc = {
        '_id': user_id,
        'email': 'user@example.com',
        'username': 'user',
        'password_hash': password_hash,
    }
    mock_db['users'].find_one.side_effect = [user_doc, None]

    resp = client.post('/login', data={
        'email': 'user@example.com',
        'password': password
    })
    assert resp.status_code == 302
    assert '/profile' in resp.headers['Location']


def test_profile_logged_in(client, mock_db):
    """Profile page with logged-in user."""
    user_id = ObjectId()
    user_doc = {
        '_id': user_id,
        'username': 'tester',
        'email': 't@example.com',
        'member_since': None,
        'created_at': datetime.utcnow(),
    }
    mock_db['users'].find_one.return_value = user_doc
    mock_db['pets'].find.return_value = MagicMock()

    with client.session_transaction() as sess:
        sess['user_id'] = str(user_id)

    resp = client.get('/profile')
    assert resp.status_code == 200


def test_edit_profile_get(client, mock_db):
    """GET edit_profile with logged-in user."""
    user_id = ObjectId()
    user_doc = {
        '_id': user_id,
        'username': 'tester',
        'bio': 'hello',
    }
    mock_db['users'].find_one.return_value = user_doc

    with client.session_transaction() as sess:
        sess['user_id'] = str(user_id)

    resp = client.get('/profile/edit')
    assert resp.status_code == 200


def test_edit_profile_post_update(client, mock_db):
    """POST edit_profile updates user."""
    user_id = ObjectId()
    user_doc = {
        '_id': user_id,
        'username': 'oldname',
        'bio': '',
    }
    mock_db['users'].find_one.return_value = user_doc

    with client.session_transaction() as sess:
        sess['user_id'] = str(user_id)

    resp = client.post('/profile/edit', data={
        'bio': 'new bio',
        'username': 'newname'
    })
    assert resp.status_code == 302
    assert '/profile' in resp.headers['Location']
    mock_db['users'].update_one.assert_called_once()


def test_save_image_valid_file():
    """Test save_image with a valid file (happy path)."""
    from web.backend.app import save_image
    mock_file = MagicMock()
    mock_file.filename = "avatar.png"

    with app.test_request_context():
        url = save_image(mock_file)

    mock_file.save.assert_called_once()
    assert url is not None
    assert 'uploads' in url


def _login_with_user(client, mock_db, user_doc=None):
    """Helper: set session + mock current_user user."""
    if user_doc is None:
        user_id = ObjectId()
        user_doc = {
            '_id': user_id,
            'username': 'tester',
            'email': 't@example.com',
            'member_since': datetime.utcnow(),
        }
    else:
        user_id = user_doc['_id']

    mock_db['users'].find_one.return_value = user_doc
    with client.session_transaction() as sess:
        sess['user_id'] = str(user_id)
    return user_doc


def test_add_pet_get_logged_in(client, mock_db):
    """GET /pets/new with logged-in user."""
    _login_with_user(client, mock_db)
    resp = client.get('/pets/new')
    assert resp.status_code == 200


def test_add_pet_post_missing_required_fields(client, mock_db):
    """POST /pets/new missing name should flash + redirect."""
    _login_with_user(client, mock_db)
    resp = client.post('/pets/new', data={
        'name': '',
        'pet_type': 'dog',
    })
    assert resp.status_code == 302
    assert '/pets/new' in resp.headers['Location']


def test_add_pet_post_success_with_invalid_age_weight(client, mock_db):
    """POST /pets/new with invalid age/weight values still inserts pet."""
    user = _login_with_user(client, mock_db)
    mock_db['pets'].insert_one.return_value.inserted_id = ObjectId()

    resp = client.post('/pets/new', data={
        'name': 'Buddy',
        'pet_type': 'dog',
        'age': 'abc', 
        'weight': 'xyz', 
        'breed': 'Golden',
        'tags': ['cute', 'big']
    })
    assert resp.status_code == 302
    assert '/pets/' in resp.headers['Location']
    mock_db['pets'].insert_one.assert_called_once()
    insert_doc = mock_db['pets'].insert_one.call_args[0][0]
    assert insert_doc['owner_id'] == user['_id']


def test_edit_pet_get_success(client, mock_db):
    """GET /pets/<pet_id>/edit with existing pet."""
    user = _login_with_user(client, mock_db)
    pet_id = ObjectId()
    pet_doc = {
        '_id': pet_id,
        'owner_id': user['_id'],
        'name': 'Buddy',
        'pet_type': 'dog',
    }
    mock_db['pets'].find_one.return_value = pet_doc

    resp = client.get(f'/pets/{pet_id}/edit')
    assert resp.status_code == 200


def test_edit_pet_not_found(client, mock_db):
    """Edit pet when pet does not exist redirects."""
    _login_with_user(client, mock_db)
    mock_db['pets'].find_one.return_value = None

    pet_id = ObjectId()
    resp = client.post(f'/pets/{pet_id}/edit', data={'name': 'New'})
    assert resp.status_code == 302
    assert '/profile' in resp.headers['Location']


def test_edit_pet_post_success(client, mock_db):
    """POST /pets/<pet_id>/edit updates pet."""
    user = _login_with_user(client, mock_db)
    pet_id = ObjectId()
    pet_doc = {
        '_id': pet_id,
        'owner_id': user['_id'],
        'name': 'Buddy',
        'pet_type': 'dog',
        'age': 3,
        'weight': 10.0,
        'breed': 'Golden',
        'tags': ['cute'],
    }
    mock_db['pets'].find_one.return_value = pet_doc

    resp = client.post(f'/pets/{pet_id}/edit', data={
        'name': 'NewName',
        'pet_type': 'dog',
        'age': '4',
        'weight': '11.5',
        'breed': 'Golden',
        'tags': ['cute', 'smart']
    })
    assert resp.status_code == 302
    assert f'/pets/{pet_id}' in resp.headers['Location']
    mock_db['pets'].update_one.assert_called_once()


def test_pet_detail_success_dog(client, mock_db):
    """Pet detail page for a dog."""
    user = _login_with_user(client, mock_db)
    pet_id = ObjectId()
    pet_doc = {
        '_id': pet_id,
        'owner_id': user['_id'],
        'name': 'Buddy',
        'pet_type': 'dog',
    }
    mock_db['pets'].find_one.return_value = pet_doc

    resp = client.get(f'/pets/{pet_id}')
    assert resp.status_code == 200


def test_pet_detail_not_found(client, mock_db):
    """Pet detail when not found redirects."""
    _login_with_user(client, mock_db)
    mock_db['pets'].find_one.return_value = None
    pet_id = ObjectId()
    resp = client.get(f'/pets/{pet_id}')
    assert resp.status_code == 302
    assert '/profile' in resp.headers['Location']


def test_pet_diary_list_success(client, mock_db):
    """List diary posts for a pet."""
    user = _login_with_user(client, mock_db)
    pet_id = ObjectId()
    pet_doc = {
        '_id': pet_id,
        'owner_id': user['_id'],
        'name': 'Buddy',
    }
    mock_db['pets'].find_one.return_value = pet_doc

    resp = client.get(f'/pets/{pet_id}/diary')
    assert resp.status_code == 200


def test_pet_diary_list_pet_not_found(client, mock_db):
    """Diary list when pet not found redirects."""
    _login_with_user(client, mock_db)
    mock_db['pets'].find_one.return_value = None
    pet_id = ObjectId()
    resp = client.get(f'/pets/{pet_id}/diary')
    assert resp.status_code == 302
    assert '/profile' in resp.headers['Location']


def test_add_diary_post_get(client, mock_db):
    """GET /pets/<pet_id>/diary/new."""
    user = _login_with_user(client, mock_db)
    pet_id = ObjectId()
    pet_doc = {
        '_id': pet_id,
        'owner_id': user['_id'],
        'name': 'Buddy',
    }
    mock_db['pets'].find_one.return_value = pet_doc

    resp = client.get(f'/pets/{pet_id}/diary/new')
    assert resp.status_code == 200


def test_add_diary_post_missing_title(client, mock_db):
    """POST diary without title should redirect back to form."""
    user = _login_with_user(client, mock_db)
    pet_id = ObjectId()
    pet_doc = {
        '_id': pet_id,
        'owner_id': user['_id'],
        'name': 'Buddy',
    }
    mock_db['pets'].find_one.return_value = pet_doc

    resp = client.post(f'/pets/{pet_id}/diary/new', data={
        'title': '',
        'description': 'desc'
    })
    assert resp.status_code == 302
    assert f'/pets/{pet_id}/diary/new' in resp.headers['Location']


def test_add_diary_post_success(client, mock_db):
    """POST /pets/<pet_id>/diary/new creates a post."""
    user = _login_with_user(client, mock_db)
    pet_id = ObjectId()
    pet_doc = {
        '_id': pet_id,
        'owner_id': user['_id'],
        'name': 'Buddy',
    }
    mock_db['pets'].find_one.return_value = pet_doc
    mock_db['diary_posts'].insert_one.return_value.inserted_id = ObjectId()

    resp = client.post(f'/pets/{pet_id}/diary/new', data={
        'title': 'First Post',
        'description': 'desc',
        'photo_url': 'http://example.com/photo.jpg'
    })
    assert resp.status_code == 302
    assert '/diary/' in resp.headers['Location']
    mock_db['diary_posts'].insert_one.assert_called_once()


def test_delete_pet_success(client, mock_db):
    """Delete a pet and its diary posts."""
    user = _login_with_user(client, mock_db)
    pet_id = ObjectId()
    pet_doc = {
        '_id': pet_id,
        'owner_id': user['_id'],
        'name': 'Buddy',
    }
    mock_db['pets'].find_one.return_value = pet_doc

    resp = client.post(f'/pets/{pet_id}/delete')
    assert resp.status_code == 302
    assert '/profile' in resp.headers['Location']
    mock_db['pets'].delete_one.assert_called_once()
    mock_db['diary_posts'].delete_many.assert_called_once()


def test_delete_pet_not_found(client, mock_db):
    """Delete pet when not found."""
    _login_with_user(client, mock_db)
    mock_db['pets'].find_one.return_value = None
    pet_id = ObjectId()
    resp = client.post(f'/pets/{pet_id}/delete')
    assert resp.status_code == 302
    assert '/profile' in resp.headers['Location']


def test_diary_detail_success(client, mock_db):
    """Diary detail page."""
    user = _login_with_user(client, mock_db)
    pet_id = ObjectId()
    post_id = ObjectId()

    post_doc = {
        '_id': post_id,
        'pet_id': str(pet_id),
        'owner_id': str(user['_id']),
        'title': 'Title',
        'description': 'desc',
    }
    pet_doc = {
        '_id': pet_id,
        'owner_id': user['_id'],
        'name': 'Buddy',
    }

    mock_db['diary_posts'].find_one.return_value = post_doc
    mock_db['pets'].find_one.return_value = pet_doc
    mock_db['users'].find_one.return_value = user

    resp = client.get(f'/diary/{post_id}')
    assert resp.status_code == 200


def test_diary_detail_not_found(client, mock_db):
    """Diary detail when post not found redirects."""
    _login_with_user(client, mock_db)
    mock_db['diary_posts'].find_one.return_value = None
    post_id = ObjectId()
    resp = client.get(f'/diary/{post_id}')
    assert resp.status_code == 302
    assert '/profile' in resp.headers['Location']


def test_delete_diary_post_not_found(client, mock_db):
    """Delete diary when post not found."""
    _login_with_user(client, mock_db)
    mock_db['diary_posts'].find_one.return_value = None
    post_id = ObjectId()
    resp = client.post(f'/diary/{post_id}/delete')
    assert resp.status_code == 302
    assert '/profile' in resp.headers['Location']


def test_delete_diary_post_not_owner(client, mock_db):
    """Delete diary when user is not owner."""
    user = _login_with_user(client, mock_db)
    post_id = ObjectId()
    post_doc = {
        '_id': post_id,
        'pet_id': str(ObjectId()),
        'owner_id': str(ObjectId()), 
        'title': 'Title',
    }
    mock_db['diary_posts'].find_one.return_value = post_doc

    resp = client.post(f'/diary/{post_id}/delete')
    assert resp.status_code == 302
    assert '/profile' in resp.headers['Location']
    mock_db['diary_posts'].delete_one.assert_not_called()


def test_delete_diary_post_success(client, mock_db):
    """Delete diary when user is the owner."""
    user = _login_with_user(client, mock_db)
    pet_id = ObjectId()
    post_id = ObjectId()
    post_doc = {
        '_id': post_id,
        'pet_id': str(pet_id),
        'owner_id': str(user['_id']),
        'title': 'Title',
    }
    mock_db['diary_posts'].find_one.return_value = post_doc

    resp = client.post(f'/diary/{post_id}/delete')
    assert resp.status_code == 302
    assert '/pets/' in resp.headers['Location'] or '/profile' in resp.headers['Location']
    mock_db['diary_posts'].delete_one.assert_called_once()


def test_export_pet_diary_success(client, mock_db):
    """Export diary CSV for a pet."""
    user = _login_with_user(client, mock_db)
    pet_id = ObjectId()
    pet_doc = {
        '_id': pet_id,
        'owner_id': user['_id'],
        'name': 'Buddy',
        'pet_type': 'dog',
    }
    mock_db['pets'].find_one.return_value = pet_doc

    post_doc = {
        'title': 'T',
        'description': 'D',
        'photo_url': 'http://example.com/p.png',
        'created_at': datetime(2024, 1, 1, 12, 0, 0),
    }
    cursor_mock = MagicMock()
    cursor_mock.sort.return_value = [post_doc]
    mock_db['diary_posts'].find.return_value = cursor_mock

    resp = client.get(f'/pets/{pet_id}/diary/export')
    assert resp.status_code == 200
    assert resp.mimetype == 'text/csv'
    disp = resp.headers.get('Content-Disposition', '')
    assert 'attachment;' in disp
    assert 'Buddy_diary_export.csv' in disp
    assert b'Pet Name,Pet Type,Title,Description,Photo URL,Created At' in resp.data


def test_export_pet_diary_pet_not_found(client, mock_db):
    """Export diary when pet not found redirects."""
    _login_with_user(client, mock_db)
    mock_db['pets'].find_one.return_value = None
    pet_id = ObjectId()
    resp = client.get(f'/pets/{pet_id}/diary/export')
    assert resp.status_code == 302
    assert '/profile' in resp.headers['Location']


def test_save_reminders_not_logged_in(client, monkeypatch):
    """If not loggin, should return 401 and error"""
    monkeypatch.setattr(backend_app, "current_user", lambda: None)

    pet_id = str(ObjectId())
    resp = client.post(f"/pets/{pet_id}/reminders", json={"reminders": ["a", "b"]})

    assert resp.status_code == 401
    data = resp.get_json()
    assert data["error"] == "Not logged in"


def test_save_reminders_invalid_pet_id(client, mock_db, monkeypatch):
    """If pet_id is not legal ObjectId, it should return 400"""
    user = {"_id": ObjectId(), "username": "tester"}
    monkeypatch.setattr(backend_app, "current_user", lambda: user)

    bad_id = "not-a-valid-objectid"
    resp = client.post(f"/pets/{bad_id}/reminders", json={"reminders": ["a"]})

    assert resp.status_code == 400
    data = resp.get_json()
    assert "Invalid pet ID" in data["error"]


def test_save_reminders_pet_not_found(client, mock_db, monkeypatch):
    """If id is legal but cannot search from database, it should return 404"""
    user = {"_id": ObjectId(), "username": "tester"}
    monkeypatch.setattr(backend_app, "current_user", lambda: user)

    pet_oid = ObjectId()
    mock_db["pets"].find_one.return_value = None

    resp = client.post(f"/pets/{pet_oid}/reminders", json={"reminders": ["a"]})

    assert resp.status_code == 404
    data = resp.get_json()
    assert "Pet not found" in data["error"]


def test_save_reminders_success(client, mock_db, monkeypatch):
    """Good: Successfully save reminders, return success=True"""
    user = {"_id": ObjectId(), "username": "tester"}
    monkeypatch.setattr(backend_app, "current_user", lambda: user)

    pet_oid = ObjectId()
    mock_db["pets"].find_one.return_value = {
        "_id": pet_oid,
        "owner_id": user["_id"],
        "name": "Buddy",
        "pet_type": "dog",
    }

    mock_db["pets"].update_one = MagicMock()

    reminders = ["Walk", "Feed"]
    resp = client.post(
        f"/pets/{pet_oid}/reminders",
        json={"reminders": reminders},
    )

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True

    mock_db["pets"].update_one.assert_called_once_with(
        {"_id": pet_oid},
        {"$set": {"reminders": reminders}},
    )


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

