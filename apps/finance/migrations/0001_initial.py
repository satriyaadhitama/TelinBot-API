# Generated by Django 5.0.3 on 2024-04-17 07:16

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Finance",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("year", models.IntegerField()),
                (
                    "q",
                    models.IntegerField(
                        choices=[(1, "Q1"), (2, "Q2"), (3, "Q3"), (4, "Q4")]
                    ),
                ),
                ("file", models.FileField(null=True, upload_to="documents/finance/")),
                ("created_at", models.DateTimeField(auto_now_add=True, null=True)),
                ("updated_at", models.DateTimeField(auto_now=True, null=True)),
            ],
        ),
    ]
