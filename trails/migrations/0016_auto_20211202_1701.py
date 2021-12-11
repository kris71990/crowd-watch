# Generated by Django 3.2 on 2021-12-03 01:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trails', '0015_trailhead_region'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='trailhead',
            name='trail',
        ),
        migrations.AddField(
            model_name='trail',
            name='trailheads',
            field=models.ManyToManyField(related_name='trails', to='trails.Trailhead'),
        ),
    ]
