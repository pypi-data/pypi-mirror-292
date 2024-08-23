from datetime import datetime

def calculate_months_between(d1, d2):
    date_format = "%d.%m.%Y"
    start_date = datetime.strptime(d1, date_format)
    end_date = datetime.strptime(d2, date_format)

    # Calculate the number of months between the two dates
    months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
    return months

def get_months(date):
    date_format = "%d.%m.%Y"
    date=datetime.strptime(date,date_format)
    months=date.month
    return months

def get_year(date,date_format="%d.%m.%Y"):
    date=str(date)
    date=datetime.strptime(date,date_format)
    year=date.year
    year=int(year)
    return year