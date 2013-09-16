# -*- coding: utf-8 -*-

from django.http import HttpResponse, Http404
from django.template.loader import get_template
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.template import Context
from stock_analysis.settings import STATIC_URL

from stocks.models import StockId, Revenue

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
			return HttpResponse(stockid + ' exists')
		else:
			return HttpResponse('error')

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
