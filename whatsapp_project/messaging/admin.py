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