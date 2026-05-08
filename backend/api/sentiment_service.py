# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

"""
情绪分析服务
用于分析内容的情绪倾向（积极、消极、中性、敏感）
"""

import json
import re
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List


class SentimentType:
    """情绪类型枚举"""

    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    SENSITIVE = "sensitive"


class SentimentAnalyzer:
    """基于规则的情绪分析器"""

    LEXICON_PATH = Path(__file__).with_name("sensitive_lexicon.json")

    DEFAULT_LEXICON = {
        "global_whitelist_phrases": [],
        "categories": {
            "adult": {
                "keywords": [],
                "whitelist_phrases": [],
            },
            "political": {
                "keywords": [],
                "whitelist_phrases": [],
            },
            "violence": {
                "keywords": [],
                "whitelist_phrases": [],
            },
            "illegal": {
                "keywords": [],
                "whitelist_phrases": [],
            },
        },
    }

    POSITIVE_KEYWORDS = [
        "开心",
        "快乐",
        "幸福",
        "美好",
        "优秀",
        "棒",
        "赞",
        "喜欢",
        "爱",
        "感谢",
        "支持",
        "加油",
        "努力",
        "成功",
        "胜利",
        "棒棒",
        "厉害",
        "太好了",
        "😊",
        "😄",
        "👍",
        "💪",
        "❤️",
        "🎉",
    ]

    NEGATIVE_KEYWORDS = [
        "难过",
        "伤心",
        "痛苦",
        "失望",
        "糟糕",
        "差",
        "讨厌",
        "恨",
        "愤怒",
        "生气",
        "烦",
        "痛苦",
        "失败",
        "完蛋",
        "垃圾",
        "废物",
        "没用",
        "😭",
        "😢",
        "😡",
        "😠",
        "💔",
    ]

    ASCII_WORD_CHARS = "0-9A-Za-z_"

    @classmethod
    def analyze(cls, content: str, title: str = "") -> Dict[str, Any]:
        if not content and not title:
            return cls._neutral_result()

        text = f"{title or ''} {content or ''}".strip()
        normalized_text = text.casefold()

        sensitive_result = cls._check_sensitive(text)
        if sensitive_result["is_sensitive"]:
            return {
                "sentiment": SentimentType.SENSITIVE,
                "score": -1.0,
                "labels": sensitive_result["labels"],
            }

        positive_count = sum(
            1 for keyword in cls.POSITIVE_KEYWORDS if keyword.casefold() in normalized_text
        )
        negative_count = sum(
            1 for keyword in cls.NEGATIVE_KEYWORDS if keyword.casefold() in normalized_text
        )

        total_count = positive_count + negative_count
        if total_count == 0:
            score = 0.0
        else:
            score = (positive_count - negative_count) / total_count

        if score > 0.3:
            sentiment = SentimentType.POSITIVE
        elif score < -0.3:
            sentiment = SentimentType.NEGATIVE
        else:
            sentiment = SentimentType.NEUTRAL

        return {
            "sentiment": sentiment,
            "score": score,
            "labels": cls._empty_labels(cls._get_sensitive_config()["category_names"]),
        }

    @classmethod
    def _check_sensitive(cls, text: str) -> Dict[str, Any]:
        config = cls._get_sensitive_config()
        labels = cls._empty_labels(config["category_names"])
        matched_categories: List[str] = []
        matched_keywords: List[str] = []
        matched_by_category: Dict[str, List[str]] = {}

        global_whitelist_spans = cls._collect_match_spans(text, config["global_whitelist"])

        for category in config["category_names"]:
            category_config = config["categories"][category]
            category_whitelist_spans = cls._collect_match_spans(
                text,
                category_config["whitelist"],
            )
            whitelist_spans = cls._merge_spans(global_whitelist_spans + category_whitelist_spans)
            category_hits = cls._find_unwhitelisted_keywords(
                text,
                category_config["keywords"],
                whitelist_spans,
            )

            if category_hits:
                labels[category] = True
                matched_categories.append(category)
                matched_by_category[category] = category_hits
                matched_keywords.extend(category_hits)

        labels["sensitive"] = bool(matched_categories)
        labels["matched_categories"] = matched_categories
        labels["matched_keywords"] = list(dict.fromkeys(matched_keywords))
        labels["matched_by_category"] = matched_by_category

        return {
            "is_sensitive": labels["sensitive"],
            "labels": labels,
        }

    @classmethod
    def clear_cache(cls) -> None:
        cls._build_sensitive_config.cache_clear()

    @classmethod
    def _get_sensitive_config(cls) -> Dict[str, Any]:
        return cls._build_sensitive_config(cls._get_lexicon_cache_key())

    @classmethod
    def _get_lexicon_cache_key(cls) -> str:
        try:
            stat = cls.LEXICON_PATH.stat()
        except OSError:
            return "default"
        return f"{stat.st_mtime_ns}:{stat.st_size}"

    @classmethod
    @lru_cache(maxsize=1)
    def _build_sensitive_config(cls, _cache_key: str) -> Dict[str, Any]:
        lexicon = cls._load_lexicon()
        compiled_categories: Dict[str, Dict[str, List[tuple[str, re.Pattern]]]] = {}

        for category, category_config in lexicon["categories"].items():
            compiled_categories[category] = {
                "keywords": [
                    cls._compile_phrase_matcher(keyword)
                    for keyword in category_config.get("keywords", [])
                ],
                "whitelist": [
                    cls._compile_phrase_matcher(phrase)
                    for phrase in category_config.get("whitelist_phrases", [])
                ],
            }

        return {
            "category_names": list(lexicon["categories"].keys()),
            "global_whitelist": [
                cls._compile_phrase_matcher(phrase)
                for phrase in lexicon.get("global_whitelist_phrases", [])
            ],
            "categories": compiled_categories,
        }

    @classmethod
    def _load_lexicon(cls) -> Dict[str, Any]:
        lexicon = deepcopy(cls.DEFAULT_LEXICON)

        try:
            raw_lexicon = json.loads(cls.LEXICON_PATH.read_text(encoding="utf-8"))
        except (OSError, TypeError, ValueError):
            return lexicon

        if not isinstance(raw_lexicon, dict):
            return lexicon

        raw_categories = raw_lexicon.get("categories")
        category_names = list(lexicon["categories"].keys())
        if isinstance(raw_categories, dict):
            extra_categories = [
                category for category in raw_categories.keys() if category not in lexicon["categories"]
            ]
            category_names.extend(extra_categories)

        normalized_categories: Dict[str, Dict[str, List[str]]] = {}
        for category in category_names:
            default_config = lexicon["categories"].get(
                category,
                {"keywords": [], "whitelist_phrases": []},
            )
            raw_category_config = raw_categories.get(category) if isinstance(raw_categories, dict) else None

            keywords_source = (
                raw_category_config.get("keywords")
                if isinstance(raw_category_config, dict)
                else default_config.get("keywords")
            )
            whitelist_source = (
                raw_category_config.get("whitelist_phrases")
                if isinstance(raw_category_config, dict)
                else default_config.get("whitelist_phrases")
            )

            normalized_categories[category] = {
                "keywords": cls._normalize_string_list(
                    keywords_source,
                    default_config.get("keywords", []),
                ),
                "whitelist_phrases": cls._normalize_string_list(
                    whitelist_source,
                    default_config.get("whitelist_phrases", []),
                ),
            }

        lexicon["categories"] = normalized_categories
        lexicon["global_whitelist_phrases"] = cls._normalize_string_list(
            raw_lexicon.get("global_whitelist_phrases"),
            lexicon.get("global_whitelist_phrases", []),
        )
        return lexicon

    @classmethod
    def _compile_phrase_matcher(cls, phrase: str) -> tuple[str, re.Pattern]:
        if cls._is_ascii_keyword(phrase):
            pattern = re.compile(
                rf"(?<![{cls.ASCII_WORD_CHARS}]){re.escape(phrase)}(?![{cls.ASCII_WORD_CHARS}])",
                flags=re.IGNORECASE,
            )
        else:
            pattern = re.compile(re.escape(phrase))
        return phrase, pattern

    @classmethod
    def _find_unwhitelisted_keywords(
        cls,
        text: str,
        matchers: List[tuple[str, re.Pattern]],
        whitelist_spans: List[tuple[int, int]],
    ) -> List[str]:
        hits: List[str] = []

        for keyword, pattern in matchers:
            for match in pattern.finditer(text):
                if not cls._is_span_whitelisted(match.span(), whitelist_spans):
                    hits.append(keyword)
                    break

        return hits

    @staticmethod
    def _collect_match_spans(
        text: str,
        matchers: List[tuple[str, re.Pattern]],
    ) -> List[tuple[int, int]]:
        spans: List[tuple[int, int]] = []
        for _, pattern in matchers:
            spans.extend(match.span() for match in pattern.finditer(text))
        return SentimentAnalyzer._merge_spans(spans)

    @staticmethod
    def _merge_spans(spans: List[tuple[int, int]]) -> List[tuple[int, int]]:
        if not spans:
            return []

        merged: List[List[int]] = []
        for start, end in sorted(spans):
            if not merged or start > merged[-1][1]:
                merged.append([start, end])
            else:
                merged[-1][1] = max(merged[-1][1], end)

        return [(start, end) for start, end in merged]

    @staticmethod
    def _is_span_whitelisted(
        span: tuple[int, int],
        whitelist_spans: List[tuple[int, int]],
    ) -> bool:
        start, end = span
        for white_start, white_end in whitelist_spans:
            if start >= white_start and end <= white_end:
                return True
        return False

    @staticmethod
    def _normalize_string_list(values: Any, default_values: List[str]) -> List[str]:
        source = values if isinstance(values, list) else default_values
        normalized: List[str] = []
        seen = set()

        for item in source:
            text = str(item or "").strip()
            if not text or text in seen:
                continue
            seen.add(text)
            normalized.append(text)

        return normalized

    @staticmethod
    def _is_ascii_keyword(keyword: str) -> bool:
        if not keyword or not keyword.isascii():
            return False
        return any(ch.isalnum() for ch in keyword)

    @classmethod
    def _empty_labels(cls, category_names: List[str]) -> Dict[str, Any]:
        labels: Dict[str, Any] = {"sensitive": False}
        for category in category_names:
            labels[category] = False
        labels["matched_categories"] = []
        labels["matched_keywords"] = []
        labels["matched_by_category"] = {}
        return labels

    @classmethod
    def _neutral_result(cls) -> Dict[str, Any]:
        return {
            "sentiment": SentimentType.NEUTRAL,
            "score": 0.0,
            "labels": cls._empty_labels(cls._get_sensitive_config()["category_names"]),
        }


def analyze_sentiment(content: str, title: str = "") -> Dict[str, Any]:
    """分析内容情绪的便捷函数"""

    return SentimentAnalyzer.analyze(content, title)
