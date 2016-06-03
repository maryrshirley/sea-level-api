from __future__ import unicode_literals
from datetime import timedelta
from functools import partial

from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from api.apps.locations.models import Location
from api.libs.view_helpers import now_rounded

from ..prediction_window import (pairwise, ONE_DAY, ONE_MIN, PredictionWindow,
                                 TimeRange, transform_time_window)


class CombinedPredictionObservationManager(models.Manager):
    def latest_object(self, location):
        now = now_rounded()
        qs = self.filter(location=location,
                         datetime__gte=now) \
                 .order_by('datetime')
        return qs[:1] if qs.count() else None

    def sea_level_windows(self, location_slug, sea_level, start, end):
        qs = self.filter(location__slug=location_slug,
                         datetime__range=[start, end],
                         predicted_sea_level__gte=sea_level
                         )
        if not qs.exists():
            return None

        time_range = TimeRange(start=start, end=end)
        extended_time_range = TimeRange(
            start=time_range.start - ONE_DAY,
            end=time_range.end + ONE_DAY)

        windows = self.split_prediction_into_windows(qs)
        return filter(None, map(
            partial(transform_time_window, time_range, extended_time_range),
            windows))

    def sea_level_windows_now(self, location_slug, sea_level):
        now = now_rounded()
        # Limit to looking 30 days ahead, otherwise the return set is large
        now_plus_1d = now + timedelta(days=1)

        windows = self.sea_level_windows(location_slug, sea_level, now,
                                         now_plus_1d)
        return list(windows)[:1] if windows else None

    @staticmethod
    def split_prediction_into_windows(predictions):
        if not predictions:
            return

        current_window = PredictionWindow(CombinedPredictionObservation)
        for p0, p1 in pairwise(predictions):
            current_window.add_prediction(p0)
            time_interval = p1.datetime - p0.datetime

            if time_interval > ONE_MIN:
                for window in current_window.spawn_for_each_high_tide():
                    yield window

                current_window = PredictionWindow(
                    CombinedPredictionObservation)
            elif time_interval <= timedelta(0):
                raise ValueError('Predictions must be ascending')
        current_window.add_prediction(p1)
        for window in current_window.spawn_for_each_high_tide():
            yield window


@python_2_unicode_compatible
class CombinedPredictionObservation(models.Model):
    class Meta:
        app_label = 'sea_levels'
        managed = False
    objects = CombinedPredictionObservationManager()

    datetime = models.DateTimeField(primary_key=True)
    location = models.ForeignKey(
        Location,
        null=False,
        on_delete=models.DO_NOTHING,
    )
    predicted_tide_level = models.FloatField(null=False)
    predicted_is_high = models.BooleanField(null=False, default=False)
    predicted_surge_level = models.FloatField(null=False)
    predicted_sea_level = models.FloatField(null=False)
    observed_sea_level = models.FloatField(null=True)
    derived_surge_level = models.FloatField(null=True)

    def __str__(self):
        return "{}".format(self.datetime)
