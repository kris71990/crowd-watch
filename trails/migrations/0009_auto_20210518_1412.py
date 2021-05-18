# Generated by Django 3.2 on 2021-05-18 21:12

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trails', '0008_auto_20210517_1924'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='access_condition',
            field=models.CharField(blank=True, choices=[('I', 'Impassable'), ('P+', 'Many potholes'), ('P', 'Potholes'), ('P-', 'Occasional potholes'), ('G', 'Good')], help_text='If accessed via service road, What condition was the service road in?', max_length=2, null=True),
        ),
        migrations.AddField(
            model_name='report',
            name='access_distance',
            field=models.IntegerField(blank=True, help_text='If accessed via service road, length of service road from paved road to trailhead', null=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AddField(
            model_name='report',
            name='car_type',
            field=models.CharField(blank=True, choices=[('Suv', 'SUV'), ('S', 'Sedan'), ('T', 'Truck'), ('4wd', 'Four-wheel drive')], help_text='With what type of car did you access the trail?', max_length=3, null=True),
        ),
        migrations.AddField(
            model_name='report',
            name='temperature',
            field=models.CharField(blank=True, choices=[('F', '< 32'), ('C', '33-50'), ('N', '51-70'), ('W', '71-85'), ('H', '86-100'), ('E', '100 <')], help_text='What was the temperature?', max_length=1, null=True),
        ),
        migrations.AddField(
            model_name='report',
            name='weather_type',
            field=models.CharField(blank=True, choices=[('R', 'Rain'), ('Sn', 'Snow'), ('S', 'Sun'), ('PC', 'Partly Cloudy'), ('O', 'Overcast')], help_text='What was the weather like?', max_length=2, null=True),
        ),
        migrations.AddField(
            model_name='trailhead',
            name='access_distance',
            field=models.IntegerField(blank=True, help_text='If accessed via service road, length of service road from paved road to trailhead', null=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
    ]