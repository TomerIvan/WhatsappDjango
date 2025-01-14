"""
Models for user and message data in the messaging application.

The `User` model extends Django's `AbstractUser` to customize the user model with additional validation for `username` and `password`. The `Message` model represents a message sent from one user to another.

Models:
1. **User**
    - Extends `AbstractUser` to provide custom validation for the `username` and `password` fields.
    - Fields:
        - `username`: A `CharField` (max length 150) that is unique and validated to start with a letter and allow only letters, numbers, and underscores.
        - `first_name`: A `CharField` (max length 30) representing the user's first name.
        - `last_name`: A `CharField` (max length 30) representing the user's last name.
        - `password`: A `CharField` (max length 128) representing the user's password, validated to ensure it contains no spaces.
        - `groups`: A `ManyToManyField` linking the user to groups. Uses a unique `related_name` to avoid conflicts with the default Django `auth.Group`.
        - `user_permissions`: A `ManyToManyField` linking the user to specific permissions. Uses a unique `related_name` to avoid conflicts with the default Django `auth.Permission`.

2. **Message**
    - Represents a message sent from one user to another, with support for replies to messages.
    - Fields:
        - `sender`: A `ForeignKey` to the `User` model representing the sender of the message.
        - `recipient`: A `ForeignKey` to the `User` model representing the recipient of the message.
        - `content`: A `TextField` containing the content of the message (max length 1024).
        - `timestamp`: A `DateTimeField` automatically set when the message is created.
        - `parent_message`: A `ForeignKey` to the `Message` model, allowing replies to be linked to the original message. Set to `null` and `blank` to allow non-reply messages.

    Methods:
        - `__str__(self)`: Returns a string representation of the message in the format:
          "Message from {sender.username} to {recipient.username} at {timestamp}"
"""

from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

class User(AbstractUser):
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z][a-zA-Z0-9_]*$',
                message="Username must start with a letter and can only contain letters, numbers, and underscores."
            )
        ],
    )
    first_name = models.CharField(max_length=30, blank=False)
    last_name = models.CharField(max_length=30, blank=False)
    password = models.CharField(
        max_length=128,
        validators=[
            RegexValidator(
                regex=r'^\S+$',
                message="Password cannot contain spaces."
            )
        ],
        blank=False
    )

    # Define unique related_name to avoid conflicts with auth.User's groups and user_permissions
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='messaging_user_set',  # unique related_name for groups
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='messaging_user_permissions',  # unique related_name for user_permissions
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )
class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField(max_length=1024)
    timestamp = models.DateTimeField(auto_now_add=True)
    parent_message = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='replies')

    def __str__(self):
        return f"Message from {self.sender.username} to {self.recipient.username} at {self.timestamp}"
