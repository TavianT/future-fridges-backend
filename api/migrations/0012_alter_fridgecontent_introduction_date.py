# Generated by Django 4.0 on 2022-01-07 17:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0011_rename_lock_status_door_door_locked'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fridgecontent',
            name='introduction_date',
            field=models.DateField(auto_now_add=True),
        ),
    ]
