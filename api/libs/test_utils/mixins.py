import json

from .location import LocationMixin as ParentLocationMixin


class PostJsonMixin(object):
    def _post_json(self, url, data, **extras):
        return self.client.post(url,
                                data=json.dumps(data),
                                content_type='application/json',
                                **extras)


class LocationMixin(ParentLocationMixin):

    def setUpLocation(self):
        self.location = self.create_location(slug='liverpool',
                                             name='Liverpool')

    def tearDownLocation(self):
        self.location.delete()
