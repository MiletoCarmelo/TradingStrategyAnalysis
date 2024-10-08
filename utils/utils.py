import pandas as pd
from datetime import datetime

def days_to_year_fraction(expiration_date):
    """
    Calculate the fraction of the year remaining until the expiration date.

    Parameters:
    - expiration_date: The expiration date as a string (format 'YYYY-MM-DD').

    Returns:
    - year_fraction: A float representing the fraction of the year remaining.
    """
    # Convert the expiration date string to a datetime object
    expiration = pd.to_datetime(expiration_date)
    current_date = datetime.now()

    # Calculate the difference in days
    delta_days = (expiration - current_date).days

    # Determine if the current year is a leap year
    if current_date.year % 4 == 0 and (current_date.year % 100 != 0 or current_date.year % 400 == 0):
        total_days_in_year = 366
    else:
        total_days_in_year = 365

    # Calculate the fraction of the year remaining
    year_fraction = delta_days / total_days_in_year

    return year_fraction