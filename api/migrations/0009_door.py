# Generated by Django 4.0 on 2022-01-05 20:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_alter_fridgecontent_expiration_date_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Door',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=10)),
                ('lock_status', models.BooleanField()),
            ],
        ),
    ]
