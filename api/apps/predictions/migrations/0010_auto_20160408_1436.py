# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('predictions', '0009_weatherprediction'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='weatherprediction',
            unique_together=set([('location', 'minute_from'), ('location', 'minute_to')]),
        ),
    ]
