#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.http import HttpResponse
from reaserch.models import WawaGrowthPower, VKGrowthPower
from financial.models import SeasonFinancialRatio, YearFinancialRatio
from decimal import Decimal
from core.utils import season_to_date
from stocks.models import WatchList, StockId
from price.models import NewPrice
from datetime import *
import pdb
import csv

#找出籌碼跟股價 持續 高度相關的
def chip_price_relation(cnt, score, chip_type):
	strDate = 'date'
	strSymbol = 'symbol'
	strYoy = 'year_growth_rate'
	if revenue_type == 'month':
		filter_model = MonthRevenue
		table = 'stocks.stocks_monthrevenue'
	elif revenue_type == 'season':
		filter_model = SeasonRevenue
		table = 'stocks.stocks_seasonrevenue'
	else:
		return Nonetio

	#select date, symbol, data_kind, (value0_1 + value1_5 + value5_10) as sum1, (value600_800 + value800_1000 + value1000) as sum2 from stocks.chip_shareholderstructure
	dates = filter_model.objects.values(strDate).distinct().order_by('-' + strDate).values_list(strDate, flat=True)
	cursor = connection.cursor()
	#get the symbols which haven't updated the latest data
	pre_date_str = get_condition_str(dates, 2, cnt+2)
	#print pre_date_str
	query_str = ('SELECT * FROM ( SELECT symbol, AVG(year_growth_rate) avg_yoy from ' + table + ' A'
				' WHERE date in ' + pre_date_str + ' group by symbol) AS A  WHERE avg_yoy >= ' + str(growth_rate))
	cursor.execute(query_str)
	not_update_lists = cursor.fetchall()

	pre_date_str = get_condition_str(dates, 1, cnt+1)
	#print pre_date_str
	query_str = ('SELECT * FROM ( SELECT symbol, AVG(year_growth_rate) avg_yoy from ' + table + ' A'
				' WHERE date in ' + pre_date_str + ' group by symbol) AS B WHERE avg_yoy >= ' + str(growth_rate))
	cursor.execute(query_str)
	update_lists = cursor.fetchall()
	
	print '------Before Union-------'
	results = list(set(update_lists).union(set(not_update_lists)))
	result_symbols = map(lambda item: item[0], results)
	return result_symbols

#wawa growth power
def update_wawa_growth_power(request):
	print 'start update wawa growth power'
	if 'date' in request.GET:
		date = request.GET['date']
		if date != '':
			try:
				str_year, str_season = date.split('-')
				year = int(str_year)
				season = int(str_season)
			except:
					return HttpResponse("please input correct season 'year-season'")
		else:
			return HttpResponse("please input correct season 'year-season'")
	else:
		return HttpResponse("please input correct season 'year-season'")
	stockids = WatchList.objects.values_list('symbol', flat=True)
	for stockid in stockids:
		print("start " + stockid + "'s wawa growth power date:" + str_year + "-" + str_season)
		wawa_growth = WawaGrowthPower()
		wawa_growth.symbol = stockid
		wawa_growth.year = year
		wawa_growth.season = season
		wawa_growth.date = season_to_date(year, season)
		wawa_growth.surrogate_key = stockid + '_' + str(year) + str(season).zfill(2)
		if not SeasonFinancialRatio.objects.filter(symbol=stockid, year=year-1, season=season):
			continue
		if not YearFinancialRatio.objects.filter(symbol=stockid, year=year-1):
			continue
		if season == 1:
			financial_ratio = SeasonFinancialRatio.objects.get(symbol=stockid, year=year, season=season)
			wawa_growth.season_eps = financial_ratio.earnings_per_share
			wawa_growth.estimate_eps = wawa_growth.season_eps * 4
			wawa_growth.last_year_season_eps = SeasonFinancialRatio.objects.get(symbol=stockid, year=year-1, season=season).earnings_per_share
			wawa_growth.last_year_eps = YearFinancialRatio.objects.get(symbol=stockid, year=year-1).earnings_per_share
			wawa_growth.estimate_growth_rate = wawa_growth.estimate_eps / wawa_growth.last_year_eps - 1
			wawa_growth.reasonable_price = wawa_growth.estimate_growth_rate * Decimal(66) * wawa_growth.last_year_eps
			wawa_growth.save()
		elif season == 2:
			financial_ratio1 = SeasonFinancialRatio.objects.get(symbol=stockid, year=year, season=season-1)
			financial_ratio2 = SeasonFinancialRatio.objects.get(symbol=stockid, year=year, season=season)
			wawa_growth.season_eps = financial_ratio2.earnings_per_share
			wawa_growth.estimate_eps = (financial_ratio1.earnings_per_share + financial_ratio2.earnings_per_share) * 2
			wawa_growth.last_year_season_eps = SeasonFinancialRatio.objects.get(symbol=stockid, year=year-1, season=season).earnings_per_share
			wawa_growth.last_year_eps = YearFinancialRatio.objects.get(symbol=stockid, year=year-1).earnings_per_share
			wawa_growth.estimate_growth_rate = wawa_growth.estimate_eps / wawa_growth.last_year_eps - 1
			wawa_growth.reasonable_price = wawa_growth.estimate_growth_rate * Decimal(66) * wawa_growth.last_year_eps
			wawa_growth.save()
		elif season == 3:
			financial_ratio1 = SeasonFinancialRatio.objects.get(symbol=stockid, year=year, season=season-2)
			financial_ratio2 = SeasonFinancialRatio.objects.get(symbol=stockid, year=year, season=season-1)
			financial_ratio3 = SeasonFinancialRatio.objects.get(symbol=stockid, year=year, season=season)
			wawa_growth.season_eps = financial_ratio3.earnings_per_share
			wawa_growth.estimate_eps = (financial_ratio1.earnings_per_share + financial_ratio2.earnings_per_share + financial_ratio3.earnings_per_share) * 4 / 3
			wawa_growth.last_year_season_eps = SeasonFinancialRatio.objects.get(symbol=stockid, year=year-1, season=season).earnings_per_share
			wawa_growth.last_year_eps = YearFinancialRatio.objects.get(symbol=stockid, year=year-1).earnings_per_share
			wawa_growth.estimate_growth_rate = wawa_growth.estimate_eps / wawa_growth.last_year_eps - 1
			wawa_growth.reasonable_price = wawa_growth.estimate_growth_rate * Decimal(66) * wawa_growth.last_year_eps
			wawa_growth.save()
		elif season == 4:
			financial_ratio1 = SeasonFinancialRatio.objects.get(symbol=stockid, year=year, season=season-3)
			financial_ratio2 = SeasonFinancialRatio.objects.get(symbol=stockid, year=year, season=season-2)
			financial_ratio3 = SeasonFinancialRatio.objects.get(symbol=stockid, year=year, season=season-1)
			financial_ratio4 = SeasonFinancialRatio.objects.get(symbol=stockid, year=year, season=season)
			wawa_growth.season_eps = financial_ratio4.earnings_per_share
			wawa_growth.estimate_eps = financial_ratio1.earnings_per_share + financial_ratio2.earnings_per_share + \
									   financial_ratio3.earnings_per_share + financial_ratio4.earnings_per_share
			wawa_growth.last_year_season_eps = SeasonFinancialRatio.objects.get(symbol=stockid, year=year-1, season=season).earnings_per_share
			wawa_growth.last_year_eps = YearFinancialRatio.objects.get(symbol=stockid, year=year-1).earnings_per_share
			wawa_growth.estimate_growth_rate = wawa_growth.estimate_eps / wawa_growth.last_year_eps - 1
			wawa_growth.reasonable_price = wawa_growth.estimate_growth_rate * Decimal(66) * wawa_growth.estimate_eps
			wawa_growth.save()
		print("update " + stockid + "'s wawa growth power date:" + str_year + "-" + str_season)
	return HttpResponse('update wawa_growth')

def update_vk_growth_power(request):
	print 'start update vk growth power'
	if 'date' in request.GET:
		date = request.GET['date']
		if date != '':
			try:
				str_year, str_season = date.split('-')
				year = int(str_year)
				season = int(str_season)
			except:
					return HttpResponse("please input correct season 'year-season'")
		else:
			return HttpResponse("please input correct season 'year-season'")
	else:
		return HttpResponse("please input correct season 'year-season'")
	stockids = WatchList.objects.values_list('symbol', flat=True)
	for stockid in stockids:
		vk_growth = VKGrowthPower()
		vk_growth.symbol = stockid
		vk_growth.year = year
		vk_growth.season = season
		vk_growth.date = season_to_date(year, season)
		vk_growth.surrogate_key = stockid + '_' + str(year) + str(season).zfill(2)
		financial_ratios = SeasonFinancialRatio.objects.filter(symbol=stockid).order_by('-date')
		if (len(financial_ratios) >= 8):
			financial_ratio = financial_ratios[0]
			financial_ratio1 = financial_ratios[1]
			financial_ratio2 = financial_ratios[2]
			financial_ratio3 = financial_ratios[3]
			financial_ratio4 = financial_ratios[4]
			financial_ratio5 = financial_ratios[5]
			financial_ratio6 = financial_ratios[6]
			financial_ratio7 = financial_ratios[7]
			vk_growth.season_eps = financial_ratio.earnings_per_share
			vk_growth.estimate_eps = financial_ratio.earnings_per_share + financial_ratio1.earnings_per_share + \
									 financial_ratio2.earnings_per_share + financial_ratio3.earnings_per_share
			vk_growth.last_year_season_eps = financial_ratio4.earnings_per_share
			vk_growth.last_year_eps = financial_ratio4.earnings_per_share + financial_ratio5.earnings_per_share + \
									  financial_ratio6.earnings_per_share + financial_ratio7.earnings_per_share
			vk_growth.estimate_growth_rate = vk_growth.estimate_eps / vk_growth.last_year_eps - 1
			vk_growth.reasonable_price = vk_growth.estimate_growth_rate * 66 * vk_growth.estimate_eps
			vk_growth.save()
			print("update " + stockid + "'s vk growth power date:" + str_year + "-" + str_season)
		else:
			print(stockid + "'s data not enough to update vk growth power")
	return HttpResponse('update vk_growth date:' + str_year + "-"+ str_season)

def down_load_growth(request):
	if 'date' in request.GET:
		date = request.GET['date']
		if date != '':
			try:
				str_year, str_season = date.split('-')
				year = int(str_year)
				season = int(str_season)
			except:
					return HttpResponse("please input correct season 'year-season'")
		else:
			return HttpResponse("please input correct season 'year-season'")
	else:
		return HttpResponse("please input correct season 'year-season'")
	response = HttpResponse(content_type='text/csv')
	today = datetime.today()
	filename = 'growth_power_' + today.strftime('%Y%m%d') + '.csv'
	response['Content-Disposition'] = 'attachment; filename=' + filename
	writer = csv.writer(response, delimiter=',', quotechar='"')
	header = ['StockID','Name', 'Type','W_G', 'V_G', 'Price', 'SeasonEPS', 'LastYearSeasonEPS',
			  'W_ReasonablePrice', 'W_GrowthRate', 'W_EstiamteEPS', 'W_LastYearEPS', 
			  'V_ResonablePrice', 'V_GrowthRate', 'V_EstimateEPS', 'V_LastYearEPS']
	writer.writerow([x for x in header])
	stockids = WatchList.objects.values_list('symbol', flat=True)
	for stockid in stockids:
		if (StockId.objects.filter(symbol__contains=stockid)):
			stockId = StockId.objects.get(symbol=stockid)
			body = [stockid]
			body.append(stockId.name)
			body.append(stockId.company_type)
			body.append('')
			body.append('')
			if (NewPrice.objects.filter(symbol=stockid)):
				price = NewPrice.objects.filter(symbol=stockid).order_by('-date')[0].close_price
				body.append(str(price))
			else:
				body.append('0')
			if (WawaGrowthPower.objects.filter(symbol=stockid, year=year, season=season)):
				growth_power = WawaGrowthPower.objects.get(symbol=stockid, year=year, season=season)
				body.append(str(growth_power.season_eps))
				body.append(str(growth_power.last_year_season_eps))
				body.append(str(growth_power.reasonable_price))
				body.append(str(growth_power.estimate_growth_rate))
				body.append(str(growth_power.estimate_eps))
				body.append(str(growth_power.last_year_eps))
			else:
				body.append('')
				body.append('')
				body.append('')
				body.append('')
				body.append('')
				body.append('')
			if (VKGrowthPower.objects.filter(symbol=stockid, year=year, season=season)):
				vk_growth_power = VKGrowthPower.objects.get(symbol=stockid, year=year, season=season)
				body.append(str(vk_growth_power.reasonable_price))
				body.append(str(vk_growth_power.estimate_growth_rate))
				body.append(str(vk_growth_power.estimate_eps))
				body.append(str(vk_growth_power.last_year_eps))
			else:
				body.append('')
				body.append('')
				body.append('')
				body.append('')
			writer.writerow([x.encode("cp950") for x in body])
	return response

def update_avg_pe(request):
	if 'year' in request.GET:
		str_year = request.GET['year']
		try:
			year = int(str_year)
		except:
			return HttpResponse("please input correct 'year'")
		else:
			return HttpResponse("please input correct 'year'")
	else:
		return HttpResponse("please input correct 'year'")
	yfrs = YearFinancialRatio.objects.filter(year=year, symbol='6274')
	for yfr in yfrs:
		max_price = 0;
		min_price = 1000000;
		prices = NewPrice.objects.filter(symbol=yfr.symbol)
		for price in prices:
			if price.close_price > max_price:
				max_price = price.close_price
			if price.close_price < min_price:
				min_price = price.close_price
		avg_pe = AvgPE()
		avg_pe.surrogate_key = yfr.symbol + '_' + str(year)
		avg_pe.symbol = yfr.symbol
		avg_pe.year = year
		avg_pe.date = season_to_date(year, 1)
		avg_pe.low_price = min_price;
		avg_pe.high_price = max_price;
		avg_pe.eps = yfr.earnings_per_share
		avg_pe.pe = (avg_pe.low_price + avg_pe.high_price) / 2 / avg_pe.eps
	return HttpResponse('update avg pe')