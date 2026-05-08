from datetime import date, datetime, time as dt_time
from zoneinfo import ZoneInfo

from django.db import migrations, models
from django.db.models import Count


CHINA_TIMEZONE = ZoneInfo("Asia/Shanghai")
_DATETIME_FORMATS = (
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%d %H:%M",
    "%Y/%m/%d %H:%M:%S",
    "%Y/%m/%d %H:%M",
)
_DATE_FORMATS = (
    "%Y-%m-%d",
    "%Y/%m/%d",
)
_BATCH_SIZE = 500


def _ensure_datetime(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=CHINA_TIMEZONE)
    return value.astimezone(CHINA_TIMEZONE)


def _numeric_timestamp_to_millis(value: int) -> int:
    abs_value = abs(value)
    if abs_value >= 10**11:
        return value
    if abs_value >= 10**9:
        return value * 1000
    return value


def _coerce_timestamp_ms(value):
    if value is None:
        return None

    if isinstance(value, datetime):
        return int(_ensure_datetime(value).timestamp() * 1000)

    if isinstance(value, date):
        return int(datetime.combine(value, dt_time.min, tzinfo=CHINA_TIMEZONE).timestamp() * 1000)

    if isinstance(value, (int, float)):
        return _numeric_timestamp_to_millis(int(value))

    raw = str(value).strip()
    if not raw:
        return None

    if raw[0] in "+-" and raw[1:].isdigit():
        return _numeric_timestamp_to_millis(int(raw))

    if raw.isdigit():
        return _numeric_timestamp_to_millis(int(raw))

    iso_candidate = raw
    if iso_candidate.endswith("Z"):
        iso_candidate = f"{iso_candidate[:-1]}+00:00"

    try:
        parsed = datetime.fromisoformat(iso_candidate)
    except ValueError:
        parsed = None

    if parsed is None:
        for fmt in _DATETIME_FORMATS:
            try:
                parsed = datetime.strptime(raw, fmt)
                break
            except ValueError:
                continue

    if parsed is None:
        for fmt in _DATE_FORMATS:
            try:
                parsed_date = datetime.strptime(raw, fmt).date()
                parsed = datetime.combine(parsed_date, dt_time.min)
                break
            except ValueError:
                continue

    if parsed is None:
        return None

    return int(_ensure_datetime(parsed).timestamp() * 1000)


def _backfill_normalized_timestamps(apps, schema_editor):
    TiebaNote = apps.get_model("media_platform", "TiebaNote")
    ZhihuContent = apps.get_model("media_platform", "ZhihuContent")
    MonitorFeed = apps.get_model("media_platform", "MonitorFeed")

    tieba_time_map = {}
    tieba_batch = []
    for note in TiebaNote.objects.only("id", "note_id", "publish_time").iterator(chunk_size=_BATCH_SIZE):
        note.publish_time_ms = _coerce_timestamp_ms(note.publish_time)
        tieba_time_map[str(note.note_id)] = note.publish_time_ms
        tieba_batch.append(note)
        if len(tieba_batch) >= _BATCH_SIZE:
            TiebaNote.objects.bulk_update(
                tieba_batch,
                ["publish_time_ms"],
                batch_size=_BATCH_SIZE,
            )
            tieba_batch.clear()
    if tieba_batch:
        TiebaNote.objects.bulk_update(
            tieba_batch,
            ["publish_time_ms"],
            batch_size=_BATCH_SIZE,
        )

    zhihu_time_map = {}
    zhihu_queryset = ZhihuContent.objects.only("id", "content_id", "created_time", "updated_time")
    zhihu_batch = []
    for content in zhihu_queryset.iterator(chunk_size=_BATCH_SIZE):
        content.created_time_ms = _coerce_timestamp_ms(content.created_time)
        content.updated_time_ms = _coerce_timestamp_ms(content.updated_time)
        zhihu_time_map[str(content.content_id)] = content.created_time_ms
        zhihu_batch.append(content)
        if len(zhihu_batch) >= _BATCH_SIZE:
            ZhihuContent.objects.bulk_update(
                zhihu_batch,
                ["created_time_ms", "updated_time_ms"],
                batch_size=_BATCH_SIZE,
            )
            zhihu_batch.clear()
    if zhihu_batch:
        ZhihuContent.objects.bulk_update(
            zhihu_batch,
            ["created_time_ms", "updated_time_ms"],
            batch_size=_BATCH_SIZE,
        )

    feed_batch = []
    for feed in MonitorFeed.objects.only("id", "platform", "content_id", "created_at").iterator(chunk_size=_BATCH_SIZE):
        feed_created_at = _coerce_timestamp_ms(feed.created_at)
        if feed.platform == "tieba":
            feed_created_at = tieba_time_map.get(str(feed.content_id)) or feed_created_at
        elif feed.platform == "zhihu":
            feed_created_at = zhihu_time_map.get(str(feed.content_id)) or feed_created_at
        feed.created_at = feed_created_at or 0
        feed_batch.append(feed)
        if len(feed_batch) >= _BATCH_SIZE:
            MonitorFeed.objects.bulk_update(feed_batch, ["created_at"], batch_size=_BATCH_SIZE)
            feed_batch.clear()
    if feed_batch:
        MonitorFeed.objects.bulk_update(feed_batch, ["created_at"], batch_size=_BATCH_SIZE)


def _dedupe_model_by_fields(model, field_names):
    duplicate_rows = (
        model.objects.values(*field_names)
        .annotate(row_count=Count("id"))
        .filter(row_count__gt=1)
    )
    pending_delete_ids = []

    for row in duplicate_rows.iterator(chunk_size=_BATCH_SIZE):
        filters = {field_name: row[field_name] for field_name in field_names}
        ids = list(
            model.objects.filter(**filters)
            .order_by("-last_modify_ts", "-add_ts", "-id")
            .values_list("id", flat=True)
        )
        pending_delete_ids.extend(ids[1:])
        if len(pending_delete_ids) >= _BATCH_SIZE:
            model.objects.filter(id__in=pending_delete_ids).delete()
            pending_delete_ids.clear()

    if pending_delete_ids:
        model.objects.filter(id__in=pending_delete_ids).delete()


def _dedupe_content_rows(apps, schema_editor):
    model_specs = (
        ("XhsNote", ("note_id",)),
        ("DouyinAweme", ("aweme_id",)),
        ("KuaishouVideo", ("video_id",)),
        ("WeiboNote", ("note_id",)),
        ("TiebaNote", ("note_id",)),
        ("ZhihuContent", ("content_id",)),
        ("MonitorFeed", ("platform", "content_id")),
    )

    for model_name, field_names in model_specs:
        model = apps.get_model("media_platform", model_name)
        _dedupe_model_by_fields(model, field_names)


class Migration(migrations.Migration):

    dependencies = [
        ("media_platform", "0007_add_ip_location_to_ks_bili_zhihu"),
    ]

    operations = [
        migrations.AddField(
            model_name="tiebanote",
            name="publish_time_ms",
            field=models.BigIntegerField(blank=True, db_index=True, null=True),
        ),
        migrations.AddField(
            model_name="zhihucontent",
            name="created_time_ms",
            field=models.BigIntegerField(blank=True, db_index=True, null=True),
        ),
        migrations.AddField(
            model_name="zhihucontent",
            name="updated_time_ms",
            field=models.BigIntegerField(blank=True, null=True),
        ),
        migrations.RunPython(
            _backfill_normalized_timestamps,
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.RunPython(
            _dedupe_content_rows,
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name="douyinaweme",
            name="aweme_id",
            field=models.BigIntegerField(
                db_index=True,
                unique=True,
                verbose_name="Aweme ID",
            ),
        ),
        migrations.AlterField(
            model_name="kuaishouvideo",
            name="video_id",
            field=models.CharField(
                db_index=True,
                max_length=255,
                unique=True,
                verbose_name="Video ID",
            ),
        ),
        migrations.AlterField(
            model_name="tiebanote",
            name="note_id",
            field=models.CharField(
                db_index=True,
                max_length=644,
                unique=True,
                verbose_name="Note ID",
            ),
        ),
        migrations.AlterField(
            model_name="weibonote",
            name="note_id",
            field=models.BigIntegerField(
                db_index=True,
                unique=True,
                verbose_name="Note ID",
            ),
        ),
        migrations.AlterField(
            model_name="xhsnote",
            name="note_id",
            field=models.CharField(
                db_index=True,
                max_length=255,
                unique=True,
                verbose_name="Note ID",
            ),
        ),
        migrations.AlterField(
            model_name="zhihucontent",
            name="content_id",
            field=models.CharField(
                db_index=True,
                max_length=64,
                unique=True,
                verbose_name="Content ID",
            ),
        ),
        migrations.RemoveField(
            model_name="tiebanote",
            name="publish_time",
        ),
        migrations.RenameField(
            model_name="tiebanote",
            old_name="publish_time_ms",
            new_name="publish_time",
        ),
        migrations.RemoveField(
            model_name="zhihucontent",
            name="created_time",
        ),
        migrations.RenameField(
            model_name="zhihucontent",
            old_name="created_time_ms",
            new_name="created_time",
        ),
        migrations.RemoveField(
            model_name="zhihucontent",
            name="updated_time",
        ),
        migrations.RenameField(
            model_name="zhihucontent",
            old_name="updated_time_ms",
            new_name="updated_time",
        ),
    ]
