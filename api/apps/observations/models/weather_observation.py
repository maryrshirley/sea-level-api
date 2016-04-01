import datetime

from django.db import models
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


class WeatherObservationManager(models.Manager):

    def now_minus_24(self, location):
        now = now_rounded()
        now_minus_24 = now - datetime.timedelta(hours=24)

        return self.filter(location=location,
                           minute__datetime__range=(now_minus_24, now))

    def date_range(self, location, time_range):
        start = time_range.start
        end = time_range.end

        return self.filter(location=location) \
                   .filter(minute__datetime__range=(start, end))

    def location_exists(self, slug):
        return self.filter(location__slug=slug).exists()


@python_2_unicode_compatible
class WeatherObservation(models.Model):
    location = models.ForeignKey(Location)
    minute = models.ForeignKey(Minute, related_name='weather-observations')
    precipitation = models.IntegerField()
    pressure = models.IntegerField()
    wind_gust = models.IntegerField()
    wind_speed = models.IntegerField()
    wind_direction = models.CharField(max_length=3,
                                      choices=CARDINAL_DIRECTIONS)
    wind_degrees = models.IntegerField()
    temperature = models.IntegerField()

    objects = WeatherObservationManager()

    @property
    def datetime(self):
        return self.minute.datetime

    @datetime.setter
    def datetime(self, value):
        if type(value) is str:
            value = parse_datetime(value)
        self.minute, created = Minute.objects.get_or_create(datetime=value)
        return self.minute

    def __str__(self):
        return "{}".format(self.location)
