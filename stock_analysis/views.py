﻿# -*- coding: utf-8 -*-

import json
from decimal import *
from django.http import HttpResponse, Http404
from django.template.loader import get_template
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.template import Context
from stock_analysis.settings import STATIC_URL

from stocks.models import StockId, MonthRevenue, Dividend, SeasonProfit
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from financial.models import SeasonFinancialRatio

def home(request):
	return render_to_response('home/index.html', context_instance = RequestContext(request))

def analysis(request):
	return render_to_response('analysis/index.html', 
							  context_instance = RequestContext(request))

def set_stockid(request):
	if 'q' in request.GET:
		stockid = request.GET['q']
		if StockId.objects.filter(symbol=stockid):
			request.session['stock_id'] = stockid
			stockname = StockId.objects.get(symbol=stockid)
			name = stockname.name.encode('utf-8') + '(' + str(stockid) + ')'
			return render_to_response('analysis/index.html', {"stock_id": name}, 
									  context_instance = RequestContext(request))
		else:
			return HttpResponse('stockid error')

def getSymbol(request):
	try:
		symbol = request.session['stock_id']
	except:
		symbol = '2330'
	return symbol

def performance_per_share(request):
	symbol = getSymbol(request)
	stockname = StockId.objects.get(symbol=symbol)
	performance_head = []
	performance_head.append(r'年/季')
	performance_head.append(r'每股稅前盈餘')
	performance_head.append(r'每股稅後盈餘')
	performance_body = []
	if StockId.objects.filter(symbol=symbol):
		ratios = SeasonFinancialRatio.objects.filter(symbol=symbol).order_by('-surrogate_key')
		if ratios:
			for ratio in ratios:
				item = []
				item.append(str(ratio.year) + 'Q' + str(ratio.season))
				item.append(ratio.net_before_tax_profit_per_share)
				item.append(ratio.net_after_tax_profit_per_share)
				performance_body.append(item)
			name = stockname.name.encode('utf-8') + '(' + str(symbol) + ')'
			return render_to_response(
				'analysis/performance_per_share.html', {"stock_id": name, "performance_head": performance_head,
				"performance_body": performance_body},
				context_instance = RequestContext(request))
	return render_to_response(
		'analysis/performance_per_share.html',{"stock_id": getSymbol(request)},
		context_instance = RequestContext(request))

def dividend_table(request):
	symbol = getSymbol(request)
	stockname = StockId.objects.get(symbol=symbol)
	heads = []
	heads.append(r'年度')
	heads.append(r'現金股利')
	heads.append(r'盈餘配股')
	heads.append(r'公積配股')
	heads.append(r'股票股利')
	heads.append(r'合計')
	heads.append(r'員工配股率%')
	bodys = []
	if StockId.objects.filter(symbol=symbol):
		dividends = Dividend.objects.filter(symbol=symbol).order_by('-surrogate_key')
		if dividends:
			for dividend in dividends:
				item = []
				item.append(dividend.year)
				item.append(round(dividend.cash_dividends, 2))
				item.append(round(dividend.stock_dividends_from_retained_earnings, 2))
				item.append(round(dividend.stock_dividends_from_capital_reserve, 2))
				item.append(round(dividend.stock_dividends, 2))
				item.append(round(dividend.total_dividends, 2))
				item.append(round(dividend.employee_stock_rate, 2))
				bodys.append(item)
			name = stockname.name.encode('utf-8') + '(' + str(symbol) + ')'
			return render_to_response(
				'analysis/analysis_table.html', {"stock_id": name, "heads": heads,
				"bodys": bodys},
				context_instance = RequestContext(request))
	return render_to_response(
		'analysis/analysis_table.html',{"stock_id": getSymbol(request)},
		context_instance = RequestContext(request))

def profitability(request):
	symbol = getSymbol(request)
	stockname = StockId.objects.get(symbol=symbol)
	profit_title = r'季獲利能力'
	profit_head = []
	profit_head.append(r'季度')
	profit_head.append(r'毛利率')
	profit_head.append(r'營益率')
	profit_head.append(r'稅前盈利率')
	profit_head.append(r'稅後盈利率')
	profit_body = []
	if StockId.objects.filter(symbol=symbol):
		season_profits = SeasonFinancialRatio.objects.filter(symbol=symbol).order_by('-surrogate_key')
		if season_profits:
			for profit in season_profits:
				item = []
				item.append(str(profit.year)+'Q'+str(profit.season))
				item.append(profit.gross_profit_margin)
				item.append(profit.operating_profit_margin)
				item.append(profit.net_before_tax_profit_margin)
				item.append(profit.net_after_tax_profit_margin)
				profit_body.append(item)
			name = stockname.name.encode('utf-8') + '(' + str(symbol) + ')'
			return render_to_response(
				'analysis/profitability.html', {"stock_id": name, "profit_title": profit_title,
				"profit_head": profit_head, "profit_body": profit_body},
				context_instance = RequestContext(request))
	return render_to_response(
		'analysis/profitability.html',{"stock_id": getSymbol(request)},
		context_instance = RequestContext(request))

def revenue(request):
	return render_to_response(
		'analysis/revenue.html',
		context_instance = RequestContext(request))

def dividend(request):
	return render_to_response(
		'analysis/dividend.html',
		context_instance = RequestContext(request))

def month_revenue(request):
	symbol = getSymbol(request)
	stockname = StockId.objects.get(symbol=symbol)
	heads = []
	heads.append(r'年/月')
	heads.append(r'營收(仟元)')
	heads.append(r'月增率')
	heads.append(r'去年同期(仟元)')
	heads.append(r'年增率')
	heads.append(r'累計營收(仟元)')
	heads.append(r'年增率')
	bodys = []
	if StockId.objects.filter(symbol=symbol):
		month_revenues = MonthRevenue.objects.filter(symbol=symbol).order_by('-surrogate_key')
		if month_revenues:
			for revenue in month_revenues:
				item = []
				item.append(str(revenue.year)+r'/'+str(revenue.month))
				item.append(revenue.revenue)
				item.append(revenue.month_growth_rate)
				item.append(revenue.last_year_revenue)
				item.append(revenue.year_growth_rate)
				item.append(revenue.acc_revenue)
				item.append(revenue.acc_year_growth_rate)
				bodys.append(item)

			name = stockname.name.encode('utf-8') + '(' + str(symbol) + ')'
			return render_to_response(
				'analysis/analysis_table.html', {"stock_id": name,
				"heads": heads, "bodys": bodys},
				context_instance = RequestContext(request))
	return render_to_response(
		'analysis/index.html',{"stock_id": symbol},
		context_instance = RequestContext(request))

def season_revenue(request):
	symbol = getSymbol(request)
	stockname = StockId.objects.get(symbol=symbol)
	heads = []
	heads.append(r'年/季')
	heads.append(r'稅後盈餘(仟元)')
	heads.append(r'季增率')
	heads.append(r'去年同期(仟元)')
	heads.append(r'年增率')
	heads.append(r'累計盈餘(仟元)')
	heads.append(r'年增率')
	bodys = []
	if StockId.objects.filter(symbol=symbol):
		season_revenues = SeasonProfit.objects.filter(symbol=symbol).order_by('-surrogate_key')
		if season_revenues:
			for revenue in season_revenues:
				item = []
				item.append(str(revenue.year) + r'/' + str(revenue.season))
				item.append(revenue.profit)
				item.append(revenue.season_growth_rate)
				item.append(revenue.last_year_profit)
				item.append(revenue.year_growth_rate)
				item.append(revenue.acc_profit)
				item.append(revenue.acc_year_growth_rate)
				bodys.append(item)
			name = stockname.name.encode('utf-8') + '(' + str(symbol) + ')'
			return render_to_response(
				'analysis/analysis_table.html', {
				"stock_id": name,
				"heads": heads, "bodys": bodys},
				context_instance = RequestContext(request))
	return HttpResponse('error')

def filter(request):
	symbol = request.session['stock_id']

def ajax_user_search(request):
	q = request.GET.get('q')
	if q is not None:
		return HttpResponse('ajax_usr_search ' + q)

def index(request):
	return HttpResponse('index')

def getSeasonRevenueChart(request):
	symbol = getSymbol(request)
	maxProfit = 0
	maxGrowthRate = -100
	minGrowthRate = 10000
	dataNum = 0
	if StockId.objects.filter(symbol=symbol):
		season_profits = SeasonProfit.objects.filter(symbol=symbol).order_by('surrogate_key')
		profit_data = []
		growth_rate_data = []
		xAxis_categories = []
		for profit in season_profits:
			if profit.profit is not None and profit.year_growth_rate is not None:
				int_season_profit = int(profit.profit)
				if int_season_profit > maxProfit:
					maxProfit = int_season_profit
				profit_data.append(int_season_profit)
				float_year_growth_rate = float(profit.year_growth_rate)
				if float_year_growth_rate > maxGrowthRate:
					maxGrowthRate = float_year_growth_rate
				if float_year_growth_rate < minGrowthRate:
					minGrowthRate = float_year_growth_rate
				growth_rate_data.append(float_year_growth_rate)
				xAxis_categories.append(str(profit.year) + 'Q' + str(profit.season))
		if len(profit_data) > 24:
			dataNum = 24
		else:
			dataNum = len(profit_data)
	data = {'revenue' : profit_data, 'growth_rate': growth_rate_data, 'categories' : xAxis_categories,
			'maxRevenue': maxProfit, 'maxGrowthRate' : maxGrowthRate, 'minGrowthRate': minGrowthRate,
			'dataNum' : dataNum}
	return HttpResponse(json.dumps(data), content_type="application/json")

def getRevenueChart(request):
	symbol = getSymbol(request)
	maxRevenue = 0
	maxGrowthRate = -100
	minGrowthRate = 10000
	dataNum = 0
	if StockId.objects.filter(symbol=symbol):
		month_revenues = MonthRevenue.objects.filter(symbol=symbol).order_by('surrogate_key')
		revenue_data = []
		growth_rate_data = []
		xAxis_categories = []
		for revenue in month_revenues:
			if revenue.revenue is not None and revenue.year_growth_rate is not None:
				intMonthRevenue = int(revenue.revenue)
				if intMonthRevenue > maxRevenue:
					maxRevenue = intMonthRevenue
				revenue_data.append(intMonthRevenue)
				floatYearGrowthRate = float(revenue.year_growth_rate)
				if floatYearGrowthRate > maxGrowthRate:
					maxGrowthRate = floatYearGrowthRate
				if floatYearGrowthRate < minGrowthRate:
					minGrowthRate = floatYearGrowthRate
				growth_rate_data.append(floatYearGrowthRate)
				xAxis_categories.append(str(revenue.year) + '/' + str(revenue.month).zfill(2))
		if len(revenue_data) > 24:
			dataNum = 24
		else:
			dataNum = len(revenue_data)
	data = {'revenue' : revenue_data, 'growth_rate' : growth_rate_data, 'categories' : xAxis_categories,
			'maxRevenue' : maxRevenue, 'maxGrowthRate' : maxGrowthRate, 'minGrowthRate': minGrowthRate,
			'dataNum' : dataNum}
	
	return HttpResponse(json.dumps(data), content_type="application/json")

def getDividendChart(request):
	data = {}
	symbol = getSymbol(request)
	if StockId.objects.filter(symbol=symbol):
		dividends = Dividend.objects.filter(symbol=symbol).order_by('-surrogate_key')[0:10]
		xAxis_categories = []
		cash_dividends = []
		stock_dividends = []
		for dividend in dividends:
			xAxis_categories.append(str(dividend.year))
			cash_dividends.append(round(float(dividend.cash_dividends), 2))
			stock_dividends.append(round(float(dividend.stock_dividends), 2))
	data = {'categories': xAxis_categories[::-1], 'cash_dividends': cash_dividends[::-1], 'stock_dividends': stock_dividends[::-1]}
	return HttpResponse(json.dumps(data), content_type="application/json")

def get_performance_per_share(request):
	data = {}
	symbol = getSymbol(request)
	if StockId.objects.filter(symbol=symbol):
		season_financial_ratios = SeasonFinancialRatio.objects.filter(symbol=symbol).order_by('-surrogate_key')
		net_before_tax_profit_per_shares = []
		net_after_tax_profit_per_shares = []
		for ratio in season_financial_ratios:
			net_before_tax_profit_per_shares.append(float(ratio.net_before_tax_profit_per_share))
			net_after_tax_profit_per_shares.append(float(ratio.net_after_tax_profit_per_share))
	data = {'net_before_tax_profit_per_shares': net_before_tax_profit_per_shares,
			'net_after_tax_profit_per_shares': net_after_tax_profit_per_shares}
	return HttpResponse(json.dumps(data), content_type="application/json")

def filter_index(request):
	return render_to_response(
		'filter/filter_index.html', {},
		context_instance = RequestContext(request))

@csrf_exempt
def filter_start(request):
	print 'Start to Filter'
	conditions = {}
	for key, value in request.POST.iteritems():
		condition = key.split('-')[0];
		para = key.split('-')[1];
		if conditions.has_key(condition) is False:
			conditions[condition] = {para: value}
		else:
			conditions[condition][para] = value
		print 'condition=' + condition + ', para=' + para + ', value=' + value
		print len(conditions[condition])

	results = {}

	passed = True
	dataArr = []
	for key, value in conditions.iteritems(): #逐一條件做篩選
		if key == 'MonthRevenueContinuousAnnualGrowth': #月營收連續幾個月年增率>多少
			# print 'start to check ' + stockid.symbol + ' MonthRevenueContinuousAnnualGrowth'
			data = ''
			monthCnt = value['MonthCnt']
			MonthRevenueAnnualGrowth = value['MonthRevenueAnnualGrowth']

			dates = MonthRevenue.objects.values('year', 'month').distinct().order_by('-year', '-month')
			print str(dates[0]['year']) + '-' + str(dates[0]['month'])

			# revenues = MonthRevenue.objects.filter(symbol=stockid.symbol).order_by('-year', '-month')
			if monthCnt == '' or MonthRevenueAnnualGrowth == '':
				#print 'empty input to filter MonthRevenueContinuousAnnualGrowth'
				continue

			if len(dates) >= int(monthCnt):
				yearStr = ''
				monthStr = ''
				for i in range(0, int(monthCnt)):
					yearStr += str(dates[i]['year']) +','
					monthStr += str(dates[i]['month']) + ','
				yearStr = yearStr[:-1]
				monthStr = monthStr[:-1]
				whereStr = 'stocks_monthrevenue.year in (' + yearStr + ') and stocks_monthrevenue.month in (' + monthStr + ') and stocks_monthrevenue.year_growth_rate > ' + MonthRevenueAnnualGrowth
				filters = MonthRevenue.objects.extra(where=[whereStr])
				for item in filters:
					print item.symbol
				
			# 	data += str(revenues[i].year) + '-' + str(revenues[i].month) + '=' + str(revenues[i].year_growth_rate) + '%; '
			# 	if passed:
			# 		dataArr.append('[' + data + ']')
			# else:
			# 	passed = False
		elif key == 'SeasonOPM':
			# print 'start to check ' + stockid.symbol + ' OPM'
			SeasonCnt = value['SeasonCnt']
			SeasonOPM = value['SeasonOPM']
			OverUnder = value['OverUnder']
			ratios = SeasonFinancialRatio.objects.filter(symbol=stockid.symbol).order_by('-year','-season')
			dataList = [d.operating_profit_margin for d in ratios]
			data = checkData(dataList, SeasonCnt, OverUnder, SeasonOPM)
			#print 'get checkData return=' + data
			if data != '':
				dataArr.append('SeasonOPM=' + data)
			else:
				passed = False
		elif key == 'SeasonGPM':
			# print 'start to check ' + stockid.symbol + ' GPM'
			SeasonCnt = value['SeasonCnt']
			SeasonGPM = value['SeasonGPM']
			OverUnder = value['OverUnder']
			ratios = SeasonFinancialRatio.objects.filter(symbol=stockid.symbol).order_by('-year','-season')
			dataList = [d.gross_profit_margin for d in ratios]
			data = checkData(dataList, SeasonCnt, OverUnder, SeasonGPM)
			# print 'get GPM checkData return=' + data
			if data != '':
				dataArr.append('SeasonGPM=' + data)
			else:
				passed = False

	# if passed:
	# 	results[stockid.symbol] = ';'.join(dataArr)
	# 	#print stockid.symbol
	# 	print 'key=' + stockid.symbol + ', value=' + results[stockid.symbol]
		#print revenues[0].year
	return render_to_response(
				'filter/filter_result.html', {
				"results": results},
				context_instance = RequestContext(request))

def filter_start_old(request):
	print 'Start to Filter'
	conditions = {}
	for key, value in request.POST.iteritems():
		condition = key.split('-')[0];
		para = key.split('-')[1];
		if conditions.has_key(condition) is False:
			conditions[condition] = {para: value}
		else:
			conditions[condition][para] = value
		print 'condition=' + condition + ', para=' + para + ', value=' + value
		print len(conditions[condition])

	results = {}
	stock_ids = StockId.objects.all()
	for stockid in stock_ids:
		passed = True
		dataArr = []
		for key, value in conditions.iteritems(): #逐一條件做篩選
			if key == 'MonthRevenueContinuousAnnualGrowth': #月營收連續幾個月年增率>多少
				# print 'start to check ' + stockid.symbol + ' MonthRevenueContinuousAnnualGrowth'
				data = ''
				monthCnt = value['MonthCnt']
				MonthRevenueAnnualGrowth = value['MonthRevenueAnnualGrowth']
				revenues = MonthRevenue.objects.filter(symbol=stockid.symbol).order_by('-year', '-month')
				if monthCnt == '' or MonthRevenueAnnualGrowth == '':
					#print 'empty input to filter MonthRevenueContinuousAnnualGrowth'
					continue

				if len(revenues) >= int(monthCnt):
					for i in range(0, int(monthCnt)):
						if revenues[i].year_growth_rate < Decimal(MonthRevenueAnnualGrowth):
							passed = False
						data += str(revenues[i].year) + '-' + str(revenues[i].month) + '=' + str(revenues[i].year_growth_rate) + '%; '
					if passed:
						dataArr.append('[' + data + ']')
				else:
					passed = False
			elif key == 'SeasonOPM':
				# print 'start to check ' + stockid.symbol + ' OPM'
				SeasonCnt = value['SeasonCnt']
				SeasonOPM = value['SeasonOPM']
				OverUnder = value['OverUnder']
				ratios = SeasonFinancialRatio.objects.filter(symbol=stockid.symbol).order_by('-year','-season')
				dataList = [d.operating_profit_margin for d in ratios]
				data = checkData(dataList, SeasonCnt, OverUnder, SeasonOPM)
				#print 'get checkData return=' + data
				if data != '':
					dataArr.append('SeasonOPM=' + data)
				else:
					passed = False
			elif key == 'SeasonGPM':
				# print 'start to check ' + stockid.symbol + ' GPM'
				SeasonCnt = value['SeasonCnt']
				SeasonGPM = value['SeasonGPM']
				OverUnder = value['OverUnder']
				ratios = SeasonFinancialRatio.objects.filter(symbol=stockid.symbol).order_by('-year','-season')
				dataList = [d.gross_profit_margin for d in ratios]
				data = checkData(dataList, SeasonCnt, OverUnder, SeasonGPM)
				# print 'get GPM checkData return=' + data
				if data != '':
					dataArr.append('SeasonGPM=' + data)
				else:
					passed = False

		if passed:
			results[stockid.symbol] = ';'.join(dataArr)
			#print stockid.symbol
			print 'key=' + stockid.symbol + ', value=' + results[stockid.symbol]
			#print revenues[0].year
	return render_to_response(
				'filter/filter_result.html', {
				"results": results},
				context_instance = RequestContext(request))

	'''
	tradingDays = CorpTrade.objects.values_list('trade_date', flat=True).distinct()
	if tradingDays:
		for item in tradingDays:
			print item
	else:
		return HttpResponse('Query tradingDays empty')

	overBuyDays = 0
	if 'overBuyDays' in request.POST:
		overBuyDays = request.POST['overBuyDays']
	
	end_date = date.today()
	d = date.today() - timedelta(days=10)
	delta = timedelta(days=1)
	matches = {}
	while d <= end_date:
		print d.strftime("%Y-%m-%d")
		d += delta
		corpTrades = CorpTrade.objects.filter(trade_date = d.strftime("%Y%m%d")).filter(foreign_buy__gt=F('foreign_sell'))
		if corpTrades:
			for item in corpTrades:
				if matches.has_key(item.symbol) is False:
					matches[item.symbol] = 1
				else:
					matches[item.symbol] += 1
				#print item.symbol
		for key, value in matches.items():
			if value > 1:
				print(key + ' = ' + str(value))'''

def checkData(dataList, cnt, overunder, condition):
	passed = True
	data = ''
	if len(dataList) >= int(cnt):
		for i in range(0, int(cnt)):
			if overunder == 'over':
				if dataList[i] < Decimal(condition):
					passed = False
			else:
				if dataList[i] > Decimal(condition):
					passed = False
			data += str(dataList[i]) + '%; '
		if passed:
			return '[' + data + ']'
		else:
			return ''
	else:
		return ''


def daterange(start_date, end_date):
	for n in range(int ((end_date - start_date).days)):
		yield start_date + timedelta(n)

def getProfitabilityChart(request):
	data = {}
	symbol = getSymbol(request)
	if StockId.objects.filter(symbol=symbol):
		profitabilitys = SeasonFinancialRatio.objects.filter(symbol=symbol).order_by('surrogate_key')
		xAxis_categories = []
		gross_profit_margins = []
		operating_profit_margins = []
		net_before_tax_profit_margins = []
		net_after_tax_profit_margins = []
		for profitability in profitabilitys:
			xAxis_categories.append(str(profitability.year) + "Q" + str(profitability.season))
			gross_profit_margins.append(float(profitability.gross_profit_margin))
			operating_profit_margins.append(float(profitability.operating_profit_margin))
			net_before_tax_profit_margins.append(float(profitability.net_before_tax_profit_margin))
			net_after_tax_profit_margins.append(float(profitability.net_after_tax_profit_margin))
	names = [r'毛利率', r'營益率', r'稅前淨利率', r'稅後淨利率']
	totalProfitability = [gross_profit_margins, operating_profit_margins, net_before_tax_profit_margins, 
						  net_after_tax_profit_margins]
	data = {'categories': xAxis_categories, 'gross_profit_margins': gross_profit_margins, 
			'operating_profit_margins': operating_profit_margins, 
			'net_before_tax_profit_margins': net_before_tax_profit_margins,
			'net_after_tax_profit_margins': net_after_tax_profit_margins, 'names': names, 
			'totalProfitability': totalProfitability}
	return HttpResponse(json.dumps(data), content_type="application/json")
