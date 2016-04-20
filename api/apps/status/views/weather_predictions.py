from django.db.models.loading import get_model
from django.shortcuts import render
from django.views.generic import View


class WeatherPredictions(View):
    def get(self, request, *args, **kwargs):
        WeatherPrediction = get_model(app_label='predictions',
                                      model_name='WeatherPrediction')
        statuses = WeatherPrediction.objects.all_location_status()
        all_ok = all([locationStatus.status.ok for locationStatus in statuses])
        status_code = 200 if all_ok else 500
        summary_status = 'OK' if all_ok else 'ERROR'

        return render(
            request,
            'status/one_check_multiple_locations.html',
            {'check_type': 'Weather Predictions',
             'location_statuses': statuses,
             'summary_status': summary_status},
            status=status_code)
