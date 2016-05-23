import copy
import re

from api.apps.locations.models import Location
from api.apps.vessel.models import Vessel
from api.apps.schedule.models import Schedule
from api.libs.minute_in_time.models import Minute
from api.libs.param_parsers.parse_time import parse_datetime
from api.libs.test_utils.location import LocationMixin

from .vessel import VesselMixin


class ScheduleMixin(object):

    SCHEDULE_A = {
        'origin__slug': 'liverpool',
        'destination__slug': 'heysham',
        'vessel__imo': '8219554',
        'departure__datetime': '2016-03-26T12:00:00Z',
        'arrival__datetime': '2016-03-26T14:00:00Z',
        'code': 'ST_LIV_HEY_20160326_AM'
    }

    SCHEDULE_B = {
        'origin__slug': 'heysham',
        'destination__slug': 'liverpool',
        'vessel__imo': '8219554',
        'departure__datetime': '2016-03-26T15:00:00Z',
        'arrival__datetime': '2016-03-26T17:00:00Z',
        'code': 'ST_LIV_HEY_20160326_PM'
    }

    schedule_endpoint = '/1/schedule/'

    def create_schedule(self, payload=None, **kwargs):
        if not payload:
            payload = self.payload_schedule(**kwargs)

        payload = self.related_payload(payload)

        return Schedule.objects.create(**payload)

    def related_payload(self, payload):
        get_location = lambda x, y: Location.objects.get(slug=x[y + '__slug'])
        get_minute = lambda x, y: \
            Minute.objects.get_or_create(
                datetime=parse_datetime(x[y + '__datetime']))[0]
        get_vessel = lambda x, y: Vessel.objects.get(imo=x[y + '__imo'])
        payload['origin'] = get_location(payload, 'origin')
        payload['destination'] = get_location(payload, 'destination')
        payload['departure'] = get_minute(payload, 'departure')
        payload['arrival'] = get_minute(payload, 'arrival')
        payload['vessel'] = get_vessel(payload, 'vessel')
        del payload['origin__slug']
        del payload['destination__slug']
        del payload['departure__datetime']
        del payload['arrival__datetime']
        del payload['vessel__imo']
        return payload

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

    @property
    def objects(self):
        return Schedule.objects


class ScheduleRequirementsMixin(LocationMixin, VesselMixin,
                                ScheduleMixin):

    def setUpScheduleRequirements(self):
        self.vessel = self.create_vessel()
        self.origin = self.create_location(name='Liverpool', slug='liverpool')
        self.destination = self.create_location(name='Heysham', slug='heysham')

    def tearDownScheduleRequirements(self):
        self.destination.delete()
        self.origin.delete()
        self.vessel.delete()
