# WhatsApp Django Project

[![GitHub Repository](https://img.shields.io/badge/GitHub-WhatsappDjango-blue.svg)](https://github.com/TomerIvan/WhatsappDjango)

A Django-based WhatsApp integration project that allows you to interact with WhatsApp's API through a Django web application.

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## Installation

### 1. Set Up Virtual Environment

#### On Windows:
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate
```

#### On macOS/Linux:
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Variables

Create a `.env` file in the root directory and add the following variables:
```
DEBUG=True
SECRET_KEY=your_secret_key_here
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 5. Database Setup

```bash
python manage.py migrate
```

### 6. Static Files Setup

Django's `collectstatic` command collects all static files into a single directory that can be served by a web server. Here's how to set it up:

1. Run collectstatic:
```bash
python manage.py collectstatic
```

This will copy all static files from your applications and STATICFILES_DIRS into the STATIC_ROOT directory.

### 7. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 8. Run Development Server

```bash
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000`

## Development Guidelines

- Always activate your virtual environment before working on the project
- Install new dependencies with `pip install package_name`
- Update requirements.txt after installing new packages:
  ```bash
  pip freeze > requirements.txt
  ```

## Common Virtual Environment Commands

### Creating a New Virtual Environment
```bash
# Windows
python -m venv venv

# macOS/Linux
python3 -m venv venv
```

### Activating Virtual Environment
```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### Deactivating Virtual Environment
```bash
deactivate
```

### Deleting Virtual Environment
```bash
# Windows
rmdir venv /s /q

# macOS/Linux
rm -rf venv
```

## Troubleshooting

### Static Files Issues
1. Make sure STATIC_ROOT is correctly set in settings.py
2. Ensure DEBUG is set to False for production
3. Run collectstatic with --clear flag if needed:
   ```bash
   python manage.py collectstatic --clear
   ```

### Virtual Environment Issues
1. If 'venv' activation fails, ensure Python is in your system PATH
2. For permission issues on Linux/macOS:
   ```bash
   chmod +x venv/bin/activate
   ```

## Project Structure
```bash
project-name/
├── manage.py                # Django's command-line utility for administrative tasks
├── requirements.txt         # List of dependencies (including Django)
├── readme.md                # Readme.md File
├── db.sqlite3               # for DB (optional)                    # Virtual environment directory (generated during setup)
├── whatsapp/            # Project's core directory containing settings and URL routing
│   ├── __init__.py          # Django original file
│   ├── settings.py          # Project settings file
│   ├── urls.py              # URL routing for the entire project
│   ├── wsgi.py              # WSGI entry point for deployment
│   ├── asgi.py              # asgi entry point for deployment
├── staticfiles/
│   ├── admin/
│   ├── css/
│   │   ├── login.css)
│   │   ├── messages.css)
│   │   ├── [new_message.css](whatsapp_project/staticfiles/css/new_message.css)
│   │   ├── [registration.css](whatsapp_project/staticfiles/css/registration.css)
│   ├── js/
│   │   ├── login.js
│   │   ├── messages.js
│   │   ├── new_message.js
│   │   ├── registration.js
│   ├── images/
│   │   ├── Whatsapp_Logo.png
├── app_name/                # A Django app within the project
│   ├── migrations/          # Database migrations
│   ├── models.py            # Database models
│   ├── views.py             # View logic
│   ├── urls.py              # URL routing for the app
│   ├── admin.py             # Admin interface customization
├── templates/               # HTML templates
├── static/                  # Static files (CSS, JavaScript, images)
└── manage.py                # Django management utility
```



## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a new branch
3. Make your changes
4. Submit a pull request

## Contact

For questions or support, please open an issue on GitHub or talk to us in class.
