# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

"""
URL configuration for MediaCrawler Backend project
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse

from api.views import (
    health_check,
    check_environment,
    get_platforms,
    get_config_options,
    list_data_files,
    get_file_content,
    download_file,
    get_data_stats,
    get_monitor_feed,
    get_sensitive_feed,
    get_all_feed,
    get_platform_sentiment_stats,
    CrawlerView,
    # Cookie Management
    list_cookies,
    get_cookie,
    create_cookie,
    update_cookie,
    delete_cookie,
    toggle_cookie_status,
    get_active_cookie,
)

urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),

    # API: Health & Config
    path("api/health", health_check, name="health_check"),
    path("api/env/check", check_environment, name="check_environment"),
    path("api/config/platforms", get_platforms, name="get_platforms"),
    path("api/config/options", get_config_options, name="get_config_options"),

    # API: Crawler Control
    path("api/crawler/<str:action>", CrawlerView.as_view(), name="crawler_action"),

    # API: Data Management
    path("api/data/files", list_data_files, name="list_data_files"),
    path("api/data/stats", get_data_stats, name="get_data_stats"),
    path("api/data/files/<path:file_path>", get_file_content, name="get_file_content"),
    path("api/data/download/<path:file_path>", download_file, name="download_file"),
    path("api/monitor/feed", get_monitor_feed, name="get_monitor_feed"),
    path("api/monitor/feed/sensitive", get_sensitive_feed, name="get_sensitive_feed"),
    path("api/monitor/feed/all", get_all_feed, name="get_all_feed"),
    path("api/monitor/platform-sentiment-stats", get_platform_sentiment_stats, name="get_platform_sentiment_stats"),

    # API: Cookie Management
    path("api/cookies", list_cookies, name="list_cookies"),
    path("api/cookies/active", get_active_cookie, name="get_active_cookie"),
    path("api/cookies/<int:cookie_id>", get_cookie, name="get_cookie"),
    path("api/cookies/create", create_cookie, name="create_cookie"),
    path("api/cookies/<int:cookie_id>/update", update_cookie, name="update_cookie"),
    path("api/cookies/<int:cookie_id>/delete", delete_cookie, name="delete_cookie"),
    path("api/cookies/<int:cookie_id>/toggle", toggle_cookie_status, name="toggle_cookie_status"),

    # Root endpoint
    path(
        "",
        lambda r: JsonResponse(
            {
                "message": "MediaCrawler Backend API",
                "version": "1.0.0",
                "docs": "/api/docs",
                "admin": "/admin/",
                "health": "/api/health",
            }
        ),
    ),
]

# Serve static files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
