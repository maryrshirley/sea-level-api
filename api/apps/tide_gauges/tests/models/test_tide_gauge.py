from nose.tools import assert_equal
from django.test import TestCase

from api.apps.tide_gauges.models import TideGauge, TideGaugeLocationLink
from api.libs.test_utils.location import LocationMixin


class TestLinkedLocation(TestCase, LocationMixin):
    @classmethod
    def setUpClass(cls):
        cls.gauge_unlinked = TideGauge.objects.create(slug='unlinked')
        cls.gauge_linked = TideGauge.objects.create(slug='linked')

    def setUp(self):
        self.linked_location = self.create_location(slug='somelocation',
                                                    name='Somelocation')
        self.link = TideGaugeLocationLink.objects.create(
            tide_gauge=self.gauge_linked,
            location=self.linked_location)

        super(TestLinkedLocation, self).setUp()

    def tearDown(self):
        self.link.delete()
        self.linked_location.delete()
        super(TestLinkedLocation, self).tearDown()

    @classmethod
    def tearDownClass(cls):
        cls.gauge_unlinked.delete()
        cls.gauge_linked.delete()

    def test_that_linked_location_returns_none_for_unlinked_gauge(self):
        assert_equal(None, self.gauge_unlinked.linked_location)

    def test_that_linked_location_returns_location_for_linked_gauge(self):
        assert_equal(self.linked_location, self.gauge_linked.linked_location)
