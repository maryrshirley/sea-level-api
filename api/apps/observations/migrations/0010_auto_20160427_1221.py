# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('observations', '0009_weatherobservation_supplier'),
    ]

    operations = [
        migrations.AlterField(
            model_name='weatherobservation',
            name='supplier',
            field=models.CharField(max_length=10, choices=[('met_office', 'Met Office'), ('seatruck', 'Sea Truck')]),
        ),
    ]
