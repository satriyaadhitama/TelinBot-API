from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.utils.termcolors import make_style
from django.db import transaction
from dotenv import load_dotenv
from apps.user_auth.seeds import seed_superuser, seed_groups, seed_users

import psycopg2
import os

load_dotenv()


class Command(BaseCommand):
    help = "Seeds database"

    def handle(self, *args, **options):
        yellow_style = make_style(fg="yellow")

        # Create Database if not exist
        # You might want to add error handling and ensure that PASSWORD is not None
        conn_string = f"dbname='postgres' user='{os.environ['DB_USER']}' host='{os.environ['DB_HOST']}' password='{os.environ['DB_PASSWORD']}'"
        conn = psycopg2.connect(conn_string)
        conn.autocommit = True

        cursor = conn.cursor()
        try:
            cursor.execute(f"CREATE DATABASE {os.environ['DB_NAME']}")
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully created database {os.environ['DB_NAME']}"
                )
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to create database: {e}"))
        finally:
            cursor.close()
            conn.close()

        # Make migrations
        self.stdout.write(yellow_style("Making migrations..."))
        call_command("makemigrations", interactive=False)

        # Apply migrations
        self.stdout.write(yellow_style("\nApplying migrations..."))
        call_command("migrate", interactive=False)

        self.stdout.write(yellow_style("\nSeeding data..."))

        # From Auth App
        seed_groups()
        self.stdout.write(self.style.SUCCESS("Groups seeded"))
        seed_superuser()
        self.stdout.write(self.style.SUCCESS("Superuser seeded"))
        seed_users()
        self.stdout.write(self.style.SUCCESS("Users seeded"))
