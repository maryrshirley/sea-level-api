from django.test import TestCase

from api.libs.test_utils.schedule import ScheduleMixin


class TestSchedule(TestCase, ScheduleMixin):

    def setUp(self):
        super(TestSchedule, self).setUp()
        self.setUpScheduleRequirements()

    def tearDown(self):
        self.tearDownScheduleRequirements()
        super(TestSchedule, self).tearDown()

    def test_defaults(self):
        schedule = self.create_schedule()

        schedule.delete()
