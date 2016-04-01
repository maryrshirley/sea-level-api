# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('minute_in_time', '0001_initial'),
        ('locations', '0003_add_location_visible_to_location_model'),
        ('observations', '0002_auto_django_17rc3_1608'),
    ]

    operations = [
        migrations.CreateModel(
            name='WeatherObservation',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('precipitation', models.IntegerField()),
                ('pressure', models.IntegerField()),
                ('wind_gust', models.IntegerField()),
                ('wind_speed', models.IntegerField()),
                ('wind_direction', models.CharField(max_length=3, choices=[('N', 'North'), ('NNE', 'North North East'), ('NE', 'North East'), ('ENE', 'East North East'), ('E', 'East'), ('ESE', 'East South East'), ('SE', 'South East'), ('SSE', 'South South East'), ('S', 'South'), ('SSW', 'South South West'), ('SW', 'Sout West'), ('WSW', 'West South West'), ('W', 'West'), ('WNW', 'West Noth West'), ('NW', 'North West'), ('NNW', 'North North West')])),
                ('wind_degrees', models.IntegerField()),
                ('temperature', models.IntegerField()),
                ('location', models.ForeignKey(to='locations.Location')),
                ('minute', models.ForeignKey(related_name='weather-observations', to='minute_in_time.Minute')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
