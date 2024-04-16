from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.utils.termcolors import make_style
from django.conf import settings
from dotenv import load_dotenv
from apps.user_auth.seeds import seed_superuser, seed_groups, seed_users
from apps.base.seeds import seed_data_from_csv
from apps.services.models import (
    FactNewCustomerRegion,
    FactTopCDN,
    FactTopTraffic,
    FactTrafficCDN,
)

import MySQLdb
import configparser
import os
import warnings

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

        # Seeding from file
        
        
        # Ignore DateTimeField naive datetime warnings globally
        warnings.filterwarnings(
            "ignore",
            message="DateTimeField .* received a naive datetime",
            category=RuntimeWarning,
            module='django.db.models.fields'
        )
        
        static_path = os.path.join(settings.BASE_DIR, "static", "data")
        files = [
            "fact_new_customer_region.csv",
            "fact_top_cdn.csv",
            "fact_top_traffic.csv",
            "fact_traffic_cdn.csv",
        ]

        models = [FactNewCustomerRegion, FactTopCDN, FactTopTraffic, FactTrafficCDN]

        for i, (file, model) in enumerate(zip(files, models)):
            csv_file = os.path.join(static_path, file)
            seed_data_from_csv(csv_file, model)
