# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('predictions', '0012_auto_20160420_1122'),
    ]

    operations = [
        migrations.AddField(
            model_name='weatherprediction',
            name='weather_type',
            field=models.CharField(default='not_available', choices=[('not_available', 'Not available'), ('clear_night', 'Clear night'), ('sunny_day', 'Sunny day'), ('partly_cloudy_night', 'Partly cloudy (night)'), ('partly_cloudy_day', 'Partly cloudy (day)'), ('not_used', 'Not used'), ('mist', 'Mist'), ('fog', 'Fog'), ('cloudy', 'Cloudy'), ('overcast', 'Overcast'), ('light_rain_shower_night', 'Light rain shower (night)'), ('light_rain_shower_day', 'Light rain shower (day)'), ('drizzle', 'Drizzle'), ('light_rain', 'Light rain'), ('heavy_rain_shower_night', 'Heavy rain shower (night)'), ('heavy_rain_shower_day', 'Heavy rain shower (day)'), ('heavy_rain', 'Heavy rain'), ('sleet_shower_night', 'Sleet shower (night)'), ('sleet_shower_day', 'Sleet shower (day)'), ('sleet', 'Sleet'), ('hail_shower_night', 'Hail shower (night)'), ('hail_shower_day', 'Hail shower (day)'), ('hail', 'Hail'), ('light_snow_shower_night', 'Light snow shower (night)'), ('light_snow_shower_day', 'Light snow shower (day)'), ('light_snow', 'Light snow'), ('heavy_snow_shower_night', 'Heavy snow shower (night)'), ('heavy_snow_shower_day', 'Heavy snow shower (day)'), ('heavy_snow', 'Heavy snow'), ('thunder_shower_night', 'Thunder shower (night)'), ('thunder_shower_day', 'Thunder shower (day)'), ('thunder', 'Thunder')], max_length=50),
        ),
    ]
