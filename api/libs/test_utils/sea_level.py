from api.libs.param_parsers.parse_time import parse_datetime

from .base import Mixin

from .tide_prediction import TidePredictionMixin
from .surge_prediction import SurgePredictionMixin


class SeaLevelMixin(Mixin, TidePredictionMixin, SurgePredictionMixin):

    windows_endpoint = Mixin.API_URL + 'sea-levels/{location}/windows'

    windows_range_endpoint = windows_endpoint + \
        '?start={start}&end={end}&sea_level={sea_level}'

    windows_now_endpoint = windows_endpoint + '/now/?sea_level={sea_level}'

    def setUpSeaLevelRequirements(self):
        self.setUpTidePredictionRequirements()
        self.setUpSurgePredictionRequirements()

        tides = [self.TIDEPREDICTION_A, self.TIDEPREDICTION_B,
                 self.TIDEPREDICTION_C]
        self.tide_predictions = [
            self.create_tideprediction(data=data) for data in tides
        ]
        surges = [self.SURGEPREDICTION_A, self.SURGEPREDICTION_B,
                  self.SURGEPREDICTION_C]
        self.surge_predictions = [
            self.create_surgeprediction(data=data) for data in surges
        ]

    def tearDownSeaLevelRequirements(self):
        for prediction in self.tide_predictions:
            prediction.delete()
        for prediction in self.surge_predictions:
            prediction.delete()
        self.tearDownSurgePredictionRequirements()
        self.tearDownTidePredictionRequirements()

    def get_url(self, key):
        url = getattr(self, key)
        return url.format(location=self.location.slug,
                          start='2016-03-26T12:00:00Z',
                          end='2016-03-26T14:00:00Z',
                          sea_level=2.2)

    def sea_level_window_json(self):
        start = parse_datetime(self.TIDEPREDICTION_A['minute__datetime'])
        end = parse_datetime(self.TIDEPREDICTION_C['minute__datetime'])
        data = {
            'duration':
            {
                'total_seconds': (float)((end - start).seconds + 60),
            },
            'start':
            {
                'sea_level': self.TIDEPREDICTION_A['tide_level'] +
                self.SURGEPREDICTION_A['surge_level'],
                'datetime': self.TIDEPREDICTION_A['minute__datetime'],
            },
            'end':
            {
                'sea_level': self.TIDEPREDICTION_C['tide_level'] +
                self.SURGEPREDICTION_C['surge_level'],
                'datetime': self.TIDEPREDICTION_C['minute__datetime'],
            },
            'high_tide':
            {
                'sea_level': self.TIDEPREDICTION_B['tide_level'] +
                self.SURGEPREDICTION_B['surge_level'],
                'datetime': self.TIDEPREDICTION_B['minute__datetime'],
            },
        }
        return data
