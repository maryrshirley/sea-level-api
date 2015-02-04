from django.views.generic import View
from django.shortcuts import render

from collections import namedtuple

from api.apps.locations.models import Location

from .surge_predictions import check_surge_predictions
from .tide_predictions import check_tide_predictions
from .observations import check_observations

LocationStatus = namedtuple('LocationStatus', 'name,checks')
Check = namedtuple('Check', 'name,status_text,status_class')


class StatusAll(View):
    def get(self, request, *args, **kwargs):

        all_ok, location_statuses = get_checks_by_location()
        status_code = 200 if all_ok else 500
        summary_status = 'OK' if all_ok else 'ERROR'

        return render(
            request,
            'status/status_all.html',
            {'location_statuses': location_statuses,
             'summary_status': summary_status},
            status=status_code)


def get_checks_by_location():
    statuses = []
    all_ok = True

    for location in Location.objects.all():
        ok, location_status = get_location_status(location)
        all_ok = all_ok and ok
        statuses.append(location_status)

    return all_ok, statuses


def get_location_status(location):
    checks_to_run = [
        ('Tide predictions', check_tide_predictions),
        ('Surge predictions', check_surge_predictions),
        ('Observations', check_observations),
    ]
    all_ok = True
    checks = []
    for name, function in checks_to_run:
        status = function(location)
        all_ok = all_ok and status.ok
        checks.append(Check(
            name=name,
            status_text=status.text,
            status_class='success' if status.ok else 'danger'))

    return all_ok, LocationStatus(name=location.name, checks=checks)
