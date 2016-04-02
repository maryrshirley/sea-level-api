import json


class PostJsonMixin(object):
    def _post_json(self, url, data, **extras):
        return self.client.post(url,
                                data=json.dumps(data),
                                content_type='application/json',
                                **extras)
