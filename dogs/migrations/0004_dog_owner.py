# Generated by Django 5.1.3 on 2024-12-03 20:48

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dogs', '0003_alter_breed_options_alter_dog_options_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='dog',
            name='owner',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='owned_dogs', to=settings.AUTH_USER_MODEL, verbose_name='Владелец'),
        ),
    ]
