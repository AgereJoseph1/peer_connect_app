# Installation Guide for Peer Connect

This guide will walk you through the steps necessary to get Peer Connect up and running on your local machine for development and testing purposes.

## Prerequisites

Before you begin, ensure you have the following installed on your system:
- Python 3.7 or higher
- pip (Python package installer)
- Virtualenv (optional, but recommended for creating isolated Python environments)

## Cloning the Repository

Clone the repository to your local machine using the following command:

```bash
git clone https://github.com/yourusername/peer_connect.git
cd peer_connect
```

## Setting Up a Virtual Environment
Create and activate a virtual environment to manage dependencies:

##### Windows:
```bash
python -m venv venv
venv\Scripts\activate
```
#### macOS and Linux:
```bash
pip install -r requirements.txt
```
---
### Database Initialization
Set up the database with the migrations provided:
```bash
flask db upgrade
```

### Configuration
Create a `.env` file in the root directory and fill in the necessary environment variables:

```bash
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your_secret_key
GOOGLE_API_KEY=your_google_maps_api_key
```
Replace your_secret_key and your_google_maps_api_key with your actual secret key and Google Maps API key.

---
### Running the Application
Start the Flask application using the following command:
```
flask run
```

The application will be accessible at http://localhost:5000.

### Additional Setup
If your application requires additional setup steps such as compiling assets or setting up external services, configure them in the `congig.py` file.