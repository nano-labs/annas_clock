# Generated by Django 3.0.8 on 2020-07-24 13:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='doodle',
            name='epaper_array',
            field=models.TextField(blank=True, default=''),
        ),
    ]
