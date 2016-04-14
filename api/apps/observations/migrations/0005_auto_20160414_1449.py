# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('observations', '0004_auto_20160408_1607'),
    ]

    operations = [
        migrations.AlterField(
            model_name='weatherobservation',
            name='precipitation',
            field=models.FloatField(),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='weatherobservation',
            name='pressure',
            field=models.FloatField(),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='weatherobservation',
            name='temperature',
            field=models.FloatField(),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='weatherobservation',
            name='wind_degrees',
            field=models.FloatField(),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='weatherobservation',
            name='wind_gust',
            field=models.FloatField(),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='weatherobservation',
            name='wind_speed',
            field=models.FloatField(),
            preserve_default=True,
        ),
    ]
