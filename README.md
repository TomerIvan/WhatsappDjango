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
Alternatively
```bash
python -m pip install django
```

### 4. Environment Variables

Create a `.env` file in the root directory and add the following variables:
```
DEBUG=True
SECRET_KEY=your_secret_key_here
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 5. Database Setup
**Very Crucial, setting up incorrectly may cause major problems ahead.**

```bash
python manage.py makemigrations messaging
python manage.py migrate
```

### 6. Static Files Setup

Django's `collectstatic` command collects all static files into a single directory that can be served by a web server. Here's how to set it up:

1. Run collectstatic (For production staging)
```bash
python manage.py collectstatic
```

This will copy all static files from your applications and STATICFILES_DIRS into the STATIC_ROOT directory.

### 7. Create Superuser
- Necessary for first usage
- Optional for later usage.
- Follow the prompts.
- Notice: for superusers you need to change manually in the admin panel your first and last name, for showing your name at the different sites.

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
whatsapp_project/
├── manage.py                # Django's command-line utility for administrative tasks
├── requirements.txt         # List of dependencies (including Django)
├── readme.md                # Readme.md File
├── logs/
│   ├── app.log              # log file for the app
├── whatsapp/            # Project's core directory containing settings and URL routing
│   ├── __init__.py          # Django original file
│   ├── settings.py          # Project settings file
│   ├── urls.py              # URL routing for the entire project
│   ├── wsgi.py              # WSGI entry point for deployment
│   ├── asgi.py              # asgi entry point for deployment
├── static/
│   ├── css/
│   │   ├── login.css        # design for the login page
│   │   ├── messages.css     # design for the messages Page
│   │   ├── new_message.css  # design for new message Page
│   │   ├── registration.css # design for registration Page
│   ├── js/
│   │   ├── login.js         # logics for login page
│   │   ├── messages.js      # logics for messages page
│   │   ├── new_message.js   # logics for new message page
│   │   ├── registration.js  # logics for registration page
│   ├── images/
│   │   ├── Whatsapp_Logo.png # logo
├── messaging/                # A Django app within the project
│   ├── templates/
│   │   ├── messaging/
│   │   │   ├── login.html
│   │   │   ├── messages.html
│   │   │   ├── new_message.html
│   │   │   ├── registration.html
│   ├── models.py            # Database models
│   ├── tests.py             # Django tests
│   ├── views.py             # View logic
│   ├── apps.py              # for the Django apps usage
│   ├── __init__.py          # for Django usage
│   ├── admin.py             # Admin interface customization
├── templates/               # HTML templates
├── static/                  # Static files (CSS, JavaScript, images)
└── manage.py                # Django management utility
```

## Feature Documentation

### Feature 1: Registration Screen

**Description:**
The Registration screen allows new users to create an account by providing their necessary details, such as phone number, email, and password.

**How to Use:**
1. Open the app and navigate to the "Registration" screen.
2. Enter your User name, First name, Last name and password.
3. Click the "Register" button to submit the details.
6. After successful registration, you will be redirected to the login screen.

**Known Issues:**
- No Known Issues.

---

### Feature 2: Login Screen

**Description:**
The Login screen allows registered users to access their account by logging in with their phone number/email and password.

**How to Use:**
1. Open the app and navigate to the "Login" screen.
2. Enter your registered User Name and password.
3. Click the "Login" button to authenticate.
4. Once logged in, you will be redirected to the "Messages" screen, where you can view and send messages.

**Known Issues:**
- No Known Issues.

---

### Feature 3: Messages Screen

**Description:**
The Messages screen displays all conversations that the user has with their contacts. It allows users to view, reply to, and delete messages.

**How to Use:**
1. After logging in, you will be directed to the "Messages" screen.
2. Here, you will see a list of all your conversations, from another registered individuals.
3. Tap on any conversation to open the chat and view the messages.
4. To reply, press on the reply button.
5. To create a new message, click the new message button.

**Known Issues:**
- MINOR: For superusers fresh out of console - you need to insert first and last name in the admin panel.

---

### Feature 4: New Messages Screen

**Description:**
The New Messages screen allows users to send new messages to existing contacts, and create new conversations.

**How to Use:**
1. Navigate to the "New Messages" screen from the "Messages" screen by clicking on the "New Message" button.
2. Select a contact (Auto complete field).
3. Type your message in the input box.
4. Once you’ve composed your message, click "Send" to deliver it.
5. You can clear everything by clicking on the clear button.

Also:
1. Click reply on the messages screen.
2. You will see the original message
3. You will see the recipient of the reply automatically.


**Known Issues:**
- No known issues.

---

### General Notes:
- Ensure you have an active internet connection for sending and receiving messages.


## Testing
- **General**
  - Session handling - logged out after 30 minutes of inactive (Optional - change the timeout parameter in view.py)
  - Responsiveness.
  - logs exports (Both on console and on ```app.log``` file)
- **Registration**
  - Logics testing.
  - Duplicate user name testing.
  - Logout function if logged in with another user.
- **Login**
  - Logics testing
  - Sign in with an invalid user
  - Sign in with an invalid password.
- **Messages**
  - Get messages from the database every 5 seconds.
  - Logout Function
  - Time of day testing
  - reply testing
  - new message in the same thread should be refreshed every 5 seconds.
- **New Message**
  - User suggestion shouldn't be on logged in user.
  - Up to 1024 characters in the text box.
  - URL parameter couldn't be changed to a different value (for security reasons - handled on the backend)
  
  

## Contributing Members

We would like to recognize the following individuals for their contributions to this project:

- **Tomer Ivan** - Lead Developer, Full-stack.
- **Itay Kenan** - Front End development.
- **Tamar Boneh** - Backend development.

Thank you for your valuable contributions!

## Contact

For questions or support, please open an issue on GitHub or talk to us in class.


## License

This project is licensed under the MIT License - see the LICENSE file for details.
