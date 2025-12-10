// MongoDB initialization script for Pet Diary database
// This script runs automatically when the MongoDB container is first started

// Switch to the petdiary database
db = db.getSiblingDB('petdiary');

// Create collections with validation (optional, but good practice)
db.createCollection('users', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['username', 'email', 'password_hash'],
      properties: {
        username: {
          bsonType: 'string',
          description: 'Username must be a string and is required'
        },
        email: {
          bsonType: 'string',
          pattern: '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$',
          description: 'Email must be a valid email address'
        },
        password_hash: {
          bsonType: 'string',
          description: 'Password hash must be a string and is required'
        }
      }
    }
  }
});

db.createCollection('pets');
db.createCollection('diary_posts');

// Create indexes for better performance
db.users.createIndex({ email: 1 }, { unique: true });
db.users.createIndex({ username: 1 });
db.pets.createIndex({ owner_id: 1 });
db.pets.createIndex({ pet_type: 1 });
db.diary_posts.createIndex({ pet_id: 1 });
db.diary_posts.createIndex({ owner_id: 1 });
db.diary_posts.createIndex({ created_at: -1 });

print('Pet Diary database initialized successfully!');

