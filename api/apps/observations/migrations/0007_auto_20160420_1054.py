# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('observations', '0006_auto_20160420_1020'),
    ]

    operations = [
        migrations.AlterField(
            model_name='weatherobservation',
            name='wind_direction',
            field=models.CharField(blank=True, choices=[('N', 'North'), ('NNE', 'North North East'), ('NE', 'North East'), ('ENE', 'East North East'), ('E', 'East'), ('ESE', 'East South East'), ('SE', 'South East'), ('SSE', 'South South East'), ('S', 'South'), ('SSW', 'South South West'), ('SW', 'Sout West'), ('WSW', 'West South West'), ('W', 'West'), ('WNW', 'West Noth West'), ('NW', 'North West'), ('NNW', 'North North West')], max_length=3),
            preserve_default=True,
        ),
    ]
