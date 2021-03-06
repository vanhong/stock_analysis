from decimal import Decimal
import datetime


def is_decimal(s):
    try:
        Decimal(s)
    except:
        return False
    return True

def st_to_decimal(data):
	return Decimal(data.strip().replace(',', ''))

def season_to_date(year, season):
	if season == 1:
		return datetime.date(year, 1, 1)
	elif season == 2:
		return datetime.date(year, 4, 1)
	elif season == 3:
		return datetime.date(year, 7, 1)
	elif season == 4:
		return datetime.date(year, 10, 1)

def year_to_date(year):
    return datetime.date(year, 1, 1)

def last_month(day):
    if day.month == 1:
        return day.year - 1, 12
    else:
        return day.year, day.month - 1

def last_season(day):
    year = day.year
    month = day.month
    if month <= 3:
        season = 4
        year -= 1
    elif month >= 4 and month <= 6:
        season = 1
    elif month >= 7 and month <= 9:
        season = 2
    elif month >= 10:
        season = 3
    return year, season

def next_month(day):
    if day.month == 12:
        return datetime.date(day.year+1, 1, 1)
    else:
        return datetime.date(day.year, day.month+1, 1)

def month_between(startDate, endDate):
    return (endDate.year - startDate.year) * 12 + endDate.month - startDate.month
