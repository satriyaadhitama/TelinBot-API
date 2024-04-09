from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.utils.termcolors import make_style
from dotenv import load_dotenv
from apps.user_auth.seeds import seed_superuser, seed_groups, seed_users
import MySQLdb
import configparser

import psycopg2
import os

load_dotenv()


class Command(BaseCommand):
    help = "Seeds database"

    def handle(self, *args, **options):
        yellow_style = make_style(fg="yellow")

        # Database Configuration
        config = configparser.ConfigParser()
        config.read("db.cnf")
        # database variables
        db_host = config["client"]["host"]
        db_user = config["client"]["user"]
        db_password = config["client"]["password"]
        db_name = config["client"]["database"]

        try:
            # Create Database if not exist
            db = MySQLdb.connect(host=db_host, user=db_user, passwd=db_password)
            cursor = db.cursor()
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
            )
            self.stdout.write(
                self.style.SUCCESS(f"Database {db_name} created or already exists.")
            )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to create database: {e}"))
        finally:
            if db:
                db.close()

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
