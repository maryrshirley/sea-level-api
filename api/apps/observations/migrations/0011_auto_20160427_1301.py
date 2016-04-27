# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def convert_mph(mph):
    if not mph:
        return None
    return mph * 0.44704


def convert_units(apps, schema_editor):
    WeatherObservation = apps.get_model('observations', 'WeatherObservation')
    for record in WeatherObservation.objects.filter(supplier='met_office'):
        record.wind_gust = convert_mph(record.wind_gust)
        record.wind_speed = convert_mph(record.wind_speed)
        record.save()


class Migration(migrations.Migration):

    dependencies = [
        ('observations', '0010_auto_20160427_1221'),
    ]

    operations = [
        migrations.RunPython(convert_units),
    ]
