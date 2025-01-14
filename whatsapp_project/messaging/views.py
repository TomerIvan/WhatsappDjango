import time

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
    # Get all root messages (no parent) where user is sender or recipient
    messages = Message.objects.filter(
        Q(sender=request.user) | Q(recipient=request.user),
        parent_message=None  # Only get root messages
    ).order_by('-timestamp')

    return render(request, "messages.html", {'messages': messages})


@login_required
def latest_messages_api(request):
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