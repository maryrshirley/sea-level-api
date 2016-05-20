# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0003_add_location_visible_to_location_model'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='min_depth',
            field=models.FloatField(validators=[django.core.validators.MinValueValidator(0)], default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='location',
            name='under_keal',
            field=models.FloatField(validators=[django.core.validators.MinValueValidator(0)], default=0),
            preserve_default=False,
        ),
    ]
