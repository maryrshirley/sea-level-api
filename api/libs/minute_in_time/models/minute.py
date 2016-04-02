from __future__ import unicode_literals

import datetime
import pytz

from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from api.libs.view_helpers import now_rounded


class MinuteManager(models.Manager):

    def now_plus_24(self):
        now = now_rounded()
        now_plus_24 = now + datetime.timedelta(hours=24)

        return self.filter(datetime__range=(now, now_plus_24))


@python_2_unicode_compatible
class Minute(models.Model):
    class Meta:
        app_label = 'minute_in_time'

    datetime = models.DateTimeField(unique=True)

    objects = MinuteManager()

    def save(self, *args, **kwargs):
        if self.datetime.tzinfo != pytz.UTC:
            raise ValueError("datetime must have pytz.UTC timezone: {}".format(
                self.datetime))
        self.datetime = self.datetime.replace(second=0, microsecond=0)
        super(Minute, self).save(*args, **kwargs)

    def __str__(self):
        return "{}".format(self.datetime)
