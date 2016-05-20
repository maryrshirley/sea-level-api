import copy

from api.apps.vessel.models.vessel import Vessel

VESSEL_A = {
    'slug': 'sample',
    'name': 'Sample',
    'imo': '1234567',
    'draft': 1.2,
}


class VesselMixin(object):

    def create_vessel(self, **kwargs):
        payload = self.payload_vessel(**kwargs)

        return Vessel.objects.create(**payload)

    def payload_vessel(self, payload=VESSEL_A, **kwargs):
        data = copy.copy(payload)
        data.update(**kwargs)
        return data
