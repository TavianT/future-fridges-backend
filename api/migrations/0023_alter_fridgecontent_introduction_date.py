# Generated by Django 4.0 on 2022-02-09 11:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0022_alter_order_delivery_driver'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fridgecontent',
            name='introduction_date',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
