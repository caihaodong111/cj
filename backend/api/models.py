# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

from django.db import models


class AIUsageRecord(models.Model):
    """AI使用记录模型，用于记录深度分析功能的AI调用"""

    PLATFORM_CHOICES = [
        ('all', '所有平台'),
        ('xhs', '小红书'),
        ('dy', '抖音'),
        ('ks', '快手'),
        ('bili', '哔哩哔哩'),
        ('wb', '微博'),
        ('tieba', '百度贴吧'),
        ('zhihu', '知乎'),
    ]

    id = models.AutoField(primary_key=True)
    keyword = models.CharField(
        max_length=200,
        verbose_name='分析关键词',
        db_index=True
    )
    platform = models.CharField(
        max_length=20,
        choices=PLATFORM_CHOICES,
        default='all',
        verbose_name='平台',
        db_index=True
    )
    time_range = models.CharField(
        max_length=50,
        verbose_name='时间范围'
    )
    result_keywords = models.JSONField(
        verbose_name='返回的关键词列表',
        null=True,
        blank=True
    )
    is_success = models.BooleanField(
        default=True,
        verbose_name='是否成功'
    )
    error_message = models.TextField(
        blank=True,
        default='',
        verbose_name='错误信息'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间',
        db_index=True
    )

    class Meta:
        db_table = 'ai_usage_record'
        verbose_name = 'AI使用记录'
        verbose_name_plural = 'AI使用记录'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.keyword} - {self.get_platform_display()}'


class CookieConfig(models.Model):
    """Cookie配置模型，用于存储各平台的登录Cookie"""

    PLATFORM_CHOICES = [
        ('xhs', '小红书'),
        ('dy', '抖音'),
        ('ks', '快手'),
        ('bili', '哔哩哔哩'),
        ('wb', '微博'),
        ('tieba', '百度贴吧'),
        ('zhihu', '知乎'),
    ]

    id = models.AutoField(primary_key=True)
    platform = models.CharField(
        max_length=20,
        choices=PLATFORM_CHOICES,
        verbose_name='平台',
        db_index=True
    )
    name = models.CharField(
        max_length=100,
        default='默认配置',
        verbose_name='配置名称'
    )
    cookies = models.TextField(
        verbose_name='Cookie字符串',
        help_text='格式: key1=value1;key2=value2'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='是否启用'
    )
    is_valid = models.BooleanField(
        default=True,
        verbose_name='是否有效'
    )
    last_used_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='最后使用时间'
    )
    last_verified_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='最后验证时间'
    )
    remark = models.TextField(
        blank=True,
        default='',
        verbose_name='备注'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间'
    )

    class Meta:
        db_table = 'cookie_config'
        verbose_name = 'Cookie配置'
        verbose_name_plural = 'Cookie配置'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.get_platform_display()} - {self.name}'

    @classmethod
    def get_active_cookie(cls, platform: str) -> str:
        """获取指定平台的激活Cookie"""
        try:
            config = cls.objects.filter(
                platform=platform,
                is_active=True,
                is_valid=True
            ).first()
            return config.cookies if config else ""
        except Exception:
            return ""
