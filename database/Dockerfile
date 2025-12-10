# Custom MongoDB Dockerfile for Pet Diary Database Subsystem
FROM mongo:7.0

# Set working directory
WORKDIR /docker-entrypoint-initdb.d

# Copy initialization script
COPY init-mongo.js /docker-entrypoint-initdb.d/

# MongoDB will automatically run scripts in /docker-entrypoint-initdb.d/
# when the container is first started with an empty data directory

# Expose MongoDB port
EXPOSE 27017

# Use the default MongoDB entrypoint
# The base image already handles initialization scripts

