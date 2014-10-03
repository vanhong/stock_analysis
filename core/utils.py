from decimal import Decimal
import datetime

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

