import copy

from api.apps.locations.models import Location

LOCATION_A = {
    'slug': 'sample',
    'name': 'Sample',
    'min_depth': 2.1,
    'under_keal': 4.5,
}


class LocationMixin(object):

    def create_location(self, **kwargs):
        payload = self.payload_location(**kwargs)

        return Location.objects.create(**payload)

    def payload_location(self, payload=LOCATION_A, **kwargs):
        data = copy.copy(payload)
        data.update(**kwargs)
        return data
