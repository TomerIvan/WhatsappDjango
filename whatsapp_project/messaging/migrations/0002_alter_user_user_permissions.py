# Generated by Django 5.1.4 on 2025-01-03 15:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('messaging', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='messaging_user_permissions', to='auth.permission', verbose_name='user permissions'),
        ),
    ]
