## Spotify Clone Backend

This is the backend for a Spotify clone application built with Django and MongoDB. The project aims to replicate core functionalities of Spotify, such as user authentication, music streaming, playlist management, and messaging between users.

## Table of Contents

```
Features
Technologies
Prerequisites
Installation
Running the Application
API Endpoints
Project Structure
Contributing
License
```

## Features

User authentication using Clerk (or custom auth system).
Playlist creation, editing, and deletion.
Music streaming and metadata management.
Messaging system between users.
Search functionality for songs, artists, and playlists.
Integration with MongoDB for scalable data storage.

## Technologies

```
Django: Web framework for backend development.
MongoDB: NoSQL database for storing user data, playlists, and messages.
Djongo: MongoDB connector for Django.
Python: Programming language (version 3.8+).
REST Framework: For building RESTful APIs.
```

### Prerequisites

Before setting up the project, ensure you have the following installed:

Python 3.8 or higher
pip (Python package manager)
MongoDB (local or cloud instance, e.g., MongoDB Atlas)
Git
Ubuntu (or any compatible OS for development)

## Installation

Follow these steps to set up the project locally:

Clone the repository:

```bash
git clone https://github.com/delvintrung/base_django_backend.git
cd base_django_backend
```

Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Set up environment variables:

Create a .env file in the project root and add the following:

```bash
MONGO_URI=
SECRET_KEY='django-insecure-80&wwq@l8i@2_sk-r00#mq%(+d+gyidt)pfk+#r7=x*_)no2(z'
DEBUG=True
ADMIN_EMAIL=
NODE_ENV=development

CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=
CLOUDINARY_CLOUD_NAME=


CLERK_PUBLISHABLE_KEY=
CLERK_SECRET_KEY=
CLERK_API_KEY=
```

## Run database migrations:

```bash
python3 manage.py makemigrations
python3 manage.py migrate
```

## Running the Application

Start the development server:

```bash
python manage.py runserver
```

The server will run at http://127.0.0.1:8000.

## API Endpoints

Below are some example endpoints (update based on your actual implementation):

```python
GET /api/messages/<clerk_id>: Retrieve messages between the authenticated user and another user (by Clerk ID).
POST /api/playlists/: Create a new playlist.
GET /api/songs/: Search for songs by title, artist, or genre.
PUT /api/playlists/<id>: Update an existing playlist.
```

For detailed API documentation, refer to /docs/ (if using Django REST Framework's auto-generated docs).
Project Structure

```bash
base_django_backend/
├── manage.py                # Django management script
├── base_django_backend/          # Main Django app
|   ├── lib/                 # Config lib used
|   ├── middleware/          # Middleware auth,...
|   ├── models/             # Mongoogo model
|   ├── routes/             # Router app
|   ├── utils/              #
|   ├── views/              # Folder views
│   ├── __init__.py
│   ├── settings.py         # Project settings
│   ├── urls.py             # URL routing
│   ├── wsgi.py             # WSGI configuration
│   └── asgi.py             # ASGI configuration
├── requirements.txt         # Project dependencies
├── .env                    # Environment variables
└── README.md               # This file
```

## Contributing

Contributions are welcome! To contribute:

Fork the repository.
Create a new branch (git checkout -b feature/your-feature).
Make your changes and commit (git commit -m "Add your feature").
Push to the branch (git push origin feature/your-feature).
Open a Pull Request.

Please ensure your code follows the project's coding standards and includes tests where applicable.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
[MIT](https://choosealicense.com/licenses/mit/)
