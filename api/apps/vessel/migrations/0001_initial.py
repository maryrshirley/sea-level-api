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
                ('imo', models.CharField(unique=True, max_length=7, validators=[django.core.validators.MinLengthValidator(7), django.core.validators.MaxLengthValidator(7), django.core.validators.RegexValidator(regex=b'^\\d+$', message='Must be numbers only', code=b'invalid_imo')])),
                ('draft', models.FloatField(validators=[django.core.validators.MinValueValidator(0)])),
            ],
        ),
    ]
