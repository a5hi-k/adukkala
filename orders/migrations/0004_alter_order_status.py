# Generated by Django 5.0.3 on 2024-04-24 17:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_order_payment_method'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('New', 'New'), ('Accepted', 'Accepted'), ('Completed', 'Completed'), ('Cancelled', 'Cancelled'), ('Delivered', 'Delivered')], default='New', max_length=10),
        ),
    ]
