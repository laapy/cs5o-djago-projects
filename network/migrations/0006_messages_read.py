# Generated by Django 3.0.6 on 2021-01-08 23:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0005_auto_20201122_1249'),
    ]

    operations = [
        migrations.AddField(
            model_name='messages',
            name='read',
            field=models.BooleanField(default=False),
        ),
    ]
