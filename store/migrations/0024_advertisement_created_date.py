# Generated by Django 5.0.3 on 2024-04-26 09:23

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0023_advertisement'),
    ]

    operations = [
        migrations.AddField(
            model_name='advertisement',
            name='created_date',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
