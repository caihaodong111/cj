import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.test import SimpleTestCase

from api.sentiment_service import SentimentAnalyzer, SentimentType, analyze_sentiment


class SentimentServiceTests(SimpleTestCase):
    def tearDown(self):
        SentimentAnalyzer.clear_cache()

    def test_sensitive_result_includes_consistent_sensitive_flags(self):
        result = analyze_sentiment(
            "\u8fd9\u91cc\u5305\u542b\u8272\u60c5\u3001\u8bc8\u9a97\u548c\u66b4\u529b\u5185\u5bb9"
        )

        self.assertEqual(result["sentiment"], SentimentType.SENSITIVE)
        self.assertEqual(result["score"], -1.0)
        self.assertTrue(result["labels"]["sensitive"])
        self.assertTrue(result["labels"]["adult"])
        self.assertTrue(result["labels"]["illegal"])
        self.assertTrue(result["labels"]["violence"])
        self.assertEqual(
            result["labels"]["matched_categories"],
            ["adult", "violence", "illegal"],
        )
        self.assertIn("\u8272\u60c5", result["labels"]["matched_keywords"])
        self.assertIn("\u8bc8\u9a97", result["labels"]["matched_keywords"])
        self.assertIn("\u66b4\u529b", result["labels"]["matched_keywords"])

    def test_ascii_sensitive_keywords_are_case_insensitive(self):
        lexicon = self._build_lexicon(
            adult_keywords=["FlagWord", "BetaTag"],
        )

        with self._patch_lexicon(lexicon):
            result = analyze_sentiment("this post contains flagword and BETATAG markers")

        self.assertEqual(result["sentiment"], SentimentType.SENSITIVE)
        self.assertTrue(result["labels"]["adult"])
        self.assertIn("FlagWord", result["labels"]["matched_keywords"])
        self.assertIn("BetaTag", result["labels"]["matched_keywords"])

    def test_ascii_sensitive_keywords_use_word_boundaries(self):
        lexicon = self._build_lexicon(
            adult_keywords=["OS"],
        )

        with self._patch_lexicon(lexicon):
            result = analyze_sentiment("we still have post office seats for everyone")

        self.assertNotEqual(result["sentiment"], SentimentType.SENSITIVE)
        self.assertFalse(result["labels"]["sensitive"])
        self.assertEqual(result["labels"]["matched_keywords"], [])

    def test_whitelist_phrase_suppresses_embedded_keyword_hit(self):
        result = analyze_sentiment(
            "\u793e\u533a\u53cd\u8bc8\u9a97\u5ba3\u4f20\u6d3b\u52a8\u63d0\u9192\u5927\u5bb6\u63d0\u9ad8\u8b66\u60d5"
        )

        self.assertNotEqual(result["sentiment"], SentimentType.SENSITIVE)
        self.assertFalse(result["labels"]["sensitive"])
        self.assertEqual(result["labels"]["matched_keywords"], [])

    def test_non_sensitive_result_keeps_empty_match_metadata(self):
        result = analyze_sentiment("\u4eca\u5929\u5fc3\u60c5\u5f88\u597d\uff0c\u611f\u8c22\u5927\u5bb6\u652f\u6301")

        self.assertEqual(result["sentiment"], SentimentType.POSITIVE)
        self.assertFalse(result["labels"]["sensitive"])
        self.assertEqual(result["labels"]["matched_categories"], [])
        self.assertEqual(result["labels"]["matched_keywords"], [])
        self.assertEqual(result["labels"]["matched_by_category"], {})

    def test_analyzer_loads_independent_lexicon_file(self):
        lexicon = self._build_lexicon(
            illegal_keywords=["CustomMarker"],
        )

        with self._patch_lexicon(lexicon):
            result = analyze_sentiment("the custommarker should be detected")

        self.assertEqual(result["sentiment"], SentimentType.SENSITIVE)
        self.assertTrue(result["labels"]["illegal"])
        self.assertIn("CustomMarker", result["labels"]["matched_keywords"])

    def _build_lexicon(
        self,
        adult_keywords=None,
        political_keywords=None,
        violence_keywords=None,
        illegal_keywords=None,
        adult_whitelist=None,
        political_whitelist=None,
        violence_whitelist=None,
        illegal_whitelist=None,
    ):
        return {
            "global_whitelist_phrases": [],
            "categories": {
                "adult": {
                    "keywords": adult_keywords or [],
                    "whitelist_phrases": adult_whitelist or [],
                },
                "political": {
                    "keywords": political_keywords or [],
                    "whitelist_phrases": political_whitelist or [],
                },
                "violence": {
                    "keywords": violence_keywords or [],
                    "whitelist_phrases": violence_whitelist or [],
                },
                "illegal": {
                    "keywords": illegal_keywords or [],
                    "whitelist_phrases": illegal_whitelist or [],
                },
            },
        }

    def _patch_lexicon(self, lexicon):
        temp_dir = TemporaryDirectory()
        lexicon_path = Path(temp_dir.name) / "sensitive_lexicon.json"
        lexicon_path.write_text(
            json.dumps(lexicon, ensure_ascii=True),
            encoding="utf-8",
        )

        patcher = patch.object(SentimentAnalyzer, "LEXICON_PATH", lexicon_path)
        patched = patcher.start()
        SentimentAnalyzer.clear_cache()

        class _LexiconContext:
            def __enter__(self_inner):
                return patched

            def __exit__(self_inner, exc_type, exc, tb):
                SentimentAnalyzer.clear_cache()
                patcher.stop()
                temp_dir.cleanup()

        return _LexiconContext()
