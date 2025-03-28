# Review Scanner Backend

This is the backend service for the Review Scanner mobile application, which allows users to scan products and view their reviews. The frontend mobile application is available at [Review Scanner Frontend](https://github.com/NoIdeaForMyName/Review_Scanner_frontend).

## Features

- User authentication and authorization
- Product scanning and management
- Review system with ratings and comments
- Shop information tracking
- Image upload and processing
- RESTful API endpoints for both authenticated and guest users

## Tech Stack

- Python 3.x
- Flask (Web Framework)
- PostgreSQL (Database)
- Flask-JWT-Extended (Authentication)
- Flask-SQLAlchemy (ORM)
- Pillow (Image Processing)
- NumPy (Data Processing)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/Review_Scanner_backend.git
cd Review_Scanner_backend
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

4. Configure the database:
- Create a PostgreSQL database named 'ReviewScanner'
- Update the database connection string in `config.py` if needed

5. Create the uploads directory:
```bash
mkdir uploads
```

## Configuration

The application uses a configuration file (`config.py`) for various settings:

- Database connection
- JWT settings
- Upload directory configuration
- Server host and port
- Debug mode

## Running the Application

1. Start the Flask server:
```bash
python run.py
```

The server will start on `http://127.0.0.1:8080` by default.

## API Documentation

The API provides endpoints for both authenticated users and guests. Key endpoints include:

### Guest Endpoints
- GET `/products/get-by-id-list` - Get multiple products by their IDs
- GET `/products/{id}` - Get detailed information about a specific product

### User Endpoints
- Authentication endpoints for login and registration
- Product management endpoints
- Review creation and management
- User profile management

For detailed API documentation, refer to `api_documentation.txt` in the project root.

## Project Structure

```
Review_Scanner_backend/
├── app/                      # Main application package
│   ├── __init__.py          # Flask app initialization and configuration
│   ├── models.py            # Database models (User, Product, Review, Shop)
│   ├── routes_guests.py     # Public API endpoints (no auth required)
│   ├── routes_users.py      # Protected API endpoints (requires authentication)
│   └── common_functions.py  # Shared utility functions and helpers
├── uploads/                  # Directory for storing uploaded product images
├── config.py                # Application configuration (DB, JWT, etc.)
├── config_template.py       # Template for creating new config files
├── requirements.txt         # Python package dependencies
├── run.py                   # Application entry point
└── api_documentation.txt    # Detailed API documentation
```
