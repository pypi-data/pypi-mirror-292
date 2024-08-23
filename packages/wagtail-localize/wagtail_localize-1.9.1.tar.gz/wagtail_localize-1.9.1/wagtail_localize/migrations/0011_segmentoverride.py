# Generated by Django 3.1.2 on 2020-10-23 10:24

import django.db.models.deletion

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("wagtailcore", "0059_apply_collection_ordering"),
        ("wagtail_localize", "0010_overridablesegment"),
    ]

    operations = [
        migrations.CreateModel(
            name="SegmentOverride",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("data_json", models.TextField()),
                ("has_error", models.BooleanField(default=False)),
                ("field_error", models.TextField(blank=True)),
                (
                    "context",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="overrides",
                        to="wagtail_localize.translationcontext",
                    ),
                ),
                (
                    "last_translated_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "locale",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="overrides",
                        to="wagtailcore.locale",
                    ),
                ),
            ],
        ),
    ]
