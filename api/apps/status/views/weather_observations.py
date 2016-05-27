from django.apps import apps
from django.shortcuts import render
from django.views.generic import View


class WeatherObservations(View):
    def get(self, request, *args, **kwargs):
        WeatherObservation = apps.get_model('observations',
                                            'WeatherObservation')
        statuses = WeatherObservation.objects.all_location_status()
        all_ok = all([locationStatus.status.ok for locationStatus in statuses])
        status_code = 200 if all_ok else 500
        summary_status = 'OK' if all_ok else 'ERROR'

        return render(
            request,
            'status/one_check_multiple_locations.html',
            {'check_type': 'Weather Observations',
             'location_statuses': statuses,
             'summary_status': summary_status},
            status=status_code)
