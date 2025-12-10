# Database Subsystem

This is the MongoDB database subsystem for the Pet Diary application.

## Overview

This subsystem provides a customized MongoDB database instance with:
- Pre-configured database and collections
- Indexes for optimal query performance
- Data validation schemas

## Docker Image

The Docker image is built from the official MongoDB image (mongo:7.0) with custom initialization scripts.

## Building the Image

```bash
docker build -t pet-diary-database:latest -f database/Dockerfile database/
```

## Running the Container

```bash
docker run -d \
  --name pet-diary-database \
  -p 27017:27017 \
  -v mongodb_data:/data/db \
  pet-diary-database:latest
```

## Environment Variables

- `MONGO_INITDB_DATABASE`: Database name (default: petdiary)

## Collections

- `users`: User accounts and profiles
- `pets`: Pet information
- `diary_posts`: Diary entries for pets

