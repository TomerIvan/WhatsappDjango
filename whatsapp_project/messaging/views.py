"""
This module defines various views for handling user authentication, messaging, and user interactions
in a Django web application with session timeout functionality.
"""

from django.shortcuts import redirect
from .models import User
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
import logging
from django.contrib import messages
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Message
from django.utils import timezone
from datetime import timedelta
from functools import wraps

# Session timeout in seconds (15 seconds for testing)
SESSION_IDLE_TIMEOUT = 1800


def check_session_timeout(view_func):
    """
    Decorator to check for session timeout before executing the view.

    This decorator checks if the user session has expired based on the
    'last_activity' timestamp stored in the session. If the session has
    timed out, the user will be logged out and a message will be displayed.
    If the request is an API call, a JSON response with a session expired
    status is returned, otherwise the user is redirected to the login page.
    If the request is a non-API, non-AJAX request, the session's 'last_activity'
    timestamp is updated to the current time.

    Args:
        view_func (function): The view function to be decorated.

    Returns:
        function: A wrapped view function that performs the session timeout check
                  before executing the original view function.

    Raises:
        None

    Notes:
        - This decorator only works for authenticated users.
        - It uses the `SESSION_IDLE_TIMEOUT` variable to determine the timeout duration.
        - Non-API, non-AJAX requests are the only ones that update the 'last_activity' timestamp.
    """

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            current_time = timezone.now()
            last_activity = request.session.get('last_activity')

            # Check if this is an API call or a regular request
            is_api_call = request.path.startswith('/api/')
            is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

            if last_activity:
                last_activity = timezone.datetime.fromisoformat(last_activity)
                if current_time - last_activity > timedelta(seconds=SESSION_IDLE_TIMEOUT):
                    logout(request)
                    messages.warning(request, "Your session has expired. Please log in again.")
                    return JsonResponse({'session_expired': True}, status=440) if is_api_call else redirect('login')

            # Only update last_activity for non-API, non-AJAX requests
            if not is_api_call and not is_ajax:
                request.session['last_activity'] = current_time.isoformat()

        return view_func(request, *args, **kwargs)

    return wrapper

@check_session_timeout
@login_required
def messages_view(request):
    """
    Renders the "messages" page displaying a list of root messages (threads) for the logged-in user.
    """
    messages = Message.objects.filter(
        Q(sender=request.user) | Q(recipient=request.user),
        parent_message=None
    ).order_by('-timestamp')

    return render(request, "messages.html", {'messages': messages})

@check_session_timeout
@login_required
def latest_messages_api(request):
    """
    Provides an API endpoint to fetch the latest root messages (threads) and their associated thread messages.
    """
    root_messages = Message.objects.filter(
        Q(sender=request.user) | Q(recipient=request.user),
        parent_message=None
    ).order_by('-timestamp')[:20]

    thread_ids = [msg.id for msg in root_messages]
    all_thread_messages = Message.objects.filter(
        Q(id__in=thread_ids) |
        Q(parent_message_id__in=thread_ids)
    ).order_by('timestamp')

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

    messages_data = []
    for root_message in root_messages:
        thread = threads_map.get(root_message.id, [])
        messages_data.append({
            'thread_id': root_message.id,
            'messages': thread
        })

    return JsonResponse({'threads': messages_data})

def create_user(request):
    """
    Handles user registration by processing form data and creating a new user account.
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

@ensure_csrf_cookie
def login_view(request):
    """
    Handles user login functionality, including authentication and session initialization.
    """
    if request.user.is_authenticated:
        return redirect('/messages/')

    if request.method == 'GET':
        return render(request, 'login.html')

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
            # Initialize last activity timestamp
            request.session['last_activity'] = timezone.now().isoformat()
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

@check_session_timeout
@login_required
def new_message(request):
    """
    Handles the creation of a new message or a reply to an existing message.
    """
    reply_to = request.GET.get('reply_to')
    context = {}

    if reply_to:
        try:
            original_message = Message.objects.get(id=reply_to)

            if original_message.sender != request.user and original_message.recipient != request.user:
                messages.error(request, "Message not found")
                return redirect('messages')

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

@check_session_timeout
@login_required
def search_users(request):
    """
    Handles user search functionality.
    """
    query = request.GET.get('username', '').strip()
    if len(query) < 2:
        return JsonResponse({'users': []})

    users = User.objects.filter(
        Q(username__icontains=query) |
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query)
    ).exclude(id=request.user.id)[:5]

    users_data = [{
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name
    } for user in users]

    return JsonResponse({'users': users_data})

@check_session_timeout
@login_required
def send_message(request):
    """
    Handles sending a new message or replying to an existing message.
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

    parent_message = None
    if reply_to:
        try:
            parent_message = Message.objects.get(id=reply_to)

            if parent_message.sender != request.user and parent_message.recipient != request.user:
                return JsonResponse({
                    'error': 'Message not found',
                    'field': 'recipient'
                }, status=404)

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



@login_required
def update_activity(request):
    """
    Updates the user's last activity timestamp.
    Only responds to POST requests to prevent accidental updates.
    """
    if request.method == 'POST':
        request.session['last_activity'] = timezone.now().isoformat()
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'Method not allowed'}, status=405)