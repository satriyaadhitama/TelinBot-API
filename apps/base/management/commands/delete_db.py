from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.utils.termcolors import make_style
from django.db import transaction
from dotenv import load_dotenv

import psycopg2
import os
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

load_dotenv()


class Command(BaseCommand):
    help = "Delete database"

    def handle(self, *args, **options):
        # Confirm action
        confirm = input(
            "WARNING: This will delete the entire database. Are you sure you want to proceed? Type 'y' to continue: "
        )
        if confirm.lower() != "y":
            print("Action cancelled.")
            return

        db_name = os.environ.get("DB_NAME")
        db_user = os.environ.get("DB_USER")
        db_password = os.environ.get("DB_PASSWORD")
        db_host = os.environ.get("DB_HOST")

        try:
            # Connection string with fallback values
            conn_string = f"dbname='postgres' user='{db_user}' host='{db_host}' password='{db_password}'"
            conn = psycopg2.connect(conn_string)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

            cursor = conn.cursor()
            # Terminate all active connections to the target database
            cursor.execute(
                f"""
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = '{db_name}'
            AND pid <> pg_backend_pid();
            """
            )
            # Execute the drop database command
            cursor.execute(f"DROP DATABASE IF EXISTS {db_name};")
            cursor.close()
            conn.close()

            print(f"Successfully deleted PostgreSQL database: {db_name}")

        except Exception as e:
            print(f"Error deleting database: {e}")
