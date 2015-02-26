import datetime
import pytz

from django.views.generic import View
from django.shortcuts import render

from collections import namedtuple

from api.apps.predictions.models import TidePrediction

from api.apps.locations.models import Location

from ..alert_manager import AlertType, is_alert_enabled
from .common import Status


LocationStatus = namedtuple('LocationStatus', 'location_name,status')


class TidePredictions(View):
    def get(self, request, *args, **kwargs):

        (all_ok, location_statuses) = check_every_location()
        status_code = 200 if all_ok else 500
        summary_status = 'OK' if all_ok else 'ERROR'

        return render(
            request,
            'status/one_check_multiple_locations.html',
            {'check_type': 'Tide Predictions',
             'location_statuses': location_statuses,
             'summary_status': summary_status},
            status=status_code)


def check_every_location():
    location_statuses = [
        LocationStatus(loc.name, check_tide_predictions(loc))
        for loc in Location.objects.all()]

    all_locations_ok = all([ls.status.ok for ls in location_statuses])
    return (all_locations_ok, location_statuses)


def check_tide_predictions(location):
    if not is_alert_enabled(location, AlertType.tide_predictions):
        return Status(True, 'OK (alert disabled)')

    one_month_away = (datetime.datetime.now(pytz.UTC) +
                      datetime.timedelta(days=30))

    ok = TidePrediction.objects.filter(
        location=location,
        minute__datetime__gte=one_month_away).exists()

    if ok:
        return Status(True, 'OK')
    else:
        return Status(False, '< 30 days left')
