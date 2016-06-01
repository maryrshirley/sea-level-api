# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('status', '0002_locationstatusconfig_schedule_alerts_disabled_until'),
    ]

    operations = [
        migrations.AddField(
            model_name='locationstatusconfig',
            name='weather_observations_alerts_disabled_until',
            field=models.DateTimeField(help_text='After this date/time, turn on alerts for weather                    observations at this location. Set to blank to turn on                    immediately.', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='locationstatusconfig',
            name='weather_predictions_alerts_disabled_until',
            field=models.DateTimeField(help_text='After this date/time, turn on alerts for weather predictions                    at this location. Set to blank to turn on immediately.', null=True, blank=True),
        ),
    ]
