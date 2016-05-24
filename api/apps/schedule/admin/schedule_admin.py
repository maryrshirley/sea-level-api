from django.contrib import admin
from ..models import Schedule


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    raw_id_fields = ('departure', 'arrival',)
