# Generated by Django 5.0.3 on 2024-04-26 09:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0022_product_product_brand'),
    ]

    operations = [
        migrations.CreateModel(
            name='Advertisement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ad_image', models.ImageField(upload_to='images/advertisements')),
            ],
        ),
    ]
