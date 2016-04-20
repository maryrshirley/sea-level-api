# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('observations', '0005_auto_20160414_1449'),
    ]

    operations = [
        migrations.AlterField(
            model_name='weatherobservation',
            name='precipitation',
            field=models.FloatField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='weatherobservation',
            name='pressure',
            field=models.FloatField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='weatherobservation',
            name='temperature',
            field=models.FloatField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='weatherobservation',
            name='wind_degrees',
            field=models.FloatField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='weatherobservation',
            name='wind_direction',
            field=models.CharField(blank=True, max_length=3, choices=[(b'N', b'North'), (b'NNE', b'North North East'), (b'NE', b'North East'), (b'ENE', b'East North East'), (b'E', b'East'), (b'ESE', b'East South East'), (b'SE', b'South East'), (b'SSE', b'South South East'), (b'S', b'South'), (b'SSW', b'South South West'), (b'SW', b'Sout West'), (b'WSW', b'West South West'), (b'W', b'West'), (b'WNW', b'West Noth West'), (b'NW', b'North West'), (b'NNW', b'North North West')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='weatherobservation',
            name='wind_gust',
            field=models.FloatField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='weatherobservation',
            name='wind_speed',
            field=models.FloatField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
