# Generated by Django 5.0.3 on 2024-04-26 09:27

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0024_advertisement_created_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='advertisement',
            name='name',
            field=models.CharField(default=django.utils.timezone.now, max_length=100),
            preserve_default=False,
        ),
    ]
