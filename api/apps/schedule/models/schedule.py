from collections import namedtuple
from datetime import datetime, timedelta

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import Q

from api.apps.locations.models import Location
from api.apps.status.views.common import Status
from api.apps.status.alert_manager import AlertType, is_alert_enabled
from api.libs.minute_in_time.models import Minute
from api.libs.param_parsers.parse_time import parse_datetime
from api.libs.view_helpers import now_rounded

LocationStatus = namedtuple('LocationStatus', 'location_name,status')
TidePrediction = 'predictions.tideprediction'
SurgePrediction = 'predictions.surgeprediction'


class ScheduleManager(models.Manager):

    def existing_object(self, code):
        try:
            return self.filter(code=code).latest('id')
        except ObjectDoesNotExist:
            return None

    def active(self, **kwargs):
        return self.exclude(departure__datetime__lt=datetime.now()) \
            .filter(**kwargs).order_by('departure__datetime')

    def now_plus_24(self, location):
        now = now_rounded()
        now_plus_24 = now + timedelta(hours=24)

        return self.filter(Q(origin=location,
                             departure__datetime__range=(now, now_plus_24)) |
                           Q(destination=location,
                             arrival__datetime__range=(now, now_plus_24)))

    def status(self, location):
        if location is None:
            return Status(False, "Invalid location")

        if not is_alert_enabled(location, AlertType.schedule):
            return Status(True, 'OK (alert disabled)')

        objs = self.now_plus_24(location)
        if objs.exists():
            return Status(True, "OK")
        return Status(False, "Missing data for the next 24 hours")

    def all_location_status(self):
        return [LocationStatus(location.name, self.status(location))
                for location in Location.objects.all()]


class Schedule(models.Model):
    origin = models.ForeignKey('locations.Location', related_name='+')
    destination = models.ForeignKey('locations.Location', related_name='+')
    vessel = models.ForeignKey('vessel.Vessel', related_name='+')
    departure = models.ForeignKey(Minute, related_name='+')
    departure_sea_level = models.FloatField(null=True)
    arrival = models.ForeignKey(Minute, related_name='+')
    arrival_sea_level = models.FloatField(null=True)
    code = models.CharField(max_length=100)

    objects = ScheduleManager()

    @property
    def departure_datetime(self):
        return self.departure.datetime

    @departure_datetime.setter
    def departure_datetime(self, value):
        if isinstance(value, str):
            value = parse_datetime(value)
        self.departure, _ = Minute.objects.get_or_create(datetime=value)
        return self.departure

    @property
    def arrival_datetime(self):
        return self.arrival.datetime

    @arrival_datetime.setter
    def arrival_datetime(self, value):
        if isinstance(value, str):
            value = parse_datetime(value)
        self.arrival, _ = Minute.objects.get_or_create(datetime=value)
        return self.arrival

    def __str__(self):
        return self.code
