from django.contrib import admin
from ..models import Vessel


@admin.register(Vessel)
class VesselAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
