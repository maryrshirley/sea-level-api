import copy

from api.apps.vessel.models import Vessel

VESSEL_A = {
    'slug': 'isle-of-arran',
    'name': 'ISLE OF ARRAN',
    'imo': '8219554',
    'draft': 3.2,
}


class VesselMixin(object):

    def create_vessel(self, **kwargs):
        payload = self.payload_vessel(**kwargs)

        return Vessel.objects.create(**payload)

    def payload_vessel(self, payload=VESSEL_A, **kwargs):
        data = copy.copy(payload)
        data.update(**kwargs)
        return data
