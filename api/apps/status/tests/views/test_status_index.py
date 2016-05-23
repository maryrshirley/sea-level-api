from .helpers import TestCheckBase


class TestStatusIndexView(TestCheckBase):
    BASE_PATH = '/1/_status/'

    def _setup_all_ok(self):
        pass

    def _setup_not_ok(self):
        """
        Delete locations, this will cause a failure.
        """
        self.liverpool.delete()
        self.southampton.delete()

    def test_that_status_index_is_ok_when_it_can_retrieve_some_locations(self):
        self._setup_all_ok()
        response = self.client.get(self.BASE_PATH)
        self.assertContains(response, 'API Health: OK', status_code=200)
        self.assertContains(response,
                            'App is running and talking to database.',
                            status_code=200)

    def test_that_status_index_has_error_when_no_locations(self):
        self._setup_not_ok()
        response = self.client.get(self.BASE_PATH)
        self.assertContains(response, 'API Health: ERROR', status_code=500)
        self.assertContains(response,
                            'No locations found in database.',
                            status_code=500)
