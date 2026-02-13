# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

from django.contrib import admin
from .models import CookieConfig


@admin.register(CookieConfig)
class CookieConfigAdmin(admin.ModelAdmin):
    """Cookie配置管理界面"""
    list_display = ['platform', 'name', 'is_active', 'is_valid', 'last_used_at', 'created_at']
    list_filter = ['platform', 'is_active', 'is_valid', 'created_at']
    search_fields = ['name', 'remark', 'cookies']
    list_editable = ['is_active', 'is_valid']
    ordering = ['-created_at']

    fieldsets = (
        ('基本信息', {
            'fields': ('platform', 'name', 'remark')
        }),
        ('Cookie配置', {
            'fields': ('cookies',)
        }),
        ('状态', {
            'fields': ('is_active', 'is_valid', 'last_used_at', 'last_verified_at')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['created_at', 'updated_at', 'last_used_at', 'last_verified_at']

    def save_model(self, request, obj, form, change):
        """保存时更新最后验证时间"""
        from django.utils import timezone
        if not change:  # 新建时
            obj.last_verified_at = timezone.now()
        super().save_model(request, obj, form, change)
