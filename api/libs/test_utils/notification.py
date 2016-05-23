import copy

# XXX: Maybe replace by the parent model getters?
from api.apps.locations.models import Location
from api.apps.schedule.models import Schedule
from api.apps.vessel.models import Vessel
from api.apps.notifications.models import Notification

from .schedule import ScheduleMixin


class NotificationMixin(ScheduleMixin):

    notifications_endpoint = '/1/notifications/{0}/'

    # category: sea_level, wind, wave
    # status: amber, red, green

    NOTIFICATION_A = {
        'location__slug': 'liverpool',
        'schedule__code': 'ST_LIV_HEY_20160326_AM',
        'vessel__imo': '8219554',
        'category': 'sea_level',
        'status': 'red',
    }

    def create_notification(self, payload=None, **kwargs):
        if not payload:
            payload = self.payload_notification(**kwargs)
        payload = self.related_notification_payload(payload)
        return Notification.objects.create(**payload)

    def related_notification_payload(self, payload):
        # XXX: Better way for grouping these?
        get_location = lambda x, y: Location.objects.get(slug=x[y + '__slug'])
        get_schedule = lambda x, y: Schedule.objects.get(code=x[y + '__code'])
        get_vessel = lambda x, y: Vessel.objects.get(imo=x[y + '__imo'])

        payload['location'] = get_location(payload, 'location')
        payload['schedule'] = get_schedule(payload, 'schedule')
        payload['vessel'] = get_vessel(payload, 'vessel')
        del payload['location__slug']
        del payload['schedule__code']
        del payload['vessel__imo']
        return payload

    def payload_notification(self, payload=NOTIFICATION_A, **kwargs):
        data = copy.copy(payload)
        data.update(**kwargs)
        return data

    def payload_notifications_read(self, payload):
        payload = copy.copy(payload)
        del payload['location']
        del payload['schedule']
        del payload['vessel']
        return payload

    def setUpNotificationRequirements(self):
        self.setUpScheduleRequirements()
        self.schedule = self.create_schedule()

    def tearDownNotificationRequirements(self):
        self.schedule.delete()
        self.tearDownScheduleRequirements()
