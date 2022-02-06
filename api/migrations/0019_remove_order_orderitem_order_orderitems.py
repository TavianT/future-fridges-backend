# Generated by Django 4.0 on 2022-02-04 14:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0018_orderitem_order'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='orderItem',
        ),
        migrations.AddField(
            model_name='order',
            name='orderItems',
            field=models.ManyToManyField(to='api.OrderItem'),
        ),
    ]