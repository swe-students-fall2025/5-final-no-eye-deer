# Pet Diary - Final Project

[![Web Backend CI/CD](https://github.com/swe-students-fall2025/5-final-no-eye-deer/actions/workflows/web-backend.yml/badge.svg)](https://github.com/swe-students-fall2025/5-final-no-eye-deer/actions/workflows/web-backend.yml)
[![Database CI/CD](https://github.com/swe-students-fall2025/5-final-no-eye-deer/actions/workflows/database.yml/badge.svg)](https://github.com/swe-students-fall2025/5-final-no-eye-deer/actions/workflows/database.yml)

A web application for pet owners to manage their pets' information and create diary entries. This project demonstrates software development teamwork, database integration, containerization, and CI/CD pipelines.

## Project Description

Pet Diary is a Flask-based web application that allows users to:
- Create and manage user profiles
- Add and edit pet information (dogs, cats, hamsters, rabbits, birds)
- Create diary posts for their pets with photos
- View pet-specific information and care reminders

The application consists of two main subsystems:
1. **Web Backend** - A Flask application serving the web interface and API (located in `web/` directory)
2. **Database** - A customized MongoDB database instance with pre-configured collections and indexes (located in `database/` directory)

## Team Members

- [Gavin Guo](https://github.com/GavinGuoSZ)
- [Yilin Wu](https://github.com/YilinWu1028)
- [Lily Luo](https://github.com/lilyluo7412)
- [Mojin Yuan](https://github.com/Mojin-Yuan)
- [Serena Wang](https://github.com/serena0615)

## Docker Images

- **Web Backend**: [Docker Hub - pet-diary-backend](https://hub.docker.com/r/lilyluo7412/pet-diary-backend)
- **Database**: [Docker Hub - pet-diary-database](https://hub.docker.com/r/lilyluo7412/pet-diary-database) *(Note: Image will be available after first CI/CD pipeline run)*

## Prerequisites

- Docker and Docker Compose (for running with containers)
- Python 3.11+ (for local development)
- MongoDB (can be run via Docker)

## Quick Start

### Option 1: Using Docker Compose (Recommended)

1. Clone the repository:
   ```bash
   git clone https://github.com/swe-students-fall2025/5-final-no-eye-deer.git
   cd 5-final-no-eye-deer
   ```

2. Create environment file:
   ```bash
   cp env.example .env
   ```

3. Edit `.env` file with your configuration:
   ```env
   MONGODB_URI=mongodb://mongodb:27017/petdiary
   SECRET_KEY=your-secret-key-here
   ```

4. Start the services:
   ```bash
   docker-compose up -d
   ```
   or
   ```bash
   docker compose up -d
   ```

5. Access the application at `http://localhost:8000`

### Option 2: Local Development

1. Clone the repository:
   ```bash
   git clone https://github.com/swe-students-fall2025/5-final-no-eye-deer.git
   cd 5-final-no-eye-deer
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up MongoDB:
   ```bash
   # Using Docker
   docker run -d -p 27017:27017 --name mongodb mongo:latest
   
   # Or install MongoDB locally
   ```

5. Create environment file:
   ```bash
   cp env.example .env
   ```

6. Edit `.env` file:
   ```env
   MONGODB_URI=mongodb://localhost:27017/petdiary
   SECRET_KEY=dev-secret-key
   ```

7. Run the application:
   ```bash
   export FLASK_APP=web/backend/app.py
   export FLASK_ENV=development
   flask run
   ```

8. Access the application at `http://localhost:5000`

## Environment Variables

The application requires the following environment variables:

- `MONGODB_URI`: MongoDB connection string (default: `mongodb://localhost:27017/petdiary`)
- `SECRET_KEY`: Flask secret key for session management (required for production)

### Creating the `.env` File

1. Copy the example file:
   ```bash
   cp env.example .env
   ```

2. Edit `.env` and set the appropriate values:
   ```env
   MONGODB_URI=mongodb://localhost:27017/petdiary
   SECRET_KEY=your-secret-key-here
   ```

   **Note**: For production, generate a secure secret key:
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

## Database Setup

The application uses MongoDB to store:
- User accounts and profiles
- Pet information
- Diary posts

### Initial Data

The database will be automatically initialized when you first run the application. No manual data import is required - users can register and start adding pets immediately.

### Database Collections

- `users`: User accounts and profiles
- `pets`: Pet information
- `diary_posts`: Diary entries for pets

## Running Tests

To run the test suite with coverage:

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest --cov=web/backend --cov-report=html --cov-report=term

# View coverage report
# Open htmlcov/index.html in your browser
```

The project requires at least 80% code coverage.

## Docker Deployment

### Building the Image

```bash
docker build -t pet-diary-backend:latest -f web/Dockerfile .
```

### Running the Container

```bash
docker run -d \
  --name pet-diary-backend \
  -p 5000:5000 \
  -e MONGODB_URI=mongodb://host.docker.internal:27017/petdiary \
  -e SECRET_KEY=your-secret-key \
  pet-diary-backend:latest
```

### Using Docker Compose

See the `docker-compose.yml` file for a complete setup including MongoDB.

## CI/CD Pipeline

The project uses GitHub Actions for continuous integration and deployment. Each subsystem has its own independent CI/CD pipeline that runs on every push and pull request to the `main` or `master` branch.

### Web Backend Pipeline

1. **Build and Test**: Runs on every push and pull request
   - Installs dependencies
   - Runs unit tests with coverage
   - Builds Docker image
   - Verifies coverage threshold (80%)

2. **Build and Push**: Runs on pushes to main/master
   - Builds Docker image
   - Pushes to Docker Hub

3. **Deploy**: Runs on pushes to main/master
   - Deploys to Digital Ocean
   - Pulls latest image
   - Connects to database container via Docker network
   - Restarts the application

### Database Pipeline

1. **Build and Test**: Runs on every push and pull request
   - Builds Docker image
   - Tests MongoDB connection and initialization

2. **Build and Push**: Runs on pushes to main/master
   - Builds Docker image
   - Pushes to Docker Hub

3. **Deploy**: Runs on pushes to main/master
   - Deploys to Digital Ocean
   - Pulls latest image
   - Creates Docker network for container communication
   - Starts database container

**Note**: The database container should be deployed before the web backend container to ensure proper connectivity.

## Project Structure

```
.
├── web/                    # Web Backend Subsystem
│   ├── backend/
│   │   ├── app.py          # Flask application
│   │   └── db.py           # Database connection
│   ├── frontend/
│   │   └── templates/       # HTML templates
│   ├── static/             # Static files (CSS, images, uploads)
│   └── Dockerfile          # Docker image definition
├── database/               # Database Subsystem
│   ├── Dockerfile          # Custom MongoDB image
│   ├── init-mongo.js       # Database initialization script
│   └── README.md           # Database subsystem documentation
├── .github/
│   └── workflows/
│       ├── web-backend.yml # Web backend CI/CD pipeline
│       └── database.yml    # Database CI/CD pipeline
├── requirements.txt        # Python dependencies
├── env.example            # Environment variables example
└── README.md              # This file
```

## License

See [LICENSE](./LICENSE) file for details.
