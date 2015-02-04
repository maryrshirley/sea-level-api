import datetime
import pytz

from django.views.generic import View
from django.shortcuts import render

from collections import namedtuple

from api.apps.locations.models import Location
from api.apps.observations.models import Observation

from ..alert_manager import AlertType, is_alert_enabled
from .common import Status


LocationStatus = namedtuple('LocationStatus', 'location_name,status')


class Observations(View):
    def get(self, request, *args, **kwargs):

        location = Location.objects.get(slug=kwargs['location_slug'])

        status = check_observations(location)
        status_code = 200 if status.ok else 500
        summary_status = 'OK' if status.ok else 'ERROR'

        return render(
            request,
            'status/one_check_single_location.html',
            {'check_type': 'Observations',
             'location_name': location.name,
             'summary_status': summary_status,
             'status': status},
            status=status_code)


def check_observations(location):
    if not is_alert_enabled(location, AlertType.observations):
        return Status(True, 'OK (alert disabled)')

    one_hour_ago = (datetime.datetime.now(pytz.UTC)
                    - datetime.timedelta(minutes=120))

    ok = Observation.objects.filter(
        location=location,
        minute__datetime__gte=one_hour_ago).exists()

    if ok:
        return Status(True, 'OK')
    else:
        return Status(False, '> 2 hours old')
