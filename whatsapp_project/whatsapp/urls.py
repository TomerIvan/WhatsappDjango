"""
URL configuration for whatsapp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))


URL configuration for the project.

This file contains the URL patterns for the Django web application. Each URL is mapped to a view function that handles requests to that URL.

URL Patterns:
- The root URL ('/') and 'login/' path are routed to the `login_view` from the `views.py` file to handle user login.
- 'registration/' is mapped to the `create_user` view, which handles user registration.
- 'messages/' is routed to the `messages_view` for displaying messages.
- 'new_message/' is mapped to the `new_message` view for creating a new message or replying to an existing one.
- 'api/messages/latest/' is connected to the `latest_messages_api` for retrieving the latest messages in a JSON format.
- 'api/users/search/' is connected to the `search_users` API for searching users by username, first name, or last name.
- 'api/messages/send/' is mapped to the `send_message` view to handle sending a message.
- The 'logout/' path uses the `LogoutView` to log the user out of the application.

Static and Media Files:
- In development (when `DEBUG=True`), static and media files are served by Django with `static()` and `MEDIA_URL` respectively.

Note:
- For production environments, make sure `DEBUG` is set to `False` to avoid serving static files via Django, and instead use a dedicated web server like Nginx or Apache for this purpose.
"""


from django.contrib import admin
from django.urls import path
from messaging import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.login_view, name='login'),  # Handle the root URL
    path('login/', views.login_view, name='login'),
    path('registration/', views.create_user, name="registration"),
    path('messages/', views.messages_view, name='messages'),
    path('new_message/', views.new_message, name='new_message'),
    path('api/messages/latest/', views.latest_messages_api, name='latest_messages_api'),
    path('api/users/search/', views.search_users, name='search_users'),
    path('api/messages/send/', views.send_message, name='send_message'),
    path('logout/', LogoutView.as_view(), name='logout'),

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
