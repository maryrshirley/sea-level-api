from rest_framework import generics
from rest_framework.exceptions import APIException


class NoTideGaugeException(APIException):
    status_code = 404
    default_detail = 'No tide gauge specified in URL.'


class RawMeasurementsIndex(generics.GenericAPIView):
    def get(self, req, format=None):
        raise NoTideGaugeException()
