# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('observations', '0007_auto_20160420_1054'),
    ]

    operations = [
        migrations.AlterField(
            model_name='weatherobservation',
            name='minute',
            field=models.ForeignKey(related_name='+', to='minute_in_time.Minute'),
        ),
    ]
