# Generated by Django 4.0 on 2022-01-09 20:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0014_fridgecontent_reordered'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='fridgecontent',
            name='reordered',
        ),
    ]