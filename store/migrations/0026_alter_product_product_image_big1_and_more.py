# Generated by Django 5.0.3 on 2024-04-26 13:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0025_advertisement_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='product_image_big1',
            field=models.ImageField(blank=True, null=True, upload_to='images/products'),
        ),
        migrations.AlterField(
            model_name='product',
            name='product_image_big2',
            field=models.ImageField(blank=True, null=True, upload_to='images/products'),
        ),
    ]
