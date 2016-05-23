import copy

from api.apps.locations.models import Location


class LocationMixin(object):

    LOCATION_A = {
        'slug': 'liverpool',
        'name': 'Liverpool',
        'min_depth': 2.1,
        'under_keal': 4.5,
    }

    LOCATION_B = {
        'slug': 'southampton',
        'name': 'Southampton',
        'min_depth': 1.2,
        'under_keal': 3.4,
    }

    @classmethod
    def create_location(cls, payload=LOCATION_A, **kwargs):
        payload = cls.payload_location(payload, **kwargs)

        return Location.objects.create(**payload)

    @classmethod
    def payload_location(cls, payload=LOCATION_A, **kwargs):
        data = copy.copy(payload)
        data.update(**kwargs)
        return data
