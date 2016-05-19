from django.contrib import admin
from api.apps.predictions.models import SurgePrediction


@admin.register(SurgePrediction)
class SurgePredictionAdmin(admin.ModelAdmin):
    list_display = ('surge_level', 'location', 'minute')
    list_filter = ('location',)
    readonly_fields = ('surge_level', 'minute', 'location')

    def has_add_permission(self, request):
        return False
