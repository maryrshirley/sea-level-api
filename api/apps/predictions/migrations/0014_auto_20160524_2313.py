# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('predictions', '0013_weatherprediction_weather_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='surgeprediction',
            name='location',
            field=models.ForeignKey(related_name='surge_predictions', to='locations.Location'),
        ),
        migrations.AlterField(
            model_name='tideprediction',
            name='location',
            field=models.ForeignKey(related_name='tide_predictions', to='locations.Location'),
        ),
    ]
