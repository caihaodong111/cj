from unittest.mock import MagicMock, Mock, patch

from django.test import SimpleTestCase
from rest_framework.test import APIRequestFactory

from api import views


class GetMonitorFeedViewTests(SimpleTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    @staticmethod
    def _mock_monitor_feed_manager(*, rows, aggregate=None):
        manager = Mock()
        manager.aggregate.return_value = aggregate or {
            "total_count": len(rows),
            "sensitive_count": 0,
            "positive_count": 0,
            "negative_count": 0,
            "neutral_count": len(rows),
            "avg_sentiment_score": None,
        }

        ordered_queryset = Mock()
        values_queryset = MagicMock()

        manager.order_by.return_value = ordered_queryset
        ordered_queryset.values.return_value = values_queryset
        values_queryset.__getitem__.return_value = rows

        return manager, values_queryset

    def test_get_monitor_feed_is_read_only_when_sentiment_fields_are_missing(self):
        rows = [{
            "id": 1,
            "platform": "wb",
            "platform_name": "微博",
            "content_id": "wb-1",
            "content": "需要保持只读的内容",
            "author": "tester",
            "url": "https://example.com/item/1",
            "created_at": 1_714_000_000_000,
            "sentiment": "neutral",
            "sentiment_score": None,
            "sentiment_labels": None,
            "is_sensitive": None,
        }]
        manager, _ = self._mock_monitor_feed_manager(rows=rows)
        request = self.factory.get("/api/monitor/feed", {"page": 1, "page_size": 10})

        with patch.object(views.MonitorFeed, "objects", manager):
            response = views.get_monitor_feed(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["items"]), 1)
        self.assertEqual(response.data["items"][0]["sentiment"], "neutral")
        self.assertEqual(response.data["items"][0]["sentiment_score"], 0)
        self.assertEqual(response.data["items"][0]["sentiment_labels"], {})
        self.assertFalse(response.data["items"][0]["is_sensitive"])
        manager.filter.assert_not_called()

    def test_get_monitor_feed_caps_page_size(self):
        rows = []
        manager, values_queryset = self._mock_monitor_feed_manager(rows=rows)
        request = self.factory.get("/api/monitor/feed", {"page": 1, "page_size": 1000})

        with patch.object(views.MonitorFeed, "objects", manager):
            response = views.get_monitor_feed(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data["pagination"]["page_size"],
            views.MONITOR_FEED_MAX_PAGE_SIZE,
        )
        values_queryset.__getitem__.assert_called_once_with(
            slice(0, views.MONITOR_FEED_MAX_PAGE_SIZE, None)
        )
