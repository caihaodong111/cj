from datetime import datetime
from zoneinfo import ZoneInfo

from django.test import SimpleTestCase

from media_platform.time_utils import coerce_timestamp_ms


class TimeUtilsTests(SimpleTestCase):
    def test_numeric_seconds_are_normalized_to_millis(self):
        self.assertEqual(coerce_timestamp_ms(1_714_000_000), 1_714_000_000_000)

    def test_existing_millis_are_preserved(self):
        self.assertEqual(coerce_timestamp_ms(1_714_000_000_123), 1_714_000_000_123)

    def test_tieba_datetime_string_is_parsed_with_china_timezone(self):
        expected = int(
            datetime(2026, 5, 8, 12, 30, tzinfo=ZoneInfo("Asia/Shanghai")).timestamp() * 1000
        )
        self.assertEqual(coerce_timestamp_ms("2026-05-08 12:30"), expected)

    def test_iso_datetime_string_is_supported(self):
        expected = int(
            datetime(2026, 5, 8, 12, 30, tzinfo=ZoneInfo("Asia/Shanghai")).timestamp() * 1000
        )
        self.assertEqual(coerce_timestamp_ms("2026-05-08T12:30:00"), expected)
