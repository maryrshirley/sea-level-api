import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import Q
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.encoding import python_2_unicode_compatible

from api.apps.locations.models import Location
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

SUPPLIERS = (
    ('met_office', 'Met Office'),
    ('dnmi', 'Norwegian Meteorological Institute'),
)


class WeatherPredictionManager(models.Manager):

    def now_plus_24(self, location):
        now = now_rounded()
        now_24 = now + datetime.timedelta(hours=24)

        return self.filter(location=location) \
                   .filter(Q(minute_from__datetime__range=(now, now_24))
                           | Q(minute_to__datetime__range=(now, now_24))) \
                   .order_by('minute_from__datetime')

    def date_range(self, location, time_range):
        start = time_range.start
        end = time_range.end

        return self.filter(location=location) \
                   .exclude(minute_from__datetime__gt=end) \
                   .exclude(minute_to__datetime__lt=start) \
                   .order_by('minute_from__datetime')

    def latest_object(self, location):
        now = now_rounded()
        objects = self.filter(location=location) \
                      .filter(minute_from__datetime__gte=now) \
                      .order_by('minute_from__datetime')
        if not objects.exists():
            return []

        return [objects[0]]

    def existing_object(self, slug, valid_from, valid_to):
        try:
            return self.filter(location__slug=slug) \
                       .filter(Q(minute_from__datetime=valid_from)
                               | Q(minute_to__datetime=valid_to)).get()

        except ObjectDoesNotExist:
            return None


@python_2_unicode_compatible
class WeatherPrediction(models.Model):

    location = models.ForeignKey(Location)
    precipitation = models.FloatField()
    pressure = models.FloatField()
    wind_gust = models.FloatField()
    wind_speed = models.FloatField()
    wind_direction = models.CharField(max_length=3,
                                      choices=CARDINAL_DIRECTIONS)
    wind_degrees = models.FloatField()
    temperature = models.FloatField()
    supplier = models.CharField(max_length=10, choices=SUPPLIERS)
    minute_from = models.ForeignKey(Minute, related_name='weather-minute-from')
    minute_to = models.ForeignKey(Minute, related_name='weather-minute-to')
    objects = WeatherPredictionManager()

    class Meta:
        unique_together = (('location', 'minute_from'),
                           ('location', 'minute_to'))

    def __str__(self):
        return "{}".format(self.location)

    @property
    def valid_from(self):
        return self.minute_from.datetime

    @property
    def valid_to(self):
        return self.minute_to.datetime

    @valid_from.setter
    def valid_from(self, value):
        if type(value) is str:
            value = parse_datetime(value)
        self.minute_from, c = Minute.objects.get_or_create(datetime=value)

    @valid_to.setter
    def valid_to(self, value):
        if type(value) is str:
            value = parse_datetime(value)
        self.minute_to, created = Minute.objects.get_or_create(datetime=value)


@receiver(pre_save, sender=WeatherPrediction)
def run_unique_validator(sender, instance, *args, **kwargs):
    instance.full_clean()
