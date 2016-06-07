from collections import namedtuple
import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.encoding import python_2_unicode_compatible

from api.apps.locations.models import Location
from api.apps.status.alert_manager import AlertType, is_alert_enabled
from api.apps.status.views.common import Status
from api.libs.minute_in_time.models import Minute
from api.libs.param_parsers.parse_time import parse_datetime
from api.libs.view_helpers import now_rounded


CARDINAL_DIRECTIONS = (
    ('N', 'North'),
    ('NNE', 'North North East'),
    ('NE', 'North East'),
    ('ENE', 'East North East'),
    ('E', 'East'),
    ('ESE', 'East South East'),
    ('SE', 'South East'),
    ('SSE', 'South South East'),
    ('S', 'South'),
    ('SSW', 'South South West'),
    ('SW', 'Sout West'),
    ('WSW', 'West South West'),
    ('W', 'West'),
    ('WNW', 'West Noth West'),
    ('NW', 'North West'),
    ('NNW', 'North North West'),
)
LocationStatus = namedtuple('LocationStatus', 'location_name,status')

SUPPLIERS = (
    ('met_office', 'Met Office'),
    ('seatruck', 'Sea Truck'),
)


class WeatherObservationManager(models.Manager):

    def now_minus_24(self, location):
        now = now_rounded()
        now_minus_24 = now - datetime.timedelta(hours=24)

        return self.filter(location=location,
                           minute__datetime__range=(now_minus_24, now)) \
                   .order_by('-minute__datetime')

    def date_range(self, location, time_range):
        start = time_range.start
        end = time_range.end

        return self.filter(location=location) \
                   .filter(minute__datetime__range=(start, end)) \
                   .order_by('-minute__datetime')

    def location_exists(self, slug):
        return self.filter(location__slug=slug).exists()

    def existing_object(self, slug, datetime):
        try:
            return self.filter(location__slug=slug,
                               minute__datetime=datetime).get()

        except ObjectDoesNotExist:
            return None

    def latest_object(self, location):
        objects = self.filter(location=location) \
                      .order_by('-minute__datetime')
        if not objects.exists():
            return []

        return [objects[0]]

    def status(self, location):
        if location is None:
            return Status(False, "Invalid location")

        if not is_alert_enabled(location, AlertType.weather_observations):
            return Status(True, 'OK (alert disabled)')

        objs = self.now_minus_24(location)
        if objs.exists():
            return Status(True, "OK")
        return Status(False, "Missing data for the previous 24 hours")

    def all_location_status(self):
        return [LocationStatus(location.name, self.status(location))
                for location in Location.objects.all()]


@python_2_unicode_compatible
class WeatherObservation(models.Model):
    location = models.ForeignKey(Location)
    minute = models.ForeignKey(Minute, related_name='+')
    precipitation = models.FloatField(null=True, blank=True)
    pressure = models.FloatField(null=True, blank=True)
    wind_gust = models.FloatField(null=True, blank=True)
    wind_speed = models.FloatField(null=True, blank=True)
    wind_direction = models.CharField(blank=True, max_length=3,
                                      choices=CARDINAL_DIRECTIONS)
    wind_degrees = models.FloatField(null=True, blank=True)
    temperature = models.FloatField(null=True, blank=True)
    supplier = models.CharField(max_length=10, choices=SUPPLIERS)

    objects = WeatherObservationManager()

    class Meta:
        unique_together = ('location', 'minute')

    @property
    def datetime(self):
        return self.minute.datetime

    @datetime.setter
    def datetime(self, value):
        if isinstance(value, str):
            value = parse_datetime(value)
        self.minute, _ = Minute.objects.get_or_create(datetime=value)
        return self.minute

    def __str__(self):
        return "{}".format(self.location)


@receiver(pre_save, sender=WeatherObservation)
def run_unique_validator(sender, instance, *args, **kwargs):
    instance.full_clean()
