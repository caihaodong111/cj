# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

"""
Django models for MediaCrawler - converted from SQLAlchemy models
"""

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class BaseModel(models.Model):
    """Base model with common fields"""
    add_ts = models.BigIntegerField(null=True, blank=True, verbose_name="Add timestamp")
    last_modify_ts = models.BigIntegerField(null=True, blank=True, verbose_name="Last modify timestamp")

    class Meta:
        abstract = True


# ============== Bilibili Models ==============

class BilibiliVideo(BaseModel):
    """Bilibili video model"""
    video_id = models.BigIntegerField(unique=True, db_index=True, verbose_name="Video ID")
    video_url = models.TextField(verbose_name="Video URL")
    user_id = models.BigIntegerField(db_index=True, null=True, blank=True)
    nickname = models.TextField(null=True, blank=True)
    avatar = models.TextField(null=True, blank=True)
    liked_count = models.IntegerField(null=True, blank=True)
    video_type = models.TextField(null=True, blank=True)
    title = models.TextField(null=True, blank=True)
    desc = models.TextField(null=True, blank=True)
    create_time = models.BigIntegerField(db_index=True, null=True, blank=True)
    disliked_count = models.TextField(null=True, blank=True)
    video_play_count = models.TextField(null=True, blank=True)
    video_favorite_count = models.TextField(null=True, blank=True)
    video_share_count = models.TextField(null=True, blank=True)
    video_coin_count = models.TextField(null=True, blank=True)
    video_danmaku = models.TextField(null=True, blank=True)
    video_comment = models.TextField(null=True, blank=True)
    video_cover_url = models.TextField(null=True, blank=True)
    source_keyword = models.TextField(default='', blank=True, verbose_name="Source keyword")

    class Meta:
        db_table = 'bilibili_video'
        verbose_name = "Bilibili Video"
        verbose_name_plural = "Bilibili Videos"


class BilibiliVideoComment(BaseModel):
    """Bilibili video comment model"""
    user_id = models.CharField(max_length=255, null=True, blank=True)
    nickname = models.TextField(null=True, blank=True)
    sex = models.TextField(null=True, blank=True)
    sign = models.TextField(null=True, blank=True)
    avatar = models.TextField(null=True, blank=True)
    comment_id = models.BigIntegerField(db_index=True, verbose_name="Comment ID")
    video_id = models.BigIntegerField(db_index=True, verbose_name="Video ID")
    content = models.TextField(null=True, blank=True)
    create_time = models.BigIntegerField(null=True, blank=True)
    sub_comment_count = models.TextField(null=True, blank=True)
    parent_comment_id = models.CharField(max_length=255, null=True, blank=True)
    like_count = models.TextField(default='0', blank=True)

    class Meta:
        db_table = 'bilibili_video_comment'
        verbose_name = "Bilibili Video Comment"
        verbose_name_plural = "Bilibili Video Comments"


class BilibiliUpInfo(BaseModel):
    """Bilibili UP (creator) info model"""
    user_id = models.BigIntegerField(db_index=True, verbose_name="User ID")
    nickname = models.TextField(null=True, blank=True)
    sex = models.TextField(null=True, blank=True)
    sign = models.TextField(null=True, blank=True)
    avatar = models.TextField(null=True, blank=True)
    total_fans = models.IntegerField(null=True, blank=True)
    total_liked = models.IntegerField(null=True, blank=True)
    user_rank = models.IntegerField(null=True, blank=True)
    is_official = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'bilibili_up_info'
        verbose_name = "Bilibili UP Info"
        verbose_name_plural = "Bilibili UP Info"


class BilibiliContactInfo(BaseModel):
    """Bilibili contact info model"""
    up_id = models.BigIntegerField(db_index=True, verbose_name="UP ID")
    fan_id = models.BigIntegerField(db_index=True, verbose_name="Fan ID")
    up_name = models.TextField(null=True, blank=True)
    fan_name = models.TextField(null=True, blank=True)
    up_sign = models.TextField(null=True, blank=True)
    fan_sign = models.TextField(null=True, blank=True)
    up_avatar = models.TextField(null=True, blank=True)
    fan_avatar = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'bilibili_contact_info'
        verbose_name = "Bilibili Contact Info"
        verbose_name_plural = "Bilibili Contact Info"


class BilibiliUpDynamic(BaseModel):
    """Bilibili UP dynamic model"""
    dynamic_id = models.BigIntegerField(db_index=True, verbose_name="Dynamic ID")
    user_id = models.CharField(max_length=255, null=True, blank=True)
    user_name = models.TextField(null=True, blank=True)
    text = models.TextField(null=True, blank=True)
    type = models.TextField(null=True, blank=True)
    pub_ts = models.BigIntegerField(null=True, blank=True)
    total_comments = models.IntegerField(null=True, blank=True)
    total_forwards = models.IntegerField(null=True, blank=True)
    total_liked = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'bilibili_up_dynamic'
        verbose_name = "Bilibili UP Dynamic"
        verbose_name_plural = "Bilibili UP Dynamics"


# ============== Douyin Models ==============

class DouyinAweme(BaseModel):
    """Douyin aweme (video) model"""
    user_id = models.CharField(max_length=255, null=True, blank=True)
    sec_uid = models.CharField(max_length=255, null=True, blank=True)
    short_user_id = models.CharField(max_length=255, null=True, blank=True)
    user_unique_id = models.CharField(max_length=255, null=True, blank=True)
    nickname = models.TextField(null=True, blank=True)
    avatar = models.TextField(null=True, blank=True)
    user_signature = models.TextField(null=True, blank=True)
    ip_location = models.TextField(null=True, blank=True)
    aweme_id = models.BigIntegerField(db_index=True, verbose_name="Aweme ID")
    aweme_type = models.TextField(null=True, blank=True)
    title = models.TextField(null=True, blank=True)
    desc = models.TextField(null=True, blank=True)
    create_time = models.BigIntegerField(db_index=True, null=True, blank=True)
    liked_count = models.TextField(null=True, blank=True)
    comment_count = models.TextField(null=True, blank=True)
    share_count = models.TextField(null=True, blank=True)
    collected_count = models.TextField(null=True, blank=True)
    aweme_url = models.TextField(null=True, blank=True)
    cover_url = models.TextField(null=True, blank=True)
    video_download_url = models.TextField(null=True, blank=True)
    music_download_url = models.TextField(null=True, blank=True)
    note_download_url = models.TextField(null=True, blank=True)
    source_keyword = models.TextField(default='', blank=True, verbose_name="Source keyword")

    class Meta:
        db_table = 'douyin_aweme'
        verbose_name = "Douyin Aweme"
        verbose_name_plural = "Douyin Awemes"


class DouyinAwemeComment(BaseModel):
    """Douyin aweme comment model"""
    user_id = models.CharField(max_length=255, null=True, blank=True)
    sec_uid = models.CharField(max_length=255, null=True, blank=True)
    short_user_id = models.CharField(max_length=255, null=True, blank=True)
    user_unique_id = models.CharField(max_length=255, null=True, blank=True)
    nickname = models.TextField(null=True, blank=True)
    avatar = models.TextField(null=True, blank=True)
    user_signature = models.TextField(null=True, blank=True)
    ip_location = models.TextField(null=True, blank=True)
    comment_id = models.BigIntegerField(db_index=True, verbose_name="Comment ID")
    aweme_id = models.BigIntegerField(db_index=True, verbose_name="Aweme ID")
    content = models.TextField(null=True, blank=True)
    create_time = models.BigIntegerField(null=True, blank=True)
    sub_comment_count = models.TextField(null=True, blank=True)
    parent_comment_id = models.CharField(max_length=255, null=True, blank=True)
    like_count = models.TextField(default='0', blank=True)
    pictures = models.TextField(default='', blank=True)

    class Meta:
        db_table = 'douyin_aweme_comment'
        verbose_name = "Douyin Aweme Comment"
        verbose_name_plural = "Douyin Aweme Comments"


class DyCreator(BaseModel):
    """Douyin creator model"""
    user_id = models.CharField(max_length=255, null=True, blank=True)
    nickname = models.TextField(null=True, blank=True)
    avatar = models.TextField(null=True, blank=True)
    ip_location = models.TextField(null=True, blank=True)
    desc = models.TextField(null=True, blank=True)
    gender = models.TextField(null=True, blank=True)
    follows = models.TextField(null=True, blank=True)
    fans = models.TextField(null=True, blank=True)
    interaction = models.TextField(null=True, blank=True)
    videos_count = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'dy_creator'
        verbose_name = "Douyin Creator"
        verbose_name_plural = "Douyin Creators"


# ============== Kuaishou Models ==============

class KuaishouVideo(BaseModel):
    """Kuaishou video model"""
    user_id = models.CharField(max_length=64, null=True, blank=True)
    nickname = models.TextField(null=True, blank=True)
    avatar = models.TextField(null=True, blank=True)
    video_id = models.CharField(max_length=255, db_index=True, verbose_name="Video ID")
    video_type = models.TextField(null=True, blank=True)
    title = models.TextField(null=True, blank=True)
    desc = models.TextField(null=True, blank=True)
    create_time = models.BigIntegerField(db_index=True, null=True, blank=True)
    liked_count = models.TextField(null=True, blank=True)
    viewd_count = models.TextField(null=True, blank=True)
    video_url = models.TextField(null=True, blank=True)
    video_cover_url = models.TextField(null=True, blank=True)
    video_play_url = models.TextField(null=True, blank=True)
    source_keyword = models.TextField(default='', blank=True, verbose_name="Source keyword")

    class Meta:
        db_table = 'kuaishou_video'
        verbose_name = "Kuaishou Video"
        verbose_name_plural = "Kuaishou Videos"


class KuaishouVideoComment(BaseModel):
    """Kuaishou video comment model"""
    user_id = models.TextField(null=True, blank=True)
    nickname = models.TextField(null=True, blank=True)
    avatar = models.TextField(null=True, blank=True)
    comment_id = models.BigIntegerField(db_index=True, verbose_name="Comment ID")
    video_id = models.CharField(max_length=255, db_index=True, verbose_name="Video ID")
    content = models.TextField(null=True, blank=True)
    create_time = models.BigIntegerField(null=True, blank=True)
    sub_comment_count = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'kuaishou_video_comment'
        verbose_name = "Kuaishou Video Comment"
        verbose_name_plural = "Kuaishou Video Comments"


# ============== Weibo Models ==============

class WeiboNote(BaseModel):
    """Weibo note model"""
    user_id = models.CharField(max_length=255, null=True, blank=True)
    nickname = models.TextField(null=True, blank=True)
    avatar = models.TextField(null=True, blank=True)
    gender = models.TextField(null=True, blank=True)
    profile_url = models.TextField(null=True, blank=True)
    ip_location = models.TextField(default='', blank=True)
    note_id = models.BigIntegerField(db_index=True, verbose_name="Note ID")
    content = models.TextField(null=True, blank=True)
    create_time = models.BigIntegerField(db_index=True, null=True, blank=True)
    create_date_time = models.CharField(max_length=255, db_index=True, null=True, blank=True)
    liked_count = models.TextField(null=True, blank=True)
    comments_count = models.TextField(null=True, blank=True)
    shared_count = models.TextField(null=True, blank=True)
    note_url = models.TextField(null=True, blank=True)
    source_keyword = models.TextField(default='', blank=True, verbose_name="Source keyword")

    class Meta:
        db_table = 'weibo_note'
        verbose_name = "Weibo Note"
        verbose_name_plural = "Weibo Notes"


class WeiboNoteComment(BaseModel):
    """Weibo note comment model"""
    user_id = models.CharField(max_length=255, null=True, blank=True)
    nickname = models.TextField(null=True, blank=True)
    avatar = models.TextField(null=True, blank=True)
    gender = models.TextField(null=True, blank=True)
    profile_url = models.TextField(null=True, blank=True)
    ip_location = models.TextField(default='', blank=True)
    comment_id = models.BigIntegerField(db_index=True, verbose_name="Comment ID")
    note_id = models.BigIntegerField(db_index=True, verbose_name="Note ID")
    content = models.TextField(null=True, blank=True)
    create_time = models.BigIntegerField(null=True, blank=True)
    create_date_time = models.CharField(max_length=255, db_index=True, null=True, blank=True)
    comment_like_count = models.TextField(null=True, blank=True)
    sub_comment_count = models.TextField(null=True, blank=True)
    parent_comment_id = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'weibo_note_comment'
        verbose_name = "Weibo Note Comment"
        verbose_name_plural = "Weibo Note Comments"


class WeiboCreator(BaseModel):
    """Weibo creator model"""
    user_id = models.CharField(max_length=255, null=True, blank=True)
    nickname = models.TextField(null=True, blank=True)
    avatar = models.TextField(null=True, blank=True)
    ip_location = models.TextField(null=True, blank=True)
    desc = models.TextField(null=True, blank=True)
    gender = models.TextField(null=True, blank=True)
    follows = models.TextField(null=True, blank=True)
    fans = models.TextField(null=True, blank=True)
    tag_list = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'weibo_creator'
        verbose_name = "Weibo Creator"
        verbose_name_plural = "Weibo Creators"


# ============== Xiaohongshu Models ==============

class XhsCreator(BaseModel):
    """Xiaohongshu creator model"""
    user_id = models.CharField(max_length=255, null=True, blank=True)
    nickname = models.TextField(null=True, blank=True)
    avatar = models.TextField(null=True, blank=True)
    ip_location = models.TextField(null=True, blank=True)
    desc = models.TextField(null=True, blank=True)
    gender = models.TextField(null=True, blank=True)
    follows = models.TextField(null=True, blank=True)
    fans = models.TextField(null=True, blank=True)
    interaction = models.TextField(null=True, blank=True)
    tag_list = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'xhs_creator'
        verbose_name = "Xiaohongshu Creator"
        verbose_name_plural = "Xiaohongshu Creators"


class XhsNote(BaseModel):
    """Xiaohongshu note model"""
    user_id = models.CharField(max_length=255, null=True, blank=True)
    nickname = models.TextField(null=True, blank=True)
    avatar = models.TextField(null=True, blank=True)
    ip_location = models.TextField(null=True, blank=True)
    note_id = models.CharField(max_length=255, db_index=True, verbose_name="Note ID")
    type = models.TextField(null=True, blank=True)
    title = models.TextField(null=True, blank=True)
    desc = models.TextField(null=True, blank=True)
    video_url = models.TextField(null=True, blank=True)
    time = models.BigIntegerField(db_index=True, null=True, blank=True)
    last_update_time = models.BigIntegerField(null=True, blank=True)
    liked_count = models.TextField(null=True, blank=True)
    collected_count = models.TextField(null=True, blank=True)
    comment_count = models.TextField(null=True, blank=True)
    share_count = models.TextField(null=True, blank=True)
    image_list = models.TextField(null=True, blank=True)
    tag_list = models.TextField(null=True, blank=True)
    note_url = models.TextField(null=True, blank=True)
    source_keyword = models.TextField(default='', blank=True, verbose_name="Source keyword")
    xsec_token = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'xhs_note'
        verbose_name = "Xiaohongshu Note"
        verbose_name_plural = "Xiaohongshu Notes"


class XhsNoteComment(BaseModel):
    """Xiaohongshu note comment model"""
    user_id = models.CharField(max_length=255, null=True, blank=True)
    nickname = models.TextField(null=True, blank=True)
    avatar = models.TextField(null=True, blank=True)
    ip_location = models.TextField(null=True, blank=True)
    comment_id = models.CharField(max_length=255, db_index=True, verbose_name="Comment ID")
    create_time = models.BigIntegerField(db_index=True, null=True, blank=True)
    note_id = models.CharField(max_length=255, null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    sub_comment_count = models.IntegerField(null=True, blank=True)
    pictures = models.TextField(null=True, blank=True)
    parent_comment_id = models.CharField(max_length=255, null=True, blank=True)
    like_count = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'xhs_note_comment'
        verbose_name = "Xiaohongshu Note Comment"
        verbose_name_plural = "Xiaohongshu Note Comments"


# ============== Tieba Models ==============

class TiebaNote(BaseModel):
    """Tieba note model"""
    note_id = models.CharField(max_length=644, db_index=True, verbose_name="Note ID")
    title = models.TextField(null=True, blank=True)
    desc = models.TextField(null=True, blank=True)
    note_url = models.TextField(null=True, blank=True)
    publish_time = models.CharField(max_length=255, db_index=True, null=True, blank=True)
    user_link = models.TextField(default='', blank=True)
    user_nickname = models.TextField(default='', blank=True)
    user_avatar = models.TextField(default='', blank=True)
    tieba_id = models.CharField(max_length=255, default='', blank=True)
    tieba_name = models.TextField(null=True, blank=True)
    tieba_link = models.TextField(null=True, blank=True)
    total_replay_num = models.IntegerField(default=0)
    total_replay_page = models.IntegerField(default=0)
    ip_location = models.TextField(default='', blank=True)
    source_keyword = models.TextField(default='', blank=True, verbose_name="Source keyword")

    class Meta:
        db_table = 'tieba_note'
        verbose_name = "Tieba Note"
        verbose_name_plural = "Tieba Notes"


class TiebaComment(BaseModel):
    """Tieba comment model"""
    comment_id = models.CharField(max_length=255, db_index=True, verbose_name="Comment ID")
    parent_comment_id = models.CharField(max_length=255, default='', blank=True)
    content = models.TextField(null=True, blank=True)
    user_link = models.TextField(default='', blank=True)
    user_nickname = models.TextField(default='', blank=True)
    user_avatar = models.TextField(default='', blank=True)
    tieba_id = models.CharField(max_length=255, default='', blank=True)
    tieba_name = models.TextField(null=True, blank=True)
    tieba_link = models.TextField(null=True, blank=True)
    publish_time = models.CharField(max_length=255, db_index=True, null=True, blank=True)
    ip_location = models.TextField(default='', blank=True)
    sub_comment_count = models.IntegerField(default=0)
    note_id = models.CharField(max_length=255, db_index=True, verbose_name="Note ID")
    note_url = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'tieba_comment'
        verbose_name = "Tieba Comment"
        verbose_name_plural = "Tieba Comments"


class TiebaCreator(BaseModel):
    """Tieba creator model"""
    user_id = models.CharField(max_length=64, null=True, blank=True)
    user_name = models.TextField(null=True, blank=True)
    nickname = models.TextField(null=True, blank=True)
    avatar = models.TextField(null=True, blank=True)
    ip_location = models.TextField(null=True, blank=True)
    gender = models.TextField(null=True, blank=True)
    follows = models.TextField(null=True, blank=True)
    fans = models.TextField(null=True, blank=True)
    registration_duration = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'tieba_creator'
        verbose_name = "Tieba Creator"
        verbose_name_plural = "Tieba Creators"


# ============== Monitor Feed Models ==============

class MonitorFeed(BaseModel):
    """Monitor feed for real-time data display from all platforms"""
    platform = models.CharField(max_length=20, db_index=True, verbose_name="Platform code")
    platform_name = models.CharField(max_length=50, verbose_name="Platform name")
    content_id = models.CharField(max_length=255, db_index=True, verbose_name="Original content ID")
    content = models.TextField(verbose_name="Content text")
    author = models.TextField(null=True, blank=True, verbose_name="Author nickname")
    url = models.TextField(null=True, blank=True, verbose_name="Content URL")
    created_at = models.BigIntegerField(db_index=True, verbose_name="Original publish time")
    source_keyword = models.TextField(default='', blank=True, verbose_name="Source keyword")
    extra_data = models.JSONField(null=True, blank=True, verbose_name="Extra data")
    # 情绪分析字段
    sentiment = models.CharField(
        max_length=20,
        default='neutral',
        db_index=True,
        verbose_name="Sentiment type (positive/negative/neutral/sensitive)"
    )
    sentiment_score = models.FloatField(
        null=True,
        blank=True,
        verbose_name="Sentiment score (-1 to 1)"
    )
    sentiment_labels = models.JSONField(
        null=True,
        blank=True,
        verbose_name="Sentiment analysis labels"
    )
    is_sensitive = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Is sensitive content"
    )

    class Meta:
        db_table = 'monitor_feed'
        verbose_name = "Monitor Feed"
        verbose_name_plural = "Monitor Feeds"
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['platform', '-created_at']),
            models.Index(fields=['sentiment', '-created_at']),
        ]


# ============== Zhihu Models ==============

class ZhihuContent(BaseModel):
    """Zhihu content model"""
    content_id = models.CharField(max_length=64, db_index=True, verbose_name="Content ID")
    content_type = models.TextField(null=True, blank=True)
    content_text = models.TextField(null=True, blank=True)
    content_url = models.TextField(null=True, blank=True)
    question_id = models.CharField(max_length=255, null=True, blank=True)
    title = models.TextField(null=True, blank=True)
    desc = models.TextField(null=True, blank=True)
    created_time = models.CharField(max_length=32, db_index=True, null=True, blank=True)
    updated_time = models.TextField(null=True, blank=True)
    voteup_count = models.IntegerField(default=0)
    comment_count = models.IntegerField(default=0)
    source_keyword = models.TextField(null=True, blank=True)
    user_id = models.CharField(max_length=255, null=True, blank=True)
    user_link = models.TextField(null=True, blank=True)
    user_nickname = models.TextField(null=True, blank=True)
    user_avatar = models.TextField(null=True, blank=True)
    user_url_token = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'zhihu_content'
        verbose_name = "Zhihu Content"
        verbose_name_plural = "Zhihu Contents"


class ZhihuComment(BaseModel):
    """Zhihu comment model"""
    comment_id = models.CharField(max_length=64, db_index=True, verbose_name="Comment ID")
    parent_comment_id = models.CharField(max_length=64, null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    publish_time = models.CharField(max_length=32, db_index=True, null=True, blank=True)
    ip_location = models.TextField(null=True, blank=True)
    sub_comment_count = models.IntegerField(default=0)
    like_count = models.IntegerField(default=0)
    dislike_count = models.IntegerField(default=0)
    content_id = models.CharField(max_length=64, db_index=True, verbose_name="Content ID")
    content_type = models.TextField(null=True, blank=True)
    user_id = models.CharField(max_length=64, null=True, blank=True)
    user_link = models.TextField(null=True, blank=True)
    user_nickname = models.TextField(null=True, blank=True)
    user_avatar = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'zhihu_comment'
        verbose_name = "Zhihu Comment"
        verbose_name_plural = "Zhihu Comments"


class ZhihuCreator(BaseModel):
    """Zhihu creator model"""
    user_id = models.CharField(max_length=64, unique=True, db_index=True, verbose_name="User ID")
    user_link = models.TextField(null=True, blank=True)
    user_nickname = models.TextField(null=True, blank=True)
    user_avatar = models.TextField(null=True, blank=True)
    url_token = models.TextField(null=True, blank=True)
    gender = models.TextField(null=True, blank=True)
    ip_location = models.TextField(null=True, blank=True)
    follows = models.IntegerField(default=0)
    fans = models.IntegerField(default=0)
    anwser_count = models.IntegerField(default=0)
    video_count = models.IntegerField(default=0)
    question_count = models.IntegerField(default=0)
    article_count = models.IntegerField(default=0)
    column_count = models.IntegerField(default=0)
    get_voteup_count = models.IntegerField(default=0)

    class Meta:
        db_table = 'zhihu_creator'
        verbose_name = "Zhihu Creator"
        verbose_name_plural = "Zhihu Creators"
