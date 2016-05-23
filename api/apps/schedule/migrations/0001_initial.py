# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vessel', '0001_initial'),
        ('minute_in_time', '0001_initial'),
        ('locations', '0004_auto_20160520_1013'),
    ]

    operations = [
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('code', models.CharField(max_length=100)),
                ('arrival', models.ForeignKey(to='minute_in_time.Minute', related_name='+')),
                ('departure', models.ForeignKey(to='minute_in_time.Minute', related_name='+')),
                ('destination', models.ForeignKey(to='locations.Location', related_name='+')),
                ('origin', models.ForeignKey(to='locations.Location', related_name='+')),
                ('vessel', models.ForeignKey(to='vessel.Vessel', related_name='+')),
            ],
        ),
    ]
