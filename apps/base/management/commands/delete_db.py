from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.utils.termcolors import make_style
from django.db import transaction
from dotenv import load_dotenv
import configparser
import MySQLdb

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

        # Database Configuration
        config = configparser.ConfigParser()
        config.read("db.cnf")
        # database variables
        db_host = config["client"]["host"]
        db_user = config["client"]["user"]
        db_password = config["client"]["password"]
        db_name = config["client"]["database"]

        try:
            db = MySQLdb.connect(host=db_host, user=db_user, passwd=db_password)
            cursor = db.cursor()

            # Execute the drop database command
            cursor.execute(f"DROP DATABASE IF EXISTS {db_name};")

            print(f"Successfully deleted database: {db_name}")

        except Exception as e:
            print(f"Error deleting database: {e}")

        finally:
            if db:
                db.close()
