# Generated by Django 3.2 on 2021-05-24 23:29

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trails', '0010_alter_report_access_distance'),
    ]

    operations = [
        migrations.AlterField(
            model_name='report',
            name='access_condition',
            field=models.CharField(blank=True, choices=[('I', 'Impassable'), ('P+', 'Many potholes'), ('P', 'Potholes'), ('P-', 'Occasional potholes'), ('G', 'Good')], help_text='If accessed via service road, the condition of the service road?', max_length=2, null=True),
        ),
        migrations.AlterField(
            model_name='trailhead',
            name='pkg_capacity',
            field=models.IntegerField(blank=True, help_text='Approximate number of cars capable of parking at trailhead lot', null=True, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Parking capacity'),
        ),
        migrations.AlterField(
            model_name='trailhead',
            name='pkg_type',
            field=models.CharField(blank=True, choices=[('UL', 'Unpaved Lot'), ('PL', 'Paved Lot'), ('S', 'Street/Road'), ('P', 'Designated Pullout/Shoulder')], help_text='Type of Parking at Trailhead', max_length=2, null=True, verbose_name='Parking type'),
        ),
    ]
