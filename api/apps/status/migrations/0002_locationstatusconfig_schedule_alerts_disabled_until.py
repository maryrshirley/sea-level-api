# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('status', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='locationstatusconfig',
            name='schedule_alerts_disabled_until',
            field=models.DateTimeField(help_text='After this date/time, turn on alerts for schedules at this location. Set to blank to turn on immediately.', null=True, blank=True),
        ),
    ]
