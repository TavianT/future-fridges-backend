# Generated by Django 4.0 on 2022-01-05 20:20

from django.db import migrations
from django.db.migrations import operations
from django.db.migrations.operations.models import CreateModel


class Migration(migrations.Migration):
    
    # def addDoorFields(apps, schema_editor):
    #     frontDoor = apps.get_model('api', 'Door')

    dependencies = [
        ('api', '0009_door'),
    ]

    operations = [
        migrations.RunSQL("INSERT INTO api_door (name, lock_status) VALUES ('Front Door', 1), ('Back Door', 1);")
    ]
