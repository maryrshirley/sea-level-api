import copy
import re

from api.apps.locations.models import Location
from api.apps.vessel.models import Vessel
from api.apps.schedule.models import Schedule
from api.libs.minute_in_time.models import Minute
from api.libs.param_parsers.parse_time import parse_datetime
from api.libs.test_utils.datetime_utils import delta
from api.libs.test_utils.location import LocationMixin
from api.libs.view_helpers import now_rounded
from api.libs.view_helpers.format_datetime import format_datetime

from .vessel import VesselMixin


class ScheduleMixin(LocationMixin, VesselMixin):

    SCHEDULE_A = {
        'origin__slug': 'liverpool',
        'destination__slug': 'heysham',
        'vessel__slug': 'isle-of-arran',
        'departure__datetime': '2016-03-26T12:00:00Z',
        'departure_sea_level': 1.2,
        'arrival__datetime': '2016-03-26T14:00:00Z',
        'arrival_sea_level': 2.5,
        'code': 'ST_LIV_HEY_20160326_AM'
    }

    SCHEDULE_B = {
        'origin__slug': 'heysham',
        'destination__slug': 'liverpool',
        'vessel__slug': 'isle-of-arran',
        'departure__datetime': '2016-03-26T15:00:00Z',
        'departure_sea_level': 3.9,
        'arrival__datetime': '2016-03-26T17:00:00Z',
        'arrival_sea_level': 5.2,
        'code': 'ST_LIV_HEY_20160326_PM'
    }

    schedule_endpoint = '/1/schedule/'

    schedule_status_endpoint = '/1/_status/schedule/'

    schedule_arrivals_endpoint = '/1/schedule/{0}/arrivals/'

    schedule_departures_endpoint = '/1/schedule/{0}/departures/'

    @property
    def Schedule(self):
        return Schedule

    def create_schedule(self, payload=None, **kwargs):
        if not payload:
            payload = self.payload_schedule(**kwargs)

        payload = self.related_payload(payload)

        return Schedule.objects.create(**payload)

    def create_schedule_now(self, payload=None, **kwargs):
        kwargs['departure__datetime'] = format_datetime(now_rounded())
        kwargs['arrival__datetime'] = format_datetime(delta(hours=2))

        return self.create_schedule(payload, **kwargs)

    # XXX: BAD NAME
    def related_payload(self, payload):
        get_location = lambda x, y: Location.objects.get(slug=x[y + '__slug'])
        get_minute = lambda x, y: \
            Minute.objects.get_or_create(
                datetime=parse_datetime(x[y + '__datetime']))[0]
        get_vessel = lambda x, y: Vessel.objects.get(slug=x[y + '__slug'])
        payload['origin'] = get_location(payload, 'origin')
        payload['destination'] = get_location(payload, 'destination')
        payload['departure'] = get_minute(payload, 'departure')
        payload['arrival'] = get_minute(payload, 'arrival')
        payload['vessel'] = get_vessel(payload, 'vessel')
        del payload['origin__slug']
        del payload['destination__slug']
        del payload['departure__datetime']
        del payload['arrival__datetime']
        del payload['vessel__slug']
        return payload

    # XXX: BAD NAME
    def values_payload(self, payload):
        for field in payload:
            match = re.search('(\w+)__(\w+)', field)
            if not match:
                continue
            if match.group(2) in ('slug', 'imo'):
                payload[match.group(1)] = payload[field]
            elif match.group(2) == 'datetime':
                payload[match.group(1) + "_datetime"] = payload[field]
            del payload[field]

        return payload

    def payload_schedule(self, payload=SCHEDULE_A, **kwargs):
        data = copy.copy(payload)
        data.update(**kwargs)
        return data

    def payload_schedule_read(self, payload):
        data = copy.copy(payload)
        data = {}
        return data

    @property
    def objects(self):
        return Schedule.objects

    def setUpScheduleRequirements(self):
        self.vessel = self.create_vessel()
        self.origin = self.create_location(name='Liverpool', slug='liverpool')
        self.destination = self.create_location(name='Heysham', slug='heysham')

    def tearDownScheduleRequirements(self):
        self.destination.delete()
        self.origin.delete()
        self.vessel.delete()
