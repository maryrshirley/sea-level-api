import datetime
import pytz

from django.views.generic import View
from django.shortcuts import render

from collections import namedtuple

from api.apps.locations.models import Location
from api.apps.predictions.models import SurgePrediction

from ..alert_manager import AlertType, is_alert_enabled
from .common import Status


LocationStatus = namedtuple('LocationStatus', 'location_name,status')


class SurgePredictions(View):
    def get(self, request, *args, **kwargs):

        (all_ok, location_statuses) = check_every_location()
        status_code = 200 if all_ok else 500
        summary_status = 'OK' if all_ok else 'ERROR'

        return render(
            request,
            'status/one_check_multiple_locations.html',
            {'check_type': 'Surge Predictions',
             'location_statuses': location_statuses,
             'summary_status': summary_status},
            status=status_code)


def check_every_location():
    location_statuses = [
        LocationStatus(loc.name, check_surge_predictions(loc))
        for loc in Location.objects.all()]

    all_locations_ok = all([ls.status.ok for ls in location_statuses])
    return (all_locations_ok, location_statuses)


def check_surge_predictions(location):
    """
    Test that we have a surge prediction for every minute in the next 36 hours.
    """
    if not is_alert_enabled(location, AlertType.surge_predictions):
        return Status(True, 'OK (alert disabled)')

    now = datetime.datetime.now(pytz.UTC)
    thirty_seven_hours_away = now + datetime.timedelta(hours=36)

    count = SurgePrediction.objects.filter(
        location=location,
        minute__datetime__gte=now,
        minute__datetime__lt=thirty_seven_hours_away).count()
    ok = (36 * 60) == count

    if ok:
        return Status(True, 'OK')
    else:
        return Status(
            False,
            'Missing data for next 36 hours: {} vs 2160'.format(count))
