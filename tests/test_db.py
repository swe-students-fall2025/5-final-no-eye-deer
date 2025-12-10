"""
Unit tests for the database connection module (web/backend/db.py).
"""
import pytest
import os
from unittest.mock import patch, MagicMock
from pymongo import MongoClient


class TestDatabaseConnection:
    """Test database connection functionality."""
    
    def test_get_db_returns_database(self):
        """Test that get_db() returns a database object."""
        from web.backend.db import get_db
        
        db = get_db()
        assert db is not None
        assert hasattr(db, 'name')
        assert db.name == 'petdiary' or db.name == 'petdiary_test'
    
    def test_get_db_returns_same_instance(self):
        """Test that get_db() returns the same database instance (singleton pattern)."""
        from web.backend.db import get_db
        
        db1 = get_db()
        db2 = get_db()
        assert db1 is db2
    
    def test_mongodb_uri_from_environment(self):
        """Test that MONGO_URI is read from environment variable."""
        from web.backend.db import MONGO_URI
        
        # Should have a default or be set from environment
        assert MONGO_URI is not None
        assert isinstance(MONGO_URI, str)
        assert 'mongodb://' in MONGO_URI or 'mongodb+srv://' in MONGO_URI
    
    def test_mongodb_uri_default_value(self):
        """Test that MONGO_URI has a default value when env var is not set."""
        with patch.dict(os.environ, {}, clear=True):
            # Reload module to get default value
            import importlib
            import web.backend.db as db_module
            importlib.reload(db_module)
            
            assert db_module.MONGO_URI == "mongodb://localhost:27017/petdiary"
    
    def test_mongodb_uri_from_env_var(self):
        """Test that MONGO_URI reads from MONGODB_URI environment variable."""
        test_uri = "mongodb://test-host:27017/testdb"
        with patch.dict(os.environ, {'MONGODB_URI': test_uri}):
            import importlib
            import web.backend.db as db_module
            importlib.reload(db_module)
            
            assert db_module.MONGO_URI == test_uri
    
    def test_client_initialization(self):
        """Test that MongoClient is initialized."""
        from web.backend.db import _client
        
        assert _client is not None
        assert isinstance(_client, MongoClient)
    
    def test_database_name(self):
        """Test that database name is correctly set."""
        from web.backend.db import _db
        
        assert _db is not None
        assert _db.name in ['petdiary', 'petdiary_test']
    
    def test_database_collections_exist(self):
        """Test that required collections can be accessed."""
        from web.backend.db import get_db
        
        db = get_db()
        
        # Test that we can access collections (they may be empty)
        users = db['users']
        pets = db['pets']
        diary_posts = db['diary_posts']
        
        assert users is not None
        assert pets is not None
        assert diary_posts is not None

