# Generated by Django 4.0.4 on 2022-06-22 19:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trails', '0002_remove_trail_dogs_allowed_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='trail',
            name='dogs_allowed',
            field=models.JSONField(blank=True, default=list, null=True, verbose_name='Dogs'),
        ),
        migrations.AddField(
            model_name='trail',
            name='horses_allowed',
            field=models.JSONField(blank=True, default=list, null=True, verbose_name='Horses'),
        ),
    ]
