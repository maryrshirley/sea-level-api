from django.db import models


CATEGORY_CHOICES = (
    ('sea_level', 'Sea Level'),
    ('wind', 'Wind'),
    ('wave', 'Wave'),
)

STATUS_CHOICES = (
    ('green', 'Green'),
    ('amber', 'Amber'),
    ('red', 'Red'),
)


class Notification(models.Model):
    location = models.ForeignKey('locations.Location', related_name='+')
    schedule = models.ForeignKey('schedule.Schedule', related_name='+')
    vessel = models.ForeignKey('vessel.Vessel', related_name='+')
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)

    @property
    def timestamp(self):
        if self.schedule.origin == self.location:
            return self.schedule.departure.datetime
        if self.schedule.destination == self.location:
            return self.schedule.arrival.datetime

        # XXX: Throw warning?

        return None
