"""
Custom admin configuration for the `User` and `Message` models in the Django admin interface.

This module customizes the admin interface to ensure that when a `User` is deleted, all associated messages sent or received by the user are also deleted.

Classes:
1. **CustomUserAdmin** (extends `UserAdmin`)
    - Customizes the Django admin interface for the `User` model.
    - Overrides the `delete_model` method to:
        - Delete all messages where the user is the sender.
        - Delete all messages where the user is the recipient.
        - Delete the user after their messages are removed.

    Methods:
        - `delete_model(self, request, obj)`:
            - Deletes all messages sent or received by the `obj` user before deleting the user.
            - This method ensures that message-related data is cleaned up when a user is deleted.

Model Registration:
- The `User` model is registered with the custom `CustomUserAdmin` to use the custom delete logic.
- The `Message` model is registered to appear in the Django admin without customizations.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Message

class CustomUserAdmin(UserAdmin):
    def delete_model(self, request, obj):
        Message.objects.filter(sender=obj).delete()
        Message.objects.filter(recipient=obj).delete()
        obj.delete()

admin.site.register(User, CustomUserAdmin)
admin.site.register(Message)