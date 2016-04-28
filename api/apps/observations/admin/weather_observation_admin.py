from django.contrib import admin
from api.apps.observations.models import WeatherObservation


@admin.register(WeatherObservation)
class WeatherObservationAdmin(admin.ModelAdmin):
    list_display = ('location', 'supplier', 'datetime')
    list_filter = ('location', 'supplier')

    def has_add_permission(self, request):
        return False

    def get_readonly_fields(self, request, obj=None):
        return [f.name for f in self.model._meta.fields]
