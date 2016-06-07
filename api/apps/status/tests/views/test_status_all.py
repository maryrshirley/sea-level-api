import datetime

from freezegun import freeze_time


from api.apps.observations.models import Observation
from api.apps.observations.utils import create_observation
from api.apps.predictions.models import TidePrediction, SurgePrediction
from api.apps.predictions.utils import create_tide_prediction


from .helpers import (BASE_TIME, _make_good_surge_predictions, TestCheckBase)


class TestStatusAllView(TestCheckBase):
    BASE_PATH = '/1/_status/all/'

    def _setup_all_ok(self):

        create_tide_prediction(
            self.liverpool,
            BASE_TIME + datetime.timedelta(days=31),
            5.0)
        _make_good_surge_predictions(self.liverpool)
        create_observation(
            self.liverpool,
            BASE_TIME - datetime.timedelta(minutes=10),
            4.5,
            True)
        self.southampton.delete()  # so that it doesn't come up as a failure

    @staticmethod
    def _setup_not_ok():
        """
        Create two locations but with no data - this will cause a failure.
        """

        TidePrediction.objects.all().delete()
        SurgePrediction.objects.all().delete()
        Observation.objects.all().delete()

    def test_that_status_page_has_api_status_ok_when_all_ok(self):
        self._setup_all_ok()
        with freeze_time(BASE_TIME):
            response = self.client.get(self.BASE_PATH)
        self.assertContains(response, 'API Status: OK', status_code=200)

    def test_that_status_page_has_api_status_error_when_something_not_ok(self):
        self._setup_not_ok()
        with freeze_time(BASE_TIME):
            response = self.client.get(self.BASE_PATH)
        self.assertContains(response, 'API Status: ERROR', status_code=500)
