from django.views.generic import View
from django.shortcuts import render


from api.apps.locations.models import Location


class StatusIndex(View):
    @staticmethod
    def get(request, *args, **kwargs):

        locations = Location.objects.all()
        ok = locations.count() > 0

        if ok:
            status_code = 200
            summary_status = 'OK'
            long_status = 'App is running and talking to database.'
        else:
            status_code = 500
            summary_status = 'ERROR'
            long_status = 'No locations found in database.'

        return render(
            request,
            'status/status_index.html',
            {'locations': locations,
             'ok': ok,
             'summary_status': summary_status,
             'long_status': long_status,
             },
            status=status_code)
