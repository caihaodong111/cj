# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

"""
Configuration utility for MediaCrawler Django Backend
Provides easy access to configuration values
"""

import os
from pathlib import Path
from typing import Any, Optional, List
from dataclasses import dataclass
from django.conf import settings


@dataclass
class CrawlerConfig:
    """Crawler configuration"""
    platform: str
    login_type: str
    crawler_type: str
    keywords: List[str]
    save_option: str


@dataclass 
class ServerConfig:
    """Server configuration"""
    host: str
    port: int
    debug: bool


@dataclass
class DatabaseConfig:
    """Database configuration"""
    engine: str
    name: str
    user: str
    password: str
    host: str
    port: str


class Config:
    """
    Configuration singleton class
    Provides easy access to all configuration values
    """
    _instance: Optional['Config'] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        # Initialize from Django settings
        self._load_from_settings()

    def _load_from_settings(self):
        """Load configuration from Django settings"""
        base_dir = settings.BASE_DIR

        # Crawler config
        crawler_cfg = settings.CRAWLER_CONFIG
        self.crawler = CrawlerConfig(
            platform=crawler_cfg.get('default_platform', 'xhs'),
            login_type=crawler_cfg.get('default_login_type', 'qrcode'),
            crawler_type=crawler_cfg.get('default_crawler_type', 'search'),
            keywords=crawler_cfg.get('default_keywords', []),
            save_option=crawler_cfg.get('save_data_option', 'db'),
        )

        # Server config
        self.server = ServerConfig(
            host=getattr(settings, 'SERVER_HOST', '0.0.0.0'),
            port=getattr(settings, 'SERVER_PORT', 8000),
            debug=settings.DEBUG,
        )

        # Database config
        db_cfg = settings.DATABASES['default']
        self.database = DatabaseConfig(
            engine=getattr(settings, 'DB_ENGINE', 'sqlite3'),
            name=str(db_cfg.get('NAME', '')),
            user=db_cfg.get('USER', ''),
            password=db_cfg.get('PASSWORD', ''),
            host=db_cfg.get('HOST', 'localhost'),
            port=str(db_cfg.get('PORT', '')),
        )

    # Properties for quick access
    @property
    def secret_key(self) -> str:
        return settings.SECRET_KEY

    @property
    def debug(self) -> bool:
        return settings.DEBUG

    @property
    def allowed_hosts(self) -> List[str]:
        return settings.ALLOWED_HOSTS

    @property
    def data_dir(self) -> Path:
        return settings.DATA_DIR

    @property
    def logs_dir(self) -> Path:
        return settings.BASE_DIR / "logs"

    # Methods for dynamic access
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key"""
        return os.environ.get(key, default)

    def get_bool(self, key: str, default: bool = False) -> bool:
        """Get boolean configuration value"""
        value = os.environ.get(key, str(default))
        return value.lower() in ('true', '1', 'yes', 'on')

    def get_int(self, key: str, default: int = 0) -> int:
        """Get integer configuration value"""
        try:
            return int(os.environ.get(key, str(default)))
        except (ValueError, TypeError):
            return default

    def get_list(self, key: str, default: List = None, separator: str = ',') -> List[str]:
        """Get list configuration value"""
        if default is None:
            default = []
        value = os.environ.get(key, '')
        return [item.strip() for item in value.split(separator)] if value else default

    def reload(self):
        """Reload configuration from environment"""
        self._load_from_settings()


# Global config instance
config = Config()


def get_config() -> Config:
    """Get the global configuration instance"""
    return config


# Convenience functions for quick access
def get_env(key: str, default: Any = None) -> Any:
    """Get environment variable"""
    return os.environ.get(key, default)


def get_env_bool(key: str, default: bool = False) -> bool:
    """Get boolean environment variable"""
    value = os.environ.get(key, str(default))
    return value.lower() in ('true', '1', 'yes', 'on')


def get_env_int(key: str, default: int = 0) -> int:
    """Get integer environment variable"""
    try:
        return int(os.environ.get(key, str(default)))
    except (ValueError, TypeError):
        return default


def get_env_list(key: str, default: List = None, separator: str = ',') -> List[str]:
    """Get list environment variable"""
    if default is None:
        default = []
    value = os.environ.get(key, '')
    return [item.strip() for item in value.split(separator)] if value else default
