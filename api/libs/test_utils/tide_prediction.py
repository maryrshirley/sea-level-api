import copy

from api.apps.predictions.models import TidePrediction
from api.libs.view_helpers import now_rounded
from api.libs.view_helpers.format_datetime import format_datetime

from .location import LocationMixin


class TidePredictionMixin(LocationMixin):

    TIDEPREDICTION_A = {
        'location__slug': LocationMixin.LOCATION_A['slug'],
        'minute__datetime': '2016-03-26T12:00:00Z',
        'tide_level': 12.2,
        'is_high_tide': False,
    }

    TIDEPREDICTION_B = {
        'location__slug': LocationMixin.LOCATION_A['slug'],
        'minute__datetime': '2016-03-26T12:01:00Z',
        'tide_level': 15.4,
        'is_high_tide': True,
    }

    TIDEPREDICTION_C = {
        'location__slug': LocationMixin.LOCATION_A['slug'],
        'minute__datetime': '2016-03-26T12:02:00Z',
        'tide_level': 11.1,
        'is_high_tide': False,
    }

    @property
    def TidePrediction(self):
        return TidePrediction

    def create_tideprediction(self, data=TIDEPREDICTION_A, **kwargs):
        payload = self.related_payload_tideprediction(data)
        return TidePrediction.objects.create(**payload)

    def create_tideprediction_now(self, payload=TIDEPREDICTION_A, **kwargs):
        kwargs['minute__datetime'] = format_datetime(now_rounded())
        return self.create_tideprediction(payload, **kwargs)

    def payload_tideprediction(self, payload):
        return payload

    def related_payload_tideprediction(self, data=TIDEPREDICTION_A, **kwargs):
        payload = copy.copy(data)
        payload.update(**kwargs)
        payload = self.payload_minute_datetime(payload)
        payload = self.payload_location_slug(payload)
        return payload

    def setUpTidePredictionRequirements(self):
        if not hasattr(self, 'location'):
            self.location = self.create_location()

    def tearDownTidePredictionRequirements(self):
        if self.location is not None:
            self.location.delete()
            self.location = None
