# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ea_sea_levels', '0004_auto_django_17rc3_1608'),
    ]

    operations = [
        migrations.DeleteModel(name='Measurement'),
        migrations.DeleteModel(name='Station'),
    ]
