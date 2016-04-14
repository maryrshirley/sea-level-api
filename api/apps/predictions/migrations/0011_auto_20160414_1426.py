# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('predictions', '0010_auto_20160408_1436'),
    ]

    operations = [
        migrations.AlterField(
            model_name='weatherprediction',
            name='precipitation',
            field=models.FloatField(),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='weatherprediction',
            name='pressure',
            field=models.FloatField(),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='weatherprediction',
            name='temperature',
            field=models.FloatField(),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='weatherprediction',
            name='wind_degrees',
            field=models.FloatField(),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='weatherprediction',
            name='wind_gust',
            field=models.FloatField(),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='weatherprediction',
            name='wind_speed',
            field=models.FloatField(),
            preserve_default=True,
        ),
    ]
