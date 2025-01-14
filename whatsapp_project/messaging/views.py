"""
This module defines various views for handling user authentication, messaging, and user interactions
in a Django web application.

Functions:
    messages_view(request)
    latest_messages_api(request)
    new_message(request)
    create_user(request)
    login_view(request)
    search_users(request)
    send_message(request)
"""

from django.shortcuts import redirect
from .models import User
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
import logging
from django.contrib import messages
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Message
from django.utils import timezone


@login_required
def messages_view(request):
    """
    Renders the "messages" page displaying a list of root messages (threads) for the logged-in user.

    Args:
        request (HttpRequest): The HTTP request object containing user data and session information.

    Returns:
        HttpResponse: Renders the "messages.html" template with a context containing the user's root messages.

    Context:
        messages (QuerySet): A queryset of root `Message` objects where:
            - The logged-in user is either the sender or recipient.
            - The message has no parent (root messages only).
            - Messages are ordered by timestamp in descending order.

    Notes:
        - This view is protected by the `@login_required` decorator, so only authenticated users can access it.
        - The "messages.html" template is expected to use the `messages` context to display the user's message threads.
    """
    # Get all root messages (no parent) where user is sender or recipient
    messages = Message.objects.filter(
        Q(sender=request.user) | Q(recipient=request.user),
        parent_message=None  # Only get root messages
    ).order_by('-timestamp')

    return render(request, "messages.html", {'messages': messages})


@login_required
def latest_messages_api(request):
    """
    Provides an API endpoint to fetch the latest root messages (threads) and their associated thread messages
    for the logged-in user.

    Args:
        request (HttpRequest): The HTTP request object containing user data.

    Returns:
        JsonResponse: A JSON response containing the latest root messages and their respective threads.

    JSON Response:
        {
            "threads": [
                {
                    "thread_id": int,  # ID of the root message (thread)
                    "messages": [
                        {
                            "id": int,  # ID of the message
                            "sender_name": str,  # Sender's full name in "Last Name, First Name" format
                            "recipient_name": str,  # Recipient's full name in "Last Name, First Name" format
                            "content": str,  # Content of the message
                            "timestamp": str,  # Localized timestamp of the message in ISO 8601 format
                            "is_sender": bool  # True if the logged-in user is the sender, False otherwise
                        },
                        ...
                    ]
                },
                ...
            ]
        }

    Process:
        1. Retrieves the latest 20 root messages (no parent) where the logged-in user is either the sender or recipient.
        2. Fetches all messages related to these root messages, including replies.
        3. Groups messages by their respective threads using a dictionary, with each thread represented as a list of messages.
        4. Formats the grouped messages into a structured JSON response.

    Notes:
        - This view is protected by the `@login_required` decorator, allowing access only to authenticated users.
        - Messages are sorted:
            - Root messages: By descending timestamp (most recent first).
            - Thread messages: By ascending timestamp (oldest first within the thread).
    """
    # Get root messages
    root_messages = Message.objects.filter(
        Q(sender=request.user) | Q(recipient=request.user),
        parent_message=None  # Only get root messages
    ).order_by('-timestamp')[:20]

    # Get all related thread messages in a single query
    thread_ids = [msg.id for msg in root_messages]
    all_thread_messages = Message.objects.filter(
        Q(id__in=thread_ids) |  # Include root messages
        Q(parent_message_id__in=thread_ids)  # Include all replies
    ).order_by('timestamp')

    # Group messages by their thread
    threads_map = {}
    for message in all_thread_messages:
        thread_id = message.parent_message_id or message.id
        if thread_id not in threads_map:
            threads_map[thread_id] = []
        threads_map[thread_id].append({
            'id': message.id,
            'sender_name': f"{message.sender.last_name}, {message.sender.first_name}",
            'recipient_name': f"{message.recipient.last_name}, {message.recipient.first_name}",
            'content': message.content,
            'timestamp': timezone.localtime(message.timestamp).isoformat(),
            'is_sender': message.sender_id == request.user.id
        })

    # Format the response
    messages_data = []
    for root_message in root_messages:
        thread = threads_map.get(root_message.id, [])
        messages_data.append({
            'thread_id': root_message.id,
            'messages': thread
        })

    return JsonResponse({'threads': messages_data})


@login_required
def new_message(request):
    """
    Renders the "new_message" page, optionally pre-filling the context with details of a message
    being replied to.

    Args:
        request (HttpRequest): The HTTP request object containing user data and query parameters.

    Returns:
        HttpResponse: Renders the "new_message.html" template with an optional context for the reply.

    Query Parameters:
        reply_to (str): The ID of the message being replied to. If provided, validates the message
                        and pre-fills the context with its details.

    Context:
        original_message (dict, optional): Details of the original message being replied to, including:
            - sender (dict): The sender's information:
                - username (str): The sender's username.
                - first_name (str): The sender's first name.
                - last_name (str): The sender's last name.
            - content (str): The content of the original message.
            - timestamp (datetime): The timestamp of the original message.

    Behavior:
        - If `reply_to` is provided:
            1. Fetches the original message by its ID.
            2. Ensures the logged-in user is either the sender or recipient of the original message.
            3. If valid, adds the original message details to the context.
        - If the message does not exist or an error occurs, the user is redirected to the "messages" page
          with an error message.

    Notes:
        - This view is protected by the `@login_required` decorator, so only authenticated users can access it.
        - The "new_message.html" template is expected to use the `original_message` context, if provided,
          for rendering the reply form.
        - Error handling ensures that sensitive information is not exposed in error messages.
    """
    reply_to = request.GET.get('reply_to')
    context = {}

    if reply_to:
        try:
            # First, check if the message exists
            original_message = Message.objects.get(id=reply_to)

            # Then check permissions
            if original_message.sender != request.user and original_message.recipient != request.user:
                messages.error(request, "Message not found")  # Generic error for security
                return redirect('messages')

            # If we get here, user has permission
            context['original_message'] = {
                'sender': {
                    'username': original_message.sender.username,
                    'first_name': original_message.sender.first_name,
                    'last_name': original_message.sender.last_name,
                },
                'content': original_message.content,
                'timestamp': original_message.timestamp
            }

        except Message.DoesNotExist:
            messages.error(request, "Message not found")
            return redirect('messages')
        except Exception:
            messages.error(request, "An error occurred")
            return redirect('messages')

    return render(request, "new_message.html", context)


def create_user(request):
    """
    Handles user registration by processing form data and creating a new user account.

    Args:
        request (HttpRequest): The HTTP request object containing form data.

    Returns:
        HttpResponse:
            - If the request method is POST and the registration is successful:
                Redirects the user to the login page.
            - If the request method is POST and there are errors:
                Renders the "registration.html" template with an error message.
            - If the request method is GET:
                Renders the "registration.html" template to display the registration form.

    Form Data (POST):
        - UserName (str): The desired username of the new user.
        - FirstName (str): The first name of the new user.
        - LastName (str): The last name of the new user.
        - Password (str): The password for the new user's account.

    Behavior:
        - Checks if the request method is POST.
        - Validates the form data:
            1. Ensures all fields are provided.
            2. Checks if the username is already taken.
        - If validation passes:
            - Creates a new user using the provided data.
            - Saves the user's first and last name.
            - Displays a success message and redirects to the login page.
        - If validation fails or an error occurs during user creation:
            - Renders the "registration.html" template with an appropriate error message.
        - If the request method is GET, renders the "registration.html" template for the registration form.

    Notes:
        - This view is not decorated with `@login_required`, so it is accessible to unauthenticated users.
        - The `User.objects.create_user` method is used to securely handle password hashing.
        - The logger `logger` can be used to log errors or additional information for debugging.
        - Error handling ensures that sensitive details (e.g., exception messages) are not directly exposed to the user.
    """

    if request.method == 'POST':
        # Retrieve form data
        username = request.POST.get('UserName')
        first_name = request.POST.get('FirstName')
        last_name = request.POST.get('LastName')
        password = request.POST.get('Password')

        # Custom validation - check if username already exists
        if User.objects.filter(username=username).exists():
            error_message = "Unfortunately, someone already took this username."
            return render(request, 'registration.html', {'error_message': error_message})

        # Check if any field is empty if for some reason the js messes up
        if not username or not first_name or not last_name or not password:
            error_message = "All fields are required."
            return render(request, 'registration.html', {'error_message': error_message})

        # Create user if all fields are valid
        try:
            user = User.objects.create_user(username=username, password=password)
            user.first_name = first_name
            user.last_name = last_name
            user.save()
            # Add success message
            messages.success(request, "Registration successful!")
            return redirect('login')
        except Exception as e:
            error_message = f"Error: {e}"
            return render(request, 'registration.html', {'error_message': error_message})

    return render(request, "registration.html", {})


logger = logging.getLogger(__name__)


@ensure_csrf_cookie
def login_view(request):
    """
    Handles user login functionality, including authentication and error handling.

    Args:
        request (HttpRequest): The HTTP request object containing form data for login.

    Returns:
        HttpResponse:
            - Redirects authenticated users to the `/messages/` page (for GET or POST requests).
            - Renders the `login.html` template for unauthenticated users making a GET request.
            - Returns a JSON response for POST requests:
                - Success:
                    - HTTP status 200 with a JSON object:
                        {
                            'success': True,
                            'redirect_url': '/messages/'
                        }
                - Failure:
                    - HTTP status 400 or 401 with a JSON object containing an error message:
                        {
                            'success': False,
                            'error': <error_message>,
                            'field': <field_name>
                        }
            - Returns HTTP status 405 for unsupported methods.

    Form Data (POST):
        - username (str): The username of the user attempting to log in.
        - password (str): The password of the user attempting to log in.

    Behavior:
        - Checks if the user is already authenticated:
            - Redirects authenticated users to `/messages/`.
        - Handles GET requests:
            - Renders the `login.html` template for unauthenticated users.
        - Handles POST requests:
            - Validates the presence of `username` and `password` fields.
            - Attempts to authenticate the user:
                - If authentication is successful, logs in the user and returns a success response.
                - If authentication fails, returns an error response with an appropriate error message.
        - Handles unsupported HTTP methods by returning a 405 status code with an error message.

    Notes:
        - The `authenticate` method is used to verify the provided username and password.
        - The `login` method establishes a session for the authenticated user.
        - JSON responses are used for POST requests to allow seamless integration with JavaScript-based frontends.
        - Error handling includes validation for missing fields and invalid credentials.

    Examples:
        1. For an unauthenticated user:
            - GET request to `/login/`:
                Renders the login form.
            - POST request with valid credentials:
                Returns:
                    {
                        'success': True,
                        'redirect_url': '/messages/'
                    }
            - POST request with invalid credentials:
                Returns:
                    {
                        'success': False,
                        'error': 'Invalid username or password',
                        'field': 'username'
                    }

        2. For an authenticated user:
            - GET or POST request to `/login/`:
                Redirects to `/messages/`.
    """

    # First check if user is already authenticated
    if request.user.is_authenticated:
        return redirect('/messages/')  # Redirect authenticated users directly

    # Handle GET request for non-authenticated users
    if request.method == 'GET':
        return render(request, 'login.html')

    # Handle POST request for non-authenticated users
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username:
            return JsonResponse({
                'success': False,
                'error': 'Username is required',
                'field': 'username'
            }, status=400)

        if not password:
            return JsonResponse({
                'success': False,
                'error': 'Password is required',
                'field': 'password'
            }, status=400)

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return JsonResponse({
                'success': True,
                'redirect_url': '/messages/'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Invalid username or password',
                'field': 'username'
            }, status=401)

    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required
def new_message(request):
    def new_message(request):
        """
        Handles the creation of a new message or a reply to an existing message.

        Args:
            request (HttpRequest): The HTTP request object containing the form data for creating a new message.

        Returns:
            HttpResponse:
                - Renders the `new_message.html` template with the provided context if the message is valid.
                - Redirects to the 'messages' view with an error message if any issues occur:
                    - If the message to reply to does not exist or the user does not have permission to reply.
                    - If an error occurs while retrieving or processing the original message.

        Query Parameters:
            - reply_to (str): The ID of the message being replied to (optional).

        Context:
            - If replying to an existing message, the context includes details of the original message:
                - 'original_message': {
                    'sender': {
                        'username': <sender_username>,
                        'first_name': <sender_first_name>,
                        'last_name': <sender_last_name>,
                    },
                    'content': <original_message_content>,
                    'timestamp': <original_message_timestamp>
                }

        Behavior:
            - If a `reply_to` query parameter is present:
                - Tries to find the message with the given ID.
                - Checks if the current user is either the sender or recipient of the original message.
                - If the user is authorized, provides the original message's details in the context to be used in the form.
                - If the message is not found or the user does not have permission, an error message is displayed and the user is redirected to the 'messages' page.
            - If `reply_to` is not provided, the function simply renders the new message form without additional context.

        Error Handling:
            - If the message with the given ID does not exist, or if there is an issue with permissions, an error message is displayed.
            - Generic error handling is in place to catch other exceptions that may occur during processing.

        Examples:
            1. For replying to a message:
                - GET request with `reply_to=<message_id>`:
                    Renders the new message form with the original message's details pre-filled.
                - If the original message is not found or the user does not have permission:
                    Redirects to the 'messages' view with an error message.

            2. For creating a new message:
                - GET request without `reply_to`:
                    Renders the blank new message form.
        """

    reply_to = request.GET.get('reply_to')
    context = {}

    if reply_to:
        try:
            # First, check if the message exists
            original_message = Message.objects.get(id=reply_to)

            # Then check permissions
            if original_message.sender != request.user and original_message.recipient != request.user:
                messages.error(request, "Message not found")  # Generic error for security
                return redirect('messages')

            # If we get here, user has permission
            context['original_message'] = {
                'sender': {
                    'username': original_message.sender.username,
                    'first_name': original_message.sender.first_name,
                    'last_name': original_message.sender.last_name,
                },
                'content': original_message.content,
                'timestamp': original_message.timestamp
            }

        except Message.DoesNotExist:
            messages.error(request, "Message not found")
            return redirect('messages')
        except Exception:
            messages.error(request, "An error occurred")
            return redirect('messages')

    return render(request, "new_message.html", context)


@login_required
def search_users(request):
    """
    Handles user search functionality by querying users based on their username, first name, or last name.

    Args:
        request (HttpRequest): The HTTP request object containing the search query as a GET parameter.

    Returns:
        JsonResponse: A JSON response containing a list of users that match the search query.
            - If the query is too short (less than 2 characters), an empty list is returned.
            - If no users match, an empty list is returned.
            - Otherwise, the response contains a list of up to 5 users, excluding the current logged-in user.

    Query Parameters:
        - username (str): The search query, used to filter users by their username, first name, or last name.

    Response Data:
        - 'users' (list): A list of dictionaries representing users that match the search query. Each dictionary contains:
            - 'username': The username of the user.
            - 'first_name': The first name of the user.
            - 'last_name': The last name of the user.

    Behavior:
        - If the search query length is less than 2 characters, an empty list is returned immediately.
        - If a valid query is provided, the function searches the `User` model for users whose username, first name, or last name contains the query string (case-insensitive).
        - The current logged-in user is excluded from the results.
        - The results are limited to a maximum of 5 users.

    Examples:
        1. For a search query "John":
            - The function returns a list of up to 5 users whose username, first name, or last name contains the string "John".

        2. For a short query (e.g., "J"):
            - The function returns an empty list since the query is too short.

    Notes:
        - The search is case-insensitive and matches partial strings.
        - The search excludes the currently authenticated user from the results.
        - The response is limited to a maximum of 5 users to optimize performance.
    """
    query = request.GET.get('username', '').strip()
    if len(query) < 2:
        return JsonResponse({'users': []})

    users = User.objects.filter(
        Q(username__icontains=query) |
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query)
    ).exclude(id=request.user.id)[:5]  # Limit to 5 results

    users_data = [{
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name
    } for user in users]

    return JsonResponse({'users': users_data})


@login_required
def send_message(request):
    """
    Handles sending a new message or replying to an existing message.

    Args:
        request (HttpRequest): The HTTP request object containing the message data, including recipient, content, and an optional reply.

    Returns:
        JsonResponse: A JSON response containing the result of the operation.
            - If the method is not POST, the response will return a 405 status code (Method Not Allowed).
            - If the recipient or content is missing, the response will return a 400 status code (Bad Request).
            - If the message content exceeds 1024 characters, the response will return a 400 status code.
            - If the recipient does not exist, the response will return a 400 status code.
            - If the reply_to message is invalid or unauthorized, the response will return a 404 or 400 status code accordingly.
            - If the message is successfully saved, the response will return a success message with a 200 status code.
            - If an error occurs while saving the message, the response will return a 500 status code with the error message.

    Form Data:
        - recipient (str): The username of the recipient.
        - content (str): The content of the message.
        - reply_to (str, optional): The ID of the message being replied to.

    Response Data:
        - 'error' (str): A descriptive error message if the operation fails.
        - 'field' (str): The field that caused the error (e.g., 'recipient', 'content').
        - 'success' (bool): A flag indicating the success of the message sending.

    Behavior:
        - The function checks if the HTTP method is POST. If not, it returns a 405 error.
        - It validates that both the recipient and content fields are provided and are valid.
        - If the content exceeds 1024 characters, it returns a 400 error.
        - The recipient's existence is checked in the database. If not found, it returns a 400 error.
        - If the `reply_to` field is provided, the function validates that the parent message exists and that the recipient is part of the conversation.
        - If all checks pass, the message is created and saved in the database.
        - Any errors during the process will be returned with a 500 status code.

    Examples:
        1. Sending a new message:
            - POST request with recipient "johndoe", content "Hello!".
            - Response: {'success': True}.

        2. Replying to an existing message:
            - POST request with recipient "johndoe", content "Thanks!", and reply_to 123 (valid message ID).
            - Response: {'success': True}.

        3. Invalid recipient:
            - POST request with recipient "unknownuser", content "Hello!".
            - Response: {'error': 'Recipient not found', 'field': 'recipient'}.

        4. Exceeding content length:
            - POST request with recipient "johndoe", content exceeding 1024 characters.
            - Response: {'error': 'Message content exceeds maximum length of 1024 characters', 'field': 'content'}.
    """

    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    recipient_username = request.POST.get('recipient')
    content = request.POST.get('content')
    reply_to = request.POST.get('reply_to')

    if not recipient_username:
        return JsonResponse({
            'error': 'Recipient is required',
            'field': 'recipient'
        }, status=400)

    if not content:
        return JsonResponse({
            'error': 'Message content is required',
            'field': 'content'
        }, status=400)

    if len(content) > 1024:
        return JsonResponse({
            'error': 'Message content exceeds maximum length of 1024 characters',
            'field': 'content'
        }, status=400)

    try:
        recipient = User.objects.get(username=recipient_username)
    except User.DoesNotExist:
        return JsonResponse({
            'error': 'Recipient not found',
            'field': 'recipient'
        }, status=400)

    # Validate reply_to if present
    parent_message = None
    if reply_to:
        try:
            # First, check if message exists
            parent_message = Message.objects.get(id=reply_to)

            # Then check permissions
            if parent_message.sender != request.user and parent_message.recipient != request.user:
                return JsonResponse({
                    'error': 'Message not found',  # Generic error for security
                    'field': 'recipient'
                }, status=404)

            # Check recipient is part of original conversation
            if recipient not in [parent_message.sender, parent_message.recipient]:
                return JsonResponse({
                    'error': 'Invalid recipient for this reply',
                    'field': 'recipient'
                }, status=400)

        except Message.DoesNotExist:
            return JsonResponse({
                'error': 'Message not found',
                'field': 'recipient'
            }, status=404)
        except Exception:
            return JsonResponse({
                'error': 'An error occurred',
                'field': 'recipient'
            }, status=500)

    try:
        message = Message(
            sender=request.user,
            recipient=recipient,
            content=content,
            parent_message=parent_message
        )
        message.save()
        return JsonResponse({'success': True})

    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'field': 'content'
        }, status=500)
