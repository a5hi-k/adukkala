# Generated by Django 5.0.3 on 2024-04-08 15:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0012_alter_variation_variation_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='variation',
            name='variation_stock',
            field=models.IntegerField(default=5),
            preserve_default=False,
        ),
    ]
