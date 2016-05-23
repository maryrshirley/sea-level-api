from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.utils import DataError
from django.test import TestCase

from nose_parameterized import parameterized

from api.libs.test_utils.vessel import VesselMixin


class TestVessel(TestCase, VesselMixin):
    def test_defaults(self):
        vessel = self.create_vessel()

        vessel.delete()

    def test_imo_unique_raises(self):
        vessel = self.create_vessel()
        vessel.clean_fields()

        with self.assertRaises(IntegrityError) as ra:
            vessel2 = self.create_vessel()
            vessel2.clean_fields()
        exception = "duplicate key value violates unique constraint"\
                    " \"vessel_vessel_imo_key\"\nDETAIL:  Key (imo)=(8219554)"\
                    " already exists.\n"
        self.assertEqual(exception, str(ra.exception))

    def test_imo_short_length_raises(self):
        with self.assertRaises(ValidationError) as ra:
            vessel = self.create_vessel(imo=1)
            vessel.clean_fields()
        self.assertEqual(
            ['Ensure this value has at least 7 characters (it has 1).'],
            ra.exception.messages)
        vessel.delete()

    def test_imo_long_length_raises(self):
        with self.assertRaises(DataError) as ra:
            vessel = self.create_vessel(imo=12345678)
            vessel.clean_fields()
        self.assertEqual(
            'value too long for type character varying(7)\n',
            str(ra.exception))

    @parameterized.expand([
        ("abcdefg",),
        ("12foo67",)
    ])
    def test_imo_invalid_types_raises(self, imo):
        with self.assertRaises(ValidationError) as ra:
            vessel = self.create_vessel(imo=imo)
            vessel.clean_fields()
        self.assertEqual(["Must be numbers only"],
                         ra.exception.messages)

    def test_draft_negative_raises(self):
        with self.assertRaises(ValidationError) as ra:
            vessel = self.create_vessel(draft=-1)
            vessel.clean_fields()
        self.assertEqual(["Ensure this value is greater than or equal to 0."],
                         ra.exception.messages)
