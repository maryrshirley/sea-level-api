from rest_framework import generics
from rest_framework.response import Response
from rest_framework.reverse import reverse


class ApiRoot(generics.GenericAPIView):
    @staticmethod
    def get(req, format=None):
        return Response({
            'links': [
                {'href': reverse('location-list', request=req, format=format)},
                {'href': reverse('observation-weather',
                                 request=req, format=format)},
                {'href': reverse('tide-levels', request=req, format=format)},
                {'href': reverse('tide-windows', request=req, format=format)},
                {'href': reverse('prediction-weather',
                                 request=req, format=format)},
                {'href': reverse('sea-levels', request=req, format=format)},
            ]
        })
