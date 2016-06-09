import copy

from api.apps.predictions.models import SurgePrediction
from api.libs.view_helpers import now_rounded
from api.libs.view_helpers.format_datetime import format_datetime

from .location import LocationMixin


class SurgePredictionMixin(LocationMixin):

    SURGEPREDICTION_A = {
        'location__slug': LocationMixin.LOCATION_A['slug'],
        'minute__datetime': '2016-03-26T12:00:00Z',
        'surge_level': 3.4,
    }

    SURGEPREDICTION_B = {
        'location__slug': LocationMixin.LOCATION_A['slug'],
        'minute__datetime': '2016-03-26T12:01:00Z',
        'surge_level': 4.5,
    }

    SURGEPREDICTION_C = {
        'location__slug': LocationMixin.LOCATION_A['slug'],
        'minute__datetime': '2016-03-26T12:02:00Z',
        'surge_level': 2.4,
    }

    @property
    def SurgePrediction(self):
        return SurgePrediction

    def create_surgeprediction(self, data=SURGEPREDICTION_A, **kwargs):
        payload = self.related_payload_surgeprediction(data)

        return SurgePrediction.objects.create(**payload)

    def create_surgeprediction_now(self, data=SURGEPREDICTION_A, **kwargs):
        kwargs['minute__datetime'] = format_datetime(now_rounded())
        return self.create_surgeprediction(data, **kwargs)

    def payload_surgeprediction(self, payload):
        return payload

    def related_payload_surgeprediction(self, data=SURGEPREDICTION_A,
                                        **kwargs):
        payload = copy.copy(data)
        payload.update(**kwargs)
        payload = self.payload_minute_datetime(payload)
        payload = self.payload_location_slug(payload)

        return payload

    def setUpSurgePredictionRequirements(self):
        # XXX: Not so sure on this, currently anyone will delete the location
        if not hasattr(self, 'location'):
            self.location = self.create_location()

    def tearDownSurgePredictionRequirements(self):
        if self.location is not None:
            self.location.delete()
            self.location = None
