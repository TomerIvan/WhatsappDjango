"""
App configuration for the `messaging` app.

This class is used to configure the `messaging` application within a Django project.

Class:
    **MessegingConfig** (extends `AppConfig`)
        - Configures the `messaging` app for the Django project.

    Attributes:
        - `default_auto_field`: Specifies the type of primary key to use for models within this app. Set to `'django.db.models.BigAutoField'`, which will use a `BigInt` field for primary keys by default.
        - `name`: The name of the application, which is `'messaging'`.

"""

from django.apps import AppConfig


class MessegingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'messaging'
