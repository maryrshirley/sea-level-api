# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('predictions', '0011_auto_20160414_1426'),
    ]

    operations = [
        migrations.AlterField(
            model_name='weatherprediction',
            name='minute_from',
            field=models.ForeignKey(related_name='+', to='minute_in_time.Minute'),
        ),
        migrations.AlterField(
            model_name='weatherprediction',
            name='minute_to',
            field=models.ForeignKey(related_name='+', to='minute_in_time.Minute'),
        ),
    ]
