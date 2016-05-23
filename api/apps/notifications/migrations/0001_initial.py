# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0001_initial'),
        ('locations', '0004_auto_20160520_1013'),
        ('vessel', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('category', models.CharField(max_length=10, choices=[('sea_level', 'Sea Level'), ('wind', 'Wind'), ('wave', 'Wave')])),
                ('status', models.CharField(max_length=10, choices=[('green', 'Green'), ('amber', 'Amber'), ('red', 'Red')])),
                ('location', models.ForeignKey(to='locations.Location', related_name='+')),
                ('schedule', models.ForeignKey(to='schedule.Schedule', related_name='+')),
                ('vessel', models.ForeignKey(to='vessel.Vessel', related_name='+')),
            ],
        ),
    ]
