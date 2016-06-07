from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin

from ..models import UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    max_num = 1
    can_delete = False


class UserAdmin(AuthUserAdmin):
    inlines = [UserProfileInline]
    list_display = ('username', 'first_name', 'last_name',
                    'is_internal_collector', 'available_locations')

    @staticmethod
    def is_internal_collector(user):
        return user.user_profile.is_internal_collector

    @staticmethod
    def available_locations(user):
        if user.user_profile.is_internal_collector:
            return '-'
        else:
            return user.user_profile.available_locations.count()

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
