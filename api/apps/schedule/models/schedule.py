from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.db import models

from api.libs.minute_in_time.models import Minute
from api.libs.param_parsers.parse_time import parse_datetime


class ScheduleManager(models.Manager):

    def existing_object(self, code):
        try:
            return self.filter(code=code).latest('id')
        except ObjectDoesNotExist:
            return None

    def active(self, **kwargs):
        return self.exclude(departure__datetime__lt=datetime.now()) \
            .filter(**kwargs).order_by('departure__datetime')


class Schedule(models.Model):
    origin = models.ForeignKey('locations.Location', related_name='+')
    destination = models.ForeignKey('locations.Location', related_name='+')
    vessel = models.ForeignKey('vessel.Vessel', related_name='+')
    departure = models.ForeignKey(Minute, related_name='+')
    arrival = models.ForeignKey(Minute, related_name='+')
    code = models.CharField(max_length=100)

    objects = ScheduleManager()

    @property
    def departure_datetime(self):
        return self.departure.datetime

    @departure_datetime.setter
    def departure_datetime(self, value):
        if type(value) is str:
            value = parse_datetime(value)
        self.departure, created = Minute.objects.get_or_create(datetime=value)
        return self.departure

    @property
    def arrival_datetime(self):
        return self.arrival.datetime

    @arrival_datetime.setter
    def arrival_datetime(self, value):
        if type(value) is str:
            value = parse_datetime(value)
        self.arrival, created = Minute.objects.get_or_create(datetime=value)
        return self.arrival

    @property
    def sea_level(self):
        return 0.0
