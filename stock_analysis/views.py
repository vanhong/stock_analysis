# -*- coding: utf-8 -*-
import json
from decimal import *
from django.http import HttpResponse, Http404
from django.template.loader import get_template
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.template import Context
from stock_analysis.settings import STATIC_URL

from stocks.models import StockId, MonthRevenue, Dividend

def test(request):
	return render_to_response('test.html', context_instance = RequestContext(request))

def testStockid(request):
	return render_to_response('analysis/testStockid.html', context_instance = RequestContext(request))

def site(request):
	return render_to_response('site.html', context_instance = RequestContext(request))

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
			return HttpResponse('')
			return render_to_response('analysis/index.html', {"stock_id": name}, 
									  context_instance = RequestContext(request))
		else:
			return HttpResponse('stockid error')

def dividend(request):
	symbol = request.session['stock_id']
	stockname = StockId.objects.get(symbol=symbol)
	dividend_head = []
	dividend_head.append(r'年度')
	dividend_head.append(r'現金股利')
	dividend_head.append(r'盈餘配股')
	dividend_head.append(r'公積配股')
	dividend_head.append(r'股票股利')
	dividend_head.append(r'合計')
	dividend_head.append(r'員工配股率%')
	dividend_body = []
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
				dividend_body.append(item)
			name = stockname.name.encode('utf-8') + '(' + str(symbol) + ')'
			return render_to_response(
				'analysis/dividend.html', {"stock_id": name, "dividend_head": dividend_head,
				"dividend_body": dividend_body},
				context_instance = RequestContext(request))
	return render_to_response(
		'analysis/dividend.html',{"stock_id": request.session["stock_id"]},
		context_instance = RequestContext(request))

def month_revenue(request):
	symbol = request.session['stock_id']
	stockname = StockId.objects.get(symbol=symbol)
	revenue_title = r'月營收明細'
	revenue_head = []
	revenue_head.append(r'年/月')
	revenue_head.append(r'營收(仟元)')
	revenue_head.append(r'月增率')
	revenue_head.append(r'去年同期(仟元)')
	revenue_head.append(r'年增率')
	revenue_head.append(r'累計營收(仟元)')
	revenue_head.append(r'年增率')
	revenue_body = []
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
				revenue_body.append(item)

			name = stockname.name.encode('utf-8') + '(' + str(symbol) + ')'
			return render_to_response(
				'analysis/revenue.html', {"stock_id": name, "revenue_title": revenue_title,
				"revenue_head": revenue_head, "revenue_body": revenue_body},
				context_instance = RequestContext(request))
	return render_to_response(
		'analysis/index.html',{"stock_id": request.session["stock_id"]},
		context_instance = RequestContext(request))

def season_revenue(request):
	symbol = request.session['stock_id']
	stockname = StockId.objects.get(symbol=symbol)
	revenue_title = r'季盈餘明細'
	revenue_head = []
	revenue_head.append(r'年/季')
	revenue_head.append(r'稅後盈餘(仟元)')
	revenue_head.append(r'季增率')
	revenue_head.append(r'去年同期(仟元)')
	revenue_head.append(r'年增率')
	revenue_head.append(r'累計盈餘(仟元)')
	revenue_head.append(r'年增率')
	revenue_body = []
	if StockId.objects.filter(symbol=symbol):
		season_revenues = SeasonRevenue.objects.filter(symbol=symbol).order_by('-surrogate_key')
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
				revenue_body.append(item)
			name = stockname.name.encode('utf-8') + '(' + str(symbol) + ')'
			return render_to_response(
				'analysis/revenue.html', {
				"stock_id": name, "revenue_title": revenue_title,
				"revenue_head": revenue_head, "revenue_body": revenue_body},
				context_instance = RequestContext(request))
	return render_to_response(
		'analysis/index.html', {"stock_id": request.session["stock_id"]},
		context_instance = RequestContext(request))

def filter(request):
	symbol = request.session['stock_id']

def ajax_user_search(request):
	q = request.GET.get('q')
	if q is not None:
		return HttpResponse('ajax_usr_search ' + q)

def index(request):
	return HttpResponse('index')

def getRevenueChart(request):
	symbol = request.session['stock_id']
	if not symbol:
		symbol = '8114'
	if StockId.objects.filter(symbol=symbol):
		month_revenues = MonthRevenue.objects.filter(symbol=symbol).order_by('surrogate_key')
		revenue_data = []
		growth_rate_data = []
		xAxis_categories = []
		for revenue in month_revenues:
			if revenue.revenue is not None and revenue.year_growth_rate is not None:
				revenue_data.append(int(revenue.revenue))
				growth_rate_data.append(float(revenue.year_growth_rate))
				xAxis_categories.append(str(revenue.year) + '/' + str(revenue.month).zfill(2))
	data = {'revenue' : revenue_data, 'growth_rate' : growth_rate_data, 'categories' : xAxis_categories}
	
	return HttpResponse(json.dumps(data), content_type="application/json")
