# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('observations', '0008_auto_20160420_1122'),
    ]

    operations = [
        migrations.AddField(
            model_name='weatherobservation',
            name='supplier',
            field=models.CharField(default='met_office', max_length=10, choices=[(b'met_office', b'Met Office'), (b'seatruck', b'Sea Truck')]),
            preserve_default=False,
        ),
    ]
