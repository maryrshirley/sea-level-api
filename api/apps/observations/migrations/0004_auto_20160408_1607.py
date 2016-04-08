# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('observations', '0003_weatherobservation'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='weatherobservation',
            unique_together=set([('location', 'minute')]),
        ),
    ]
