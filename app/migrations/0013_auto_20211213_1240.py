# Generated by Django 3.1.4 on 2021-12-13 07:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0012_auto_20211213_1239'),
    ]

    operations = [
        migrations.AlterField(
            model_name='classattendence',
            name='date',
            field=models.DateTimeField(),
        ),
    ]
