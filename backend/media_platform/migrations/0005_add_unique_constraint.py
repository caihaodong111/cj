# Generated manually to fix duplicate data issue

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("media_platform", "0004_monitorfeed_sentiment_fields"),
    ]

    operations = [
        # Step 1: Delete duplicate records, keep the one with highest id (most recent)
        migrations.RunSQL(
            """
            DELETE t1 FROM monitor_feed t1
            INNER JOIN monitor_feed t2
            WHERE t1.platform = t2.platform
              AND t1.content_id = t2.content_id
              AND t1.id < t2.id
            """,
            reverse_sql=migrations.RunSQL.noop
        ),
        # Step 2: Add unique index on platform + content_id
        migrations.RunSQL(
            """
            ALTER TABLE monitor_feed
            ADD UNIQUE INDEX idx_unique_platform_content (platform, content_id)
            """,
            reverse_sql="ALTER TABLE monitor_feed DROP INDEX idx_unique_platform_content"
        ),
    ]
