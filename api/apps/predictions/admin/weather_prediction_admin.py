from django.contrib import admin
from api.apps.predictions.models import WeatherPrediction


@admin.register(WeatherPrediction)
class WeatherPredictionAdmin(admin.ModelAdmin):

    def has_add_permission(self, request):
        return False

    def get_readonly_fields(self, request, obj=None):
        return [f.name for f in self.model._meta.fields]
