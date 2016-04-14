import copy

from api.libs.test_utils.datetime_utils import delta

from api.apps.predictions.models import WeatherPrediction
from api.apps.observations.models import WeatherObservation


PREDICTION_WEATHER = {
    'precipitation': 10,
    'pressure': 11,
    'wind_gust': 12,
    'wind_direction': u'E',
    'wind_degrees': 14,
    'wind_speed': 15,
    'temperature': 16,
    'supplier': u'met_office',
    'valid_from': '2016-03-26T12:00:00Z',
    'valid_to': '2016-03-26T18:00:00Z',
}

OBSERVATION_WEATHER = {
    'precipitation': 7,
    'pressure': 8,
    'wind_gust': 9,
    'wind_speed': 10,
    'wind_direction': u'S',
    'wind_degrees': 12,
    'temperature': 13,
    'datetime': '2014-06-10T10:34:00Z',
}


class CreatePredictionMixin(object):
    def create_prediction(self, **kwargs):
        data = copy.copy(PREDICTION_WEATHER)
        data['location'] = self.location
        data.update(**kwargs)

        return WeatherPrediction.objects.create(**data)

    def create_prediction_now(self, **kwargs):
        data = {
            'valid_from': delta(),
            'valid_to': delta(hours=2)
        }
        data.update(**kwargs)

        return self.create_prediction(**data)


class CreateObservationMixin(object):
    def create_observation(self, **kwargs):
        data = copy.copy(OBSERVATION_WEATHER)
        data['location_id'] = self.location.id
        data.update(**kwargs)
        return WeatherObservation.objects.create(**data)

    def create_observation_now(self, **kwargs):
        return self.create_observation(datetime=delta())
