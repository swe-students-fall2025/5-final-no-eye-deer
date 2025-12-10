# Pet Diary - Final Project

[![Web Backend CI/CD](https://github.com/swe-students-fall2025/5-final-no-eye-deer/actions/workflows/web-backend.yml/badge.svg?branch=main)](https://github.com/swe-students-fall2025/5-final-no-eye-deer/actions/workflows/web-backend.yml)
[![Database CI/CD](https://github.com/swe-students-fall2025/5-final-no-eye-deer/actions/workflows/database.yml/badge.svg?branch=main)](https://github.com/swe-students-fall2025/5-final-no-eye-deer/actions/workflows/database.yml)

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

## Live Deployment

The application is automatically deployed to Digital Ocean on every push to the `main` branch via CI/CD.

🌐 **Live Application**: [http://134.209.36.103:5000](http://134.209.36.103:5000)

> **Note**: 
> - The application runs on port 5000 by default
> - The application is automatically deployed to Digital Ocean on every push to the `main` branch
> - If you encounter any issues accessing the live deployment, please use the local setup instructions below
> - For local development and testing, we recommend using Docker Compose (see Quick Start section)

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
   python3 -m pip install -r requirements.txt
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

The project includes comprehensive unit tests for both subsystems:

### Web Backend Subsystem Tests

```bash
# Install test dependencies
python3 -m pip install pytest pytest-cov pymongo

# Run all web backend tests (app.py and db.py)
python3 -m pytest tests/test_app.py tests/test_db.py --cov=web/backend --cov-report=html --cov-report=term

# View coverage report
# Open htmlcov/index.html in your browser
```

### Database Subsystem Tests

```bash
# Run database subsystem tests
# Note: Tests will automatically start MongoDB if it's not already running
python3 -m pytest tests/test_database.py -v

# Or run all tests together
python3 -m pytest tests/ --cov=web/backend --cov-report=term
```

**Note**: The database subsystem tests will automatically attempt to start MongoDB using Docker if it's not already running. You can also manually start MongoDB using:
```bash
docker-compose up -d mongodb
# or
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

### Test Files

- `tests/test_app.py` - Tests for Flask application (`web/backend/app.py`)
- `tests/test_db.py` - Tests for database connection module (`web/backend/db.py`)
- `tests/test_database.py` - Tests for database subsystem initialization (`database/init-mongo.js`)

The project requires at least 80% code coverage for each subsystem.

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

2. **Build and Push**: Runs on every push and pull request
   - Builds Docker image
   - Pushes to Docker Hub (with PR-specific tags for pull requests)

3. **Deploy**: Runs on every push and pull request
   - **For Pull Requests**: Tests deployment using isolated resources (PR-specific container and network names) to catch deployment errors before merging
   - **For Production (main/master)**: Deploys to Digital Ocean production environment
   - Pulls latest image (or PR-specific tag)
   - Connects to database container via Docker network
   - Restarts the application

### Database Pipeline

1. **Build and Test**: Runs on every push and pull request
   - Builds Docker image
   - Tests MongoDB connection and initialization
   - Runs unit tests for database subsystem (tests/test_database.py)

2. **Build and Push**: Runs on every push and pull request
   - Builds Docker image
   - Pushes to Docker Hub (with PR-specific tags for pull requests)

3. **Deploy**: Runs on every push and pull request
   - **For Pull Requests**: Tests deployment using isolated resources (PR-specific container and network names) to catch deployment errors before merging
   - **For Production (main/master)**: Deploys to Digital Ocean production environment
   - Pulls latest image (or PR-specific tag)
   - Creates Docker network for container communication
   - Starts database container

**Notes**:
- The database container should be deployed before the web backend container to ensure proper connectivity.
- PR deployments use isolated resources (e.g., `pet-diary-database-pr-{number}`) to avoid conflicts with production, allowing safe testing of deployment scripts before merging.

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
