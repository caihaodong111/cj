# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

"""
情绪分析服务
用于分析内容的情绪倾向（积极、消极、中性、敏感）
"""

import re
from typing import Dict, List, Tuple


class SentimentType:
    """情绪类型枚举"""
    POSITIVE = 'positive'    # 积极
    NEGATIVE = 'negative'    # 消极
    NEUTRAL = 'neutral'      # 中性
    SENSITIVE = 'sensitive'  # 敏感（涉黄、涉政等）


class SentimentAnalyzer:
    """基于规则的情绪分析器"""

    # 敏感关键词（涉黄、涉政、违法等）
    SENSITIVE_KEYWORDS = {
        'adult': [
            '色情', '淫秽', '裸体', '性交', '做爱', '约炮', '卖淫',
            '黄色', '三级片', 'AV', 'Porn', '性服务', '援交',
            '色播', '裸聊', '情趣', 'SM', 'BDSM',
        ],
        'political': [
            '反党', '反政府', '反国家', '颠覆', '暴动', '造反',
            '法轮', '邪教', '分裂', '恐怖', '恐怖主义',
            '反共', '反华', '反体制', '六四', '天安门',
        ],
        'violence': [
            '杀人', '杀戮', '暴力', '血腥', '残忍', '虐待',
            '自杀', '自残', '炸弹', '爆炸', '投毒',
            '枪支', '管制刀具', '毒药', '毒品',
        ],
        'illegal': [
            '赌博', '博彩', '赌场', '彩票', '六合彩',
            '诈骗', '传销', '洗钱', '高利贷', '套路贷',
            '假币', '假发票', '走私', '贩卖',
        ],
    }

    # 积极关键词
    POSITIVE_KEYWORDS = [
        '开心', '快乐', '幸福', '美好', '优秀', '棒', '赞',
        '喜欢', '爱', '感谢', '支持', '加油', '努力',
        '成功', '胜利', '棒棒', '厉害', '太好了',
        '😊', '😄', '👍', '💪', '❤️', '🎉',
    ]

    # 消极关键词
    NEGATIVE_KEYWORDS = [
        '难过', '伤心', '痛苦', '失望', '糟糕', '差',
        '讨厌', '恨', '愤怒', '生气', '烦', '痛苦',
        '失败', '完蛋', '垃圾', '废物', '没用',
        '😭', '😢', '😡', '😠', '💔',
    ]

    @classmethod
    def analyze(cls, content: str, title: str = '') -> Dict:
        """
        分析内容的情绪

        Args:
            content: 内容文本
            title: 标题文本（可选）

        Returns:
            {
                'sentiment': 'positive/negative/neutral/sensitive',
                'score': float,
                'labels': {
                    'sensitive': bool,
                    'adult': bool,
                    'political': bool,
                    'violence': bool,
                    'illegal': bool
                }
            }
        """
        if not content and not title:
            return cls._neutral_result()

        # 合并标题和内容进行分析
        text = f"{title} {content}".lower()

        # 1. 优先检测敏感内容
        sensitive_result = cls._check_sensitive(text)
        if sensitive_result['is_sensitive']:
            return {
                'sentiment': SentimentType.SENSITIVE,
                'score': -1.0,
                'labels': sensitive_result['labels']
            }

        # 2. 检测积极/消极倾向
        positive_count = sum(1 for keyword in cls.POSITIVE_KEYWORDS if keyword in text)
        negative_count = sum(1 for keyword in cls.NEGATIVE_KEYWORDS if keyword in text)

        # 计算情绪分数 (-1 到 1)
        total_count = positive_count + negative_count
        if total_count == 0:
            score = 0.0
        else:
            score = (positive_count - negative_count) / total_count

        # 确定情绪类型
        if score > 0.3:
            sentiment = SentimentType.POSITIVE
        elif score < -0.3:
            sentiment = SentimentType.NEGATIVE
        else:
            sentiment = SentimentType.NEUTRAL

        return {
            'sentiment': sentiment,
            'score': score,
            'labels': {
                'sensitive': False,
                'adult': False,
                'political': False,
                'violence': False,
                'illegal': False
            }
        }

    @classmethod
    def _check_sensitive(cls, text: str) -> Dict:
        """
        检测敏感内容

        Returns:
            {
                'is_sensitive': bool,
                'labels': {
                    'adult': bool,
                    'political': bool,
                    'violence': bool,
                    'illegal': bool
                }
            }
        """
        labels = {
            'adult': False,
            'political': False,
            'violence': False,
            'illegal': False
        }

        for category, keywords in cls.SENSITIVE_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text:
                    labels[category] = True
                    break
            if labels[category]:
                break

        is_sensitive = any(labels.values())

        return {
            'is_sensitive': is_sensitive,
            'labels': labels
        }

    @classmethod
    def _neutral_result(cls) -> Dict:
        """返回中性结果"""
        return {
            'sentiment': SentimentType.NEUTRAL,
            'score': 0.0,
            'labels': {
                'sensitive': False,
                'adult': False,
                'political': False,
                'violence': False,
                'illegal': False
            }
        }


# 便捷函数
def analyze_sentiment(content: str, title: str = '') -> Dict:
    """分析内容情绪的便捷函数"""
    return SentimentAnalyzer.analyze(content, title)
