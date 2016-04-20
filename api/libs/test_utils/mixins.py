import json

from api.apps.locations.models import Location


class PostJsonMixin(object):
    def _post_json(self, url, data, **extras):
        return self.client.post(url,
                                data=json.dumps(data),
                                content_type='application/json',
                                **extras)


class LocationMixin(object):

    def setUpLocation(self):
        self.location = Location.objects.create(
            slug='liverpool', name='Liverpool')

    def tearDownLocation(self):
        self.location.delete()
