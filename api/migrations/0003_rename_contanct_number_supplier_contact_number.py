# Generated by Django 4.0 on 2022-01-03 21:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_supplier_item_fridgecontent'),
    ]

    operations = [
        migrations.RenameField(
            model_name='supplier',
            old_name='contanct_number',
            new_name='contact_number',
        ),
    ]
