import datetime
import random


def random_datetime_today():
    today = datetime.date.today()
    start_of_today = datetime.datetime(today.year, today.month, today.day)
    end_of_today = start_of_today + datetime.timedelta(days=1)
    random_seconds = random.randint(0, 86400)  # There are 86400 seconds in a day
    return start_of_today + datetime.timedelta(seconds=random_seconds)


def random_datetime_this_month():
    today = datetime.date.today()
    start_of_month = datetime.datetime(today.year, today.month, 1)
    if today.month == 12:
        start_of_next_month = datetime.datetime(today.year + 1, 1, 1)
    else:
        start_of_next_month = datetime.datetime(today.year, today.month + 1, 1)
    seconds_in_month = int((start_of_next_month - start_of_month).total_seconds())
    random_seconds = random.randint(0, seconds_in_month)
    return start_of_month + datetime.timedelta(seconds=random_seconds)


def random_datetime_this_year():
    today = datetime.date.today()
    start_of_year = datetime.datetime(today.year, 1, 1)
    start_of_next_year = datetime.datetime(today.year + 1, 1, 1)
    seconds_in_year = int((start_of_next_year - start_of_year).total_seconds())
    random_seconds = random.randint(0, seconds_in_year)
    return start_of_year + datetime.timedelta(seconds=random_seconds)


def random_date_before_curr_year(min_year):
    """
    Generates a random date between min_year and the current date.

    Parameters:
    - min_year: An integer specifying the minimum year limit.

    Returns:
    - A datetime.date object representing a random date within the specified range.
    """
    start_date = datetime.datetime(min_year, 1, 1)
    end_date = datetime.datetime.now()

    # Calculate the difference between start and end dates
    time_between_dates = end_date - start_date
    # Convert the difference to days
    days_between_dates = time_between_dates.days
    # Generate a random number of days to add to the start date
    random_number_of_days = random.randrange(days_between_dates)
    # Generate the random date
    random_date = start_date + datetime.timedelta(days=random_number_of_days)

    return random_date.date()  # Return the date part


def get_prev_month(year, month):
    prev_month = month - 1 if month > 1 and month < 12 else 12
    prev_year = year - 1 if prev_month == 12 else year
    return prev_year, prev_month
