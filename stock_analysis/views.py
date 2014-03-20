# -*- coding: utf-8 -*-

import json
from decimal import *
from django.http import HttpResponse, Http404
from django.template.loader import get_template
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.template import Context
from django.db.models import Count
from stock_analysis.settings import STATIC_URL

from stocks.models import StockId, MonthRevenue, Dividend, SeasonProfit, SeasonRevenue
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from financial.models import SeasonFinancialRatio, YearFinancialRatio

def venue(request):
	return render_to_response('analysis/test_auto.html', context_instance = RequestContext(request))

def venue_lookup(request):
	print request.GET['term']
	venues = StockId.objects.filter(symbol__startswith=request.GET['term'])
	results = []
	for venue in venues:
		venue_dict = {'id':venue.symbol, 'label':venue.name, 'value':venue.name}
		results.append(venue_dict)
	return HttpResponse(json.dumps(results), content_type='application/json')

def home(request):
	return render_to_response('home/index.html', context_instance = RequestContext(request))

def analysis(request, template_name, drawTool):
	url = request.path.replace('/','')
	return render_to_response('analysis/' + template_name, {'drawTool': drawTool, 'url':url},
							  context_instance = RequestContext(request))
@csrf_exempt
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

def get_symbol(request):
	try:
		symbol = request.session['stock_id']
	except:
		symbol = '2330'
	return symbol

#經營績效
@csrf_exempt
def get_performance_per_share_table(request):
	if 'time_type' in request.POST:
		time_type = request.POST['time_type']
	if time_type == 'season':
		ratio_model = SeasonFinancialRatio
	elif time_type == 'year':
		ratio_model = YearFinancialRatio
	symbol = get_symbol(request)
	stockname = StockId.objects.get(symbol=symbol)
	heads = []
	if time_type == 'year':
		heads.append(r'年度')
		ratio_model = YearFinancialRatio
	elif time_type == 'season':
		heads.append(r'年/季')
		ratio_model = SeasonFinancialRatio
	heads.append(r'每股稅前盈餘')
	heads.append(r'每股稅後盈餘')
	bodys = []
	if StockId.objects.filter(symbol=symbol):
		ratios = ratio_model.objects.filter(symbol=symbol).order_by('-date')
		if ratios:
			for ratio in ratios:
				item = []
				if ratio.net_before_tax_profit_per_share is not None and ratio.net_after_tax_profit_per_share is not None:
					if time_type == 'year':
						item.append(ratio.year)
					elif time_type == 'season':
						item.append(str(ratio.year) + 'Q' + str(ratio.season))
					item.append(ratio.net_before_tax_profit_per_share)
					item.append(ratio.net_after_tax_profit_per_share)
					bodys.append(item)
			name = stockname.name.encode('utf-8') + '(' + str(symbol) + ')'
			return render_to_response(
				'analysis/analysis_table.html', {"stock_id": name, "heads": heads,
				"bodys": bodys}, context_instance = RequestContext(request))
	return render_to_response(
		'analysis/analysis_table.html',{"stock_id": get_symbol(request)},
		context_instance = RequestContext(request))

def get_dividend_table(request):
	symbol = get_symbol(request)
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
		dividends = Dividend.objects.filter(symbol=symbol).order_by('-date')
		if dividends:
			for dividend in dividends:
				if dividend.cash_dividends:
					if dividend.cash_dividends is not None and dividend.stock_dividends is not None:
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
		'analysis/analysis_table.html',{"stock_id": get_symbol(request)},
		context_instance = RequestContext(request))

@csrf_exempt
def get_profitability_table(request):
	if 'time_type' in request.POST:
		time_type = request.POST['time_type']
		heads = []
	if time_type == 'season':
		ratio_model = SeasonFinancialRatio
		heads.append(r'季度')
	elif time_type == 'year':
		ratio_model = YearFinancialRatio
		heads.append(r'年度')
	symbol = get_symbol(request)
	stockname = StockId.objects.get(symbol=symbol)
	heads.append(r'毛利率')
	heads.append(r'營益率')
	heads.append(r'稅前盈益率')
	heads.append(r'稅後盈利率')
	bodys = []
	if StockId.objects.filter(symbol=symbol):
		season_profitabilitys = SeasonFinancialRatio.objects.filter(symbol=symbol).order_by('-date')
		if season_profitabilitys:
			for profitability in season_profitabilitys:
				if profitability.gross_profit_margin is not None and profitability.operating_profit_margin  is not None and\
				   profitability.net_before_tax_profit_margin is not None and profitability.net_after_tax_profit_margin is not None:
					item = []
					if time_type == 'season':
						item.append(str(profitability.year)+'Q'+str(profitability.season))
					elif time_type == 'year':
						item.append(profitability.year)
					item.append(profitability.gross_profit_margin)
					item.append(profitability.operating_profit_margin)
					item.append(profitability.net_before_tax_profit_margin)
					item.append(profitability.net_after_tax_profit_margin)
					bodys.append(item)
			name = stockname.name.encode('utf-8') + '(' + str(symbol) + ')'
			return render_to_response(
				'analysis/analysis_table.html', {"stock_id": name,
				"heads": heads, "bodys": bodys},
				context_instance = RequestContext(request))
	return render_to_response(
		'analysis/analysis_table.html',{"stock_id": symbol},
		context_instance = RequestContext(request))

def get_month_revenue_table(request):
	symbol = get_symbol(request)
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
		month_revenues = MonthRevenue.objects.filter(symbol=symbol).order_by('-date')
		if month_revenues:
			for revenue in month_revenues:
				if revenue.month:
					if revenue.revenue is not None:
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

def get_season_revenue_table(request):
	symbol = get_symbol(request)
	stockname = StockId.objects.get(symbol=symbol)
	heads = []
	heads.append(r'年/季')
	heads.append(r'營收(仟元)')
	heads.append(r'季增率')
	heads.append(r'去年同期(仟元)')
	heads.append(r'年增率')
	heads.append(r'累計營收(仟元)')
	heads.append(r'年增率')
	bodys = []
	if StockId.objects.filter(symbol=symbol):
		season_revenues = SeasonRevenue.objects.filter(symbol=symbol).order_by('-date')
		if season_revenues:
			for revenue in season_revenues:
				if revenue.revenue is not None:
					item = []
					item.append(str(revenue.year)+r'/'+str(revenue.season))
					item.append(revenue.revenue)
					item.append(revenue.season_growth_rate)
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

def get_season_profit_table(request):
	symbol = get_symbol(request)
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
		season_revenues = SeasonProfit.objects.filter(symbol=symbol).order_by('-date')
		if season_revenues:
			for revenue in season_revenues:
				if revenue.profit is not None:
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

@csrf_exempt
def get_roe_roa_table(request):
	if 'time_type' in request.POST:
		time_type = request.POST['time_type']
		heads = []
	if time_type == 'season':
		ratio_model = SeasonFinancialRatio
		heads.append(r'季度')
	elif time_type == 'year':
		ratio_model = YearFinancialRatio
		heads.append(r'年')
	symbol = get_symbol(request)
	stockname = StockId.objects.get(symbol=symbol)
	heads.append(r'股東權益報酬率')
	heads.append(r'資產報酬率')
	bodys = []
	if StockId.objects.filter(symbol=symbol):
		ratios = ratio_model.objects.filter(symbol=symbol).order_by('-date')
		if ratios:
			for ratio in ratios:
				if ratio.return_on_equity is not None and ratio.return_on_assets is not None:
					item = []
					if time_type == 'year':
						item.append(ratio.year)
					elif time_type == 'season':
						item.append(str(ratio.year) + 'Q' + str(ratio.season))
					item.append(ratio.return_on_equity)
					item.append(ratio.return_on_assets)
					bodys.append(item)
			name = stockname.name.encode('utf-8') + '(' + str(symbol) + ')'
			return render_to_response(
				'analysis/analysis_table.html', {"stock_id": name, "heads": heads,
				"bodys": bodys},
				context_instance = RequestContext(request))
	return render_to_response(
		'analysis/analysis_table.html',{"stock_id": get_symbol(request)},
		context_instance = RequestContext(request))

@csrf_exempt
def get_interest_cover_table(request):
	if 'time_type' in request.POST:
		time_type = request.POST['time_type']
		heads = []
	if time_type == 'season':
		ratio_model = SeasonFinancialRatio
		heads.append(r'季度')
	elif time_type == 'year':
		ratio_model = YearFinancialRatio
		heads.append(r'年')
	symbol = get_symbol(request)
	stockname = StockId.objects.get(symbol=symbol)
	heads.append(r'利息保障倍數')
	bodys = []
	if StockId.objects.filter(symbol=symbol):
		ratios = ratio_model.objects.filter(symbol=symbol).order_by('-date')
		if ratios:
			for ratio in ratios:
				if ratio.interest_cover is not None:
					item = []
					if time_type == 'year':
						item.append(ratio.year)
					elif time_type == 'season':
						item.append(str(ratio.year) + 'Q' + str(ratio.season))
					item.append(ratio.interest_cover)
					bodys.append(item)
			name = stockname.name.encode('utf-8') + '(' + str(symbol) + ')'
			return render_to_response(
				'analysis/analysis_table.html', {"stock_id": name, "heads": heads,
				"bodys": bodys},
				context_instance = RequestContext(request))
	return render_to_response(
		'analysis/analysis_table.html',{"stock_id": get_symbol(request)},
		context_instance = RequestContext(request))

@csrf_exempt
def get_growth_rate_table(request):
	if 'time_type' in request.POST and 'field' in request.POST:
		time_type = request.POST['time_type']
		field = request.POST['field']
		heads = []
	if time_type == 'season':
		ratio_model = SeasonFinancialRatio
		heads.append(r'季度')
	elif time_type == 'year':
		ratio_model = YearFinancialRatio
		heads.append(r'年')
	symbol = get_symbol(request)
	stockname = StockId.objects.get(symbol=symbol)
	model = ratio_model()
	heads.append(model.chinese(field))
	bodys = []
	if StockId.objects.filter(symbol=symbol):
		ratios = ratio_model.objects.filter(symbol=symbol).order_by('-date')
		if ratios:
			for ratio in ratios:
				if ratio.__dict__[field] is not None:
					item = []
					if time_type == 'year':
						item.append(ratio.__dict__[field])
					elif time_type == 'season':
						item.append(str(ratio.year) + 'Q' + str(ratio.season))
					# item.append(ratio.revenue_growth_rate)
					item.append(ratio.__dict__[field])
					bodys.append(item)
			name = stockname.name.encode('utf-8') + '(' + str(symbol) + ')'
			return render_to_response(
				'analysis/analysis_table.html', {"stock_id": name, "heads": heads,
				"bodys": bodys},
				context_instance = RequestContext(request))
	return render_to_response(
		'analysis/analysis_table.html',{"stock_id": get_symbol(request)},
		context_instance = RequestContext(request))

@csrf_exempt
def get_turnover_ratio_table(request):
	if 'time_type' in request.POST:
		time_type = request.POST['time_type']
		heads = []
	if time_type == 'season':
		ratio_model = SeasonFinancialRatio
		heads.append(r'季度')
	elif time_type == 'year':
		ratio_model = YearFinancialRatio
		heads.append(r'年')
	symbol = get_symbol(request)
	stockname = StockId.objects.get(symbol=symbol)
	heads.append(r'應收帳款週轉率(次)')
	heads.append(r'存貨週轉率(次)')
	heads.append(r'固定資產週轉率(次)')
	heads.append(r'總資產週轉率(次)')
	bodys = []
	if StockId.objects.filter(symbol=symbol):
		ratios = ratio_model.objects.filter(symbol=symbol).order_by('-date')
		if ratios:
			for ratio in ratios:
				if ratio.account_receivable_turnover_ratio is not None and ratio.inventory_turnover_ratio is not None and\
				   ratio.fixed_assets_turnover_ratio is not None and ratio.assets_turnover_ratio is not None:
					item = []
					if time_type == 'season':
						item.append(str(ratio.year) + 'Q' + str(ratio.season))
					elif time_type == 'year':
						item.append(str(ratio.year))
					item.append(ratio.account_receivable_turnover_ratio)
					item.append(ratio.inventory_turnover_ratio)
					item.append(ratio.fixed_assets_turnover_ratio)
					item.append(ratio.assets_turnover_ratio)
					bodys.append(item)
			name = stockname.name.encode('utf-8') + '(' + str(symbol) + ')'
			return render_to_response(
				'analysis/analysis_table.html', {'stock_id': name, 'heads':heads,
				'bodys': bodys}, context_instance = RequestContext(request))
	return render_to_response(
		'analysis/analysis_table.html', {'stock_id': get_symbol(request), 'heads':heads,
		'bodys': bodys}, context_instance = RequestContext(request))

@csrf_exempt
def get_current_ratio_table(request):
	if 'time_type' in request.POST:
		time_type = request.POST['time_type']
		heads = []
	if time_type == 'season':
		ratio_model = SeasonFinancialRatio
		heads.append(r'季度')
	elif time_type == 'year':
		ratio_model = YearFinancialRatio
		heads.append(r'年')
	symbol = get_symbol(request)
	stockname = StockId.objects.get(symbol=symbol)
	heads.append(r'流動比')
	heads.append(r'速動比')
	bodys = []
	if StockId.objects.filter(symbol=symbol):
		ratios = ratio_model.objects.filter(symbol=symbol).order_by('-date')
		if ratios:
			for ratio in ratios:
				if ratio.current_ratio is not None and ratio.quick_ratio is not None:
					item = []
					if time_type == 'season':
						item.append(str(ratio.year) + 'Q' + str(ratio.season))
					elif time_type == 'year':
						item.append(ratio.year)
					item.append(ratio.current_ratio)
					item.append(ratio.quick_ratio)
					bodys.append(item)
			name = stockname.name.encode('utf-8') + '(' + str(symbol) + ')'
			return render_to_response(
				'analysis/analysis_table.html', {'stock_id': name, 'heads':heads,
				'bodys': bodys}, context_instance = RequestContext(request))
	return render_to_response(
		'analysis/analysis_table.html', {'stock_id': get_symbol(request), 'heads':heads,
		'bodys': bodys}, context_instance = RequestContext(request))

@csrf_exempt
def get_debt_ratio_table(request):
	if 'time_type' in request.POST:
		time_type = request.POST['time_type']
		heads = []
	if time_type == 'season':
		ratio_model = SeasonFinancialRatio
		heads.append(r'年/季')
	elif time_type == 'year':
		ratio_model = YearFinancialRatio
		heads.append(r'年')
	symbol = get_symbol(request)
	stockname = StockId.objects.get(symbol=symbol)
	heads.append(r'負債比率')
	bodys = []
	if StockId.objects.filter(symbol=symbol):
		ratios = ratio_model.objects.filter(symbol=symbol).order_by('-date')
		if ratios:
			for ratio in ratios:
				if ratio.debt_ratio is not None:
					item = []
					if time_type == 'season':
						item.append(str(ratio.year) + 'Q' + str(ratio.season))
					elif time_type == 'year':
						item.append(ratio.year)
					item.append(ratio.debt_ratio)
					bodys.append(item)
			name = stockname.name.encode('utf-8') + '(' + str(symbol) + ')'
			return render_to_response(
				'analysis/analysis_table.html', {'stock_id': name, 'heads':heads,
				'bodys': bodys}, context_instance = RequestContext(request))
	return render_to_response(
		'analysis/analysis_table.html', {'stock_id': get_symbol(request), 'heads':heads,
		'bodys': bodys}, context_instance = RequestContext(request))

def get_season_revenue_chart(request):
	symbol = get_symbol(request)
	maxRevenue = 0
	maxGrowthRate = -100
	minGrowthRate = 10000
	dataNum = 0
	if StockId.objects.filter(symbol=symbol):
		season_revenues = SeasonRevenue.objects.filter(symbol=symbol).order_by('date')
		revenue_data = []
		growth_rate_data = []
		xAxis_categories = []
		for revenue in season_revenues:
			if revenue.revenue is not None and revenue.year_growth_rate is not None:
				int_season_revenue = int(revenue.revenue)
				if int_season_revenue > maxRevenue:
					maxRevenue = int_season_revenue
				revenue_data.append(int_season_revenue)
				float_year_growth_rate = float(revenue.year_growth_rate)
				if float_year_growth_rate > maxGrowthRate:
					maxGrowthRate = float_year_growth_rate
				if float_year_growth_rate < minGrowthRate:
					minGrowthRate = float_year_growth_rate
				growth_rate_data.append(float_year_growth_rate)
				xAxis_categories.append(str(revenue.year) + 'Q' + str(revenue.season))
		if len(revenue_data) > 24:
			dataNum = 24
		else:
			dataNum = len(revenue_data)
	data = {'revenue' : revenue_data, 'growth_rate': growth_rate_data, 'categories' : xAxis_categories,
			'maxRevenue': maxRevenue, 'maxGrowthRate' : maxGrowthRate, 'minGrowthRate': minGrowthRate,
			'dataNum' : dataNum}
	return HttpResponse(json.dumps(data), content_type="application/json")

def get_season_profit_chart(request):
	symbol = get_symbol(request)
	maxProfit = 0
	maxGrowthRate = -100
	minGrowthRate = 10000
	dataNum = 0
	if StockId.objects.filter(symbol=symbol):
		season_profits = SeasonProfit.objects.filter(symbol=symbol).order_by('date')
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

def get_month_revenue_chart(request):
	symbol = get_symbol(request)
	maxRevenue = 0
	maxGrowthRate = -100
	minGrowthRate = 10000
	dataNum = 0
	if StockId.objects.filter(symbol=symbol):
		month_revenues = MonthRevenue.objects.filter(symbol=symbol).order_by('date')
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

def get_dividend_chart(request):
	data = {}
	symbol = get_symbol(request)
	if StockId.objects.filter(symbol=symbol):
		dividends = Dividend.objects.filter(symbol=symbol).order_by('-year')[0:10]
		xAxis_categories = []
		cash_dividends = []
		stock_dividends = []
		for dividend in dividends:
			if dividend.cash_dividends is not None and dividend.stock_dividends is not None:
				xAxis_categories.append(str(dividend.year))
				cash_dividends.append(round(float(dividend.cash_dividends), 2))
				stock_dividends.append(round(float(dividend.stock_dividends), 2))
	data = {'categories': xAxis_categories[::-1], 'cash_dividends': cash_dividends[::-1], 'stock_dividends': stock_dividends[::-1]}
	return HttpResponse(json.dumps(data), content_type="application/json")

def get_performance_per_share_chart(request):
	if 'time_type' in request.GET:
		time_type = request.GET['time_type']
	data = {}
	symbol = get_symbol(request)
	if time_type == 'year':
		ratio_model = YearFinancialRatio
	elif time_type == 'season':
		ratio_model = SeasonFinancialRatio
	if StockId.objects.filter(symbol=symbol):
		season_financial_ratios = ratio_model.objects.filter(symbol=symbol).order_by('date')
		xAxis_categories = []
		net_before_tax_profit_per_shares = []
		net_after_tax_profit_per_shares = []
		for ratio in season_financial_ratios:
			if ratio.net_before_tax_profit_per_share is not None and ratio.net_after_tax_profit_per_share is not None:
				if time_type == 'year':
					xAxis_categories.append(ratio.year)
				elif time_type == 'season':
					xAxis_categories.append(str(ratio.year) + "Q" + str(ratio.season))
				net_before_tax_profit_per_shares.append(float(ratio.net_before_tax_profit_per_share))
				net_after_tax_profit_per_shares.append(float(ratio.net_after_tax_profit_per_share))
	names = [r'稅前每股盈餘', r'稅後每股盈餘']
	datas = [net_before_tax_profit_per_shares, net_after_tax_profit_per_shares]
	yUnit = '元'
	data = {'categories': xAxis_categories, 'names': names, 'datas': datas, 'yUnit': yUnit}
	return HttpResponse(json.dumps(data), content_type="application/json")

def get_roe_roa_chart(request):
	if 'time_type' in request.GET:
		time_type = request.GET['time_type']
	if time_type == 'year':
		ratio_model = YearFinancialRatio
	elif time_type == 'season':
		ratio_model = SeasonFinancialRatio
	data = {}
	symbol = get_symbol(request)
	if StockId.objects.filter(symbol=symbol):
		season_financial_ratios = ratio_model.objects.filter(symbol=symbol).order_by('date')
		xAxis_categories = []
		return_on_equity = []
		return_on_assets = []
		for ratio in season_financial_ratios:
			if ratio.return_on_equity is not None and ratio.return_on_assets is not None:
				if time_type == 'year':
					xAxis_categories.append(ratio.year)
				elif time_type == 'season':
					xAxis_categories.append(str(ratio.year) + "Q" + str(ratio.season))
				return_on_equity.append(float(ratio.return_on_equity))
				return_on_assets.append(float(ratio.return_on_assets))
	names = [r'股東權益報酬率', r'資產報酬率']
	datas = [return_on_equity, return_on_assets]
	yUnit = '%'
	data = {'categories': xAxis_categories, 'names': names, 'datas': datas, 'yUnit': yUnit}
	return HttpResponse(json.dumps(data), content_type="application/json")

def get_turnover_ratio_chart(request):
	if 'time_type' in request.GET:
		time_type = request.GET['time_type']
	if time_type == 'year':
		ratio_model = YearFinancialRatio
	elif time_type == 'season':
		ratio_model = SeasonFinancialRatio
	data = {}
	symbol = get_symbol(request)
	if StockId.objects.filter(symbol=symbol):
		season_financial_ratios = ratio_model.objects.filter(symbol=symbol).order_by('date')
		xAxis_categories = []
		account_receivable_turnover_ratios = []
		inventory_turnover_ratios = []
		fixed_assets_turnover_ratios = []
		assets_turnover_ratios = []
		for ratio in season_financial_ratios:
			if ratio.account_receivable_turnover_ratio is not None and ratio.inventory_turnover_ratio is not None and\
			   ratio.fixed_assets_turnover_ratio is not None and ratio.assets_turnover_ratio is not None:
				if time_type == 'year':
					xAxis_categories.append(ratio.year)
				elif time_type == 'season':
					xAxis_categories.append(str(ratio.year) + "Q" + str(ratio.season))
				account_receivable_turnover_ratios.append(float(ratio.account_receivable_turnover_ratio))
				inventory_turnover_ratios.append(float(ratio.inventory_turnover_ratio))
				fixed_assets_turnover_ratios.append(float(ratio.fixed_assets_turnover_ratio))
				assets_turnover_ratios.append(float(ratio.assets_turnover_ratio))
	names = [r'應收帳款週轉率(次)', r'存貨週轉率(次)', r'固定資產週轉率(次)', r'總資產週轉率(次)']
	datas = [account_receivable_turnover_ratios, inventory_turnover_ratios, \
			 fixed_assets_turnover_ratios, assets_turnover_ratios]
	yUnit = '%'
	data = {'categories': xAxis_categories, 'names': names, 'datas': datas, 'yUnit': yUnit}
	return HttpResponse(json.dumps(data), content_type="application/json")

def get_profitability_chart(request):
	if 'time_type' in request.GET:
		time_type = request.GET['time_type']
	if time_type == 'season':
		ratio_model = SeasonFinancialRatio
	elif time_type == 'year':
		ratio_model = YearFinancialRatio
	data = {}
	symbol = get_symbol(request)
	if StockId.objects.filter(symbol=symbol):
		profitabilitys = ratio_model.objects.filter(symbol=symbol).order_by('date')
		xAxis_categories = []
		gross_profit_margins = []
		operating_profit_margins = []
		net_before_tax_profit_margins = []
		net_after_tax_profit_margins = []
		for profitability in profitabilitys:
			if profitability.gross_profit_margin is not None and profitability.operating_profit_margin is not None and \
			   profitability.net_before_tax_profit_margin is not None and profitability.net_after_tax_profit_margin is not None:
				if time_type == 'season':
					xAxis_categories.append(str(profitability.year) + "Q" + str(profitability.season))
				elif time_type == 'year':
					xAxis_categories.append(profitability.year)
				gross_profit_margins.append(float(profitability.gross_profit_margin))
				operating_profit_margins.append(float(profitability.operating_profit_margin))
				net_before_tax_profit_margins.append(float(profitability.net_before_tax_profit_margin))
				net_after_tax_profit_margins.append(float(profitability.net_after_tax_profit_margin))
	names = [r'毛利率', r'營益率', r'稅前淨利率', r'稅後淨利率']
	datas = [gross_profit_margins, operating_profit_margins, net_before_tax_profit_margins, 
						  net_after_tax_profit_margins]
	yUnit = '%'
	data = {'categories': xAxis_categories, 'names': names, 'datas': datas, 'yUnit': yUnit}
	return HttpResponse(json.dumps(data), content_type="application/json")

def get_current_ratio_chart(request):
	if 'time_type' in request.GET:
		time_type = request.GET['time_type']
	if time_type == 'season':
		ratio_model = SeasonFinancialRatio
	elif time_type == 'year':
		ratio_model = YearFinancialRatio
	data = {}
	symbol = get_symbol(request)
	if StockId.objects.filter(symbol=symbol):
		ratios = ratio_model.objects.filter(symbol=symbol).order_by('date')
		xAxis_categories = []
		current_ratios = []
		quick_ratios = []
		for ratio in ratios:
			if ratio.current_ratio is not None and ratio.quick_ratio is not None:
				if time_type == 'season':
					xAxis_categories.append(str(ratio.year) + 'Q' + str(ratio.season))
				elif time_type == 'year':
					xAxis_categories.append(ratio.year)
				current_ratios.append(float(ratio.current_ratio))
				quick_ratios.append(float(ratio.quick_ratio))
	names = [r'流動比', r'速動比']
	datas = [current_ratios, quick_ratios]
	yUnit = '倍'
	data = {'categories': xAxis_categories, 'names': names, 'datas': datas, 'yUnit': yUnit}
	return HttpResponse(json.dumps(data), content_type="application/json")

def get_debt_ratio_chart(request):
	if 'time_type' in request.GET:
		time_type = request.GET['time_type']
	if time_type == 'season':
		ratio_model = SeasonFinancialRatio
	elif time_type == 'year':
		ratio_model = YearFinancialRatio
	date = {}
	symbol = get_symbol(request)
	if StockId.objects.filter(symbol=symbol):
		ratios = ratio_model.objects.filter(symbol=symbol).order_by('date')
		xAxis_categories = []
		debt_ratios = []
		for ratio in ratios:
			if ratio.debt_ratio is not None:
				if time_type == 'season':
					xAxis_categories.append(str(ratio.year) + 'Q' + str(ratio.season))
				elif time_type == 'year':
					xAxis_categories.append(ratio.year)
				debt_ratios.append(float(ratio.debt_ratio))
	names = [r'負債比率']
	datas = [debt_ratios]
	yUnit = '%'
	data = {'categories': xAxis_categories, 'names': names, 'datas': datas, 'yUnit': yUnit}
	return HttpResponse(json.dumps(data), content_type="application/json")

def get_growth_rate_chart(request):
	if 'time_type' in request.GET and 'field' in request.GET:
		time_type = request.GET['time_type']
		field = request.GET['field']
	if time_type == 'season':
		ratio_model = SeasonFinancialRatio
	elif time_type == 'year':
		ratio_model = YearFinancialRatio
	date = {}
	symbol = get_symbol(request)
	if StockId.objects.filter(symbol=symbol):
		ratios = ratio_model.objects.filter(symbol=symbol).order_by('date')
		xAxis_categories = []
		debt_ratios = []
		for ratio in ratios:
			if ratio.__dict__[field] is not None:
				if time_type == 'season':
					xAxis_categories.append(str(ratio.year) + 'Q' + str(ratio.season))
				elif time_type == 'year':
					xAxis_categories.append(ratio.year)
				debt_ratios.append(float(ratio.__dict__[field]))
	model = ratio_model()
	names = [model.chinese(field)]
	datas = [debt_ratios]
	yUnit = '%'
	data = {'categories': xAxis_categories, 'names': names, 'datas': datas, 'yUnit': yUnit}
	return HttpResponse(json.dumps(data), content_type="application/json")

def get_interest_cover_chart(request):
	if 'time_type' in request.GET:
		time_type = request.GET['time_type']
	if time_type == 'season':
		ratio_model = SeasonFinancialRatio
	elif time_type == 'year':
		ratio_model = YearFinancialRatio
	date = {}
	symbol = get_symbol(request)
	if StockId.objects.filter(symbol=symbol):
		ratios = ratio_model.objects.filter(symbol=symbol).order_by('date')
		xAxis_categories = []
		debt_ratios = []
		for ratio in ratios:
			if ratio.interest_cover is not None:
				if time_type == 'season':
					xAxis_categories.append(str(ratio.year) + 'Q' + str(ratio.season))
				elif time_type == 'year':
					xAxis_categories.append(ratio.year)
				debt_ratios.append(float(ratio.interest_cover))
	names = [r'利息保障倍數']
	datas = [debt_ratios]
	yUnit = '倍'
	data = {'categories': xAxis_categories, 'names': names, 'datas': datas, 'yUnit': yUnit}
	return HttpResponse(json.dumps(data), content_type="application/json")
