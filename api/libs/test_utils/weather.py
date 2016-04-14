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

PREDICTION_WEATHER_B = {
    'precipitation': 20,
    'pressure': 21,
    'wind_gust': 22,
    'wind_direction': u'S',
    'wind_degrees': 24,
    'wind_speed': 25,
    'temperature': 26,
    'supplier': u'met_office',
    'valid_from': '2016-03-27T12:00:00Z',
    'valid_to': '2016-03-27T18:00:00Z',
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

OBSERVATION_WEATHER_B = {
    'precipitation': 17,
    'pressure': 18,
    'wind_gust': 19,
    'wind_speed': 20,
    'wind_direction': u'WS',
    'wind_degrees': 25,
    'temperature': 26,
    'datetime': '2014-06-12T10:34:00Z',
}


class CreatePredictionMixin(object):
    def create_prediction(self, **kwargs):
        payload = self.payload_prediction(**kwargs)
        payload['location'] = self.location

        return WeatherPrediction.objects.create(**payload)

    def create_prediction_now(self, **kwargs):
        payload = self.payload_prediction_now(**kwargs)

        return self.create_prediction(**payload)

    def payload_prediction(self, alternative=False, **kwargs):
        if alternative:
            data = copy.copy(PREDICTION_WEATHER_B)
        else:
            data = copy.copy(PREDICTION_WEATHER)
        data.update(**kwargs)

        return data

    def payload_prediction_now(self, alternative=False, **kwargs):
        data = {
            'valid_from': delta(),
            'valid_to': delta(hours=2)
        }
        data.update(**kwargs)

        return self.payload_prediction(alternative, **data)


class CreateObservationMixin(object):
    def create_observation(self, **kwargs):
        data = copy.copy(OBSERVATION_WEATHER)
        data['location_id'] = self.location.id
        data.update(**kwargs)
        return WeatherObservation.objects.create(**data)

    def create_observation_now(self, **kwargs):
        return self.create_observation(datetime=delta())
