from django.apps import apps
from django.views.generic import View
from django.shortcuts import render


class Schedules(View):
    @staticmethod
    def get(request, *args, **kwargs):
        Schedule = apps.get_model('schedule', 'Schedule')

        statuses = Schedule.objects.all_location_status()
        all_ok = all([locationStatus.status.ok for locationStatus in statuses])
        status_code = 200 if all_ok else 500
        summary_status = 'OK' if all_ok else 'ERROR'

        return render(
            request,
            'status/one_check_multiple_locations.html',
            {'check_type': 'Schedules',
             'location_statuses': statuses,
             'summary_status': summary_status},
            status=status_code)
