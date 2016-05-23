# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Vessel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('slug', models.SlugField()),
                ('imo', models.CharField(max_length=7, unique=True, validators=[django.core.validators.MinLengthValidator(7), django.core.validators.MaxLengthValidator(7), django.core.validators.RegexValidator(message='Must be numbers only', code='invalid_imo', regex='^\\d+$')])),
                ('draft', models.FloatField(validators=[django.core.validators.MinValueValidator(0)])),
            ],
        ),
    ]
