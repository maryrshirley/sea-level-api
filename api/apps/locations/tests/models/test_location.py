from django.core.exceptions import ValidationError
from django.test import TestCase
from nose.tools import assert_equal

from api.libs.test_utils.location import LocationMixin


class TestLocation(TestCase, LocationMixin):
    def test_that_visible_defaults_to_true(self):
        location = self.create_location()
        assert_equal(True, location.visible)
        assert_equal(2.1, location.min_depth)
        assert_equal(4.5, location.under_keal)

    def test_that_negatives_are_rejected(self):
        with self.assertRaises(ValidationError) as ra:
            location = self.create_location(min_depth=-1)
            location.clean_fields()

        self.assertEqual(["Ensure this value is greater than or equal to 0."],
                         ra.exception.messages)
        location.delete()

        with self.assertRaises(ValidationError) as ra:
            location = self.create_location(under_keal=-1)
            location.clean_fields()

        self.assertEqual(["Ensure this value is greater than or equal to 0."],
                         ra.exception.messages)
        location.delete()
