import copy
import datetime

from api.libs.test_utils.datetime_utils import delta

from api.apps.predictions.models import WeatherPrediction
from api.apps.observations.models import WeatherObservation
from api.libs.view_helpers import format_datetime


PREDICTION_WEATHER = {
    'precipitation': 10.1,
    'pressure': 11.2,
    'wind_gust': 12.3,
    'wind_direction': u'E',
    'wind_degrees': 14.4,
    'wind_speed': 15.5,
    'temperature': 16.6,
    'supplier': u'met_office',
    'valid_from': '2016-03-26T12:00:00Z',
    'valid_to': '2016-03-26T18:00:00Z',
}

PREDICTION_WEATHER_B = {
    'precipitation': 20.9,
    'pressure': 21.8,
    'wind_gust': 22.7,
    'wind_direction': u'S',
    'wind_degrees': 24.5,
    'wind_speed': 25.4,
    'temperature': 26.3,
    'supplier': u'met_office',
    'valid_from': '2016-03-27T12:00:00Z',
    'valid_to': '2016-03-27T18:00:00Z',
}

OBSERVATION_WEATHER = {
    'precipitation': 7.1,
    'pressure': 8.2,
    'wind_gust': 9.3,
    'wind_speed': 10.4,
    'wind_direction': u'S',
    'wind_degrees': 12.5,
    'temperature': 13.6,
    'datetime': '2014-06-10T10:34:00Z',
}

OBSERVATION_WEATHER_B = {
    'precipitation': 17.9,
    'pressure': 18.8,
    'wind_gust': 19.7,
    'wind_speed': 20.6,
    'wind_direction': u'W',
    'wind_degrees': 25.5,
    'temperature': 26.4,
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
        payload = self.payload_observation(**kwargs)
        payload['location'] = self.location

        return WeatherObservation.objects.create(**payload)

    def create_observation_now(self, **kwargs):
        payload = self.payload_observation_now(**kwargs)

        return self.create_observation(**payload)

    def payload_observation(self, alternative=False, **kwargs):
        if alternative:
            data = copy.copy(OBSERVATION_WEATHER)
        else:
            data = copy.copy(OBSERVATION_WEATHER_B)
        data.update(**kwargs)
        return data

    def payload_observation_now(self, alternative=False, **kwargs):
        return self.payload_observation(alternative, datetime=delta())


def encode_datetime(payload):
    return {k: format_datetime(v) if type(v) is datetime.datetime else v
            for k, v in payload.items()}
