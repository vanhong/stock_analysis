# -*- coding: utf-8 -*-
import json
from django.http import HttpResponse, Http404
from django.template.loader import get_template
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.template import Context
from stock_analysis.settings import STATIC_URL

from stocks.models import StockId, MonthRevenue

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
			return month_revenue(request)
		else:
			return HttpResponse('stockid error')

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

def test2(request):
	return render_to_response('test2.html', context_instance = RequestContext(request))

def getJSON(request):
	print('in getJSON')
	tokyo = ChartData('Tokyo', [7.0, 6.9, 9.5, 14.5, 18.2, 21.5, 25.2, 26.5, 23.3, 18.3, 13.9, 9.6])
	newyork = ChartData('NewYork', [-0.2, 0.8, 5.7, 11.3, 17.0, 22.0, 24.8, 24.1, 20.1, 14.1, 8.6, 2.5])
	data = []
	data.append(tokyo.__toDict__())
	data.append(newyork.__toDict__())
	'''resDataList = []
	resData = ChartData('Tokyo', [7.0, 6.9, 9.5, 14.5, 18.2, 21.5, 25.2, 26.5, 23.3, 18.3, 13.9, 9.6])
	resDataList.append(resData)
	resData2 = ChartData('NewYork',[-0.2, 0.8, 5.7, 11.3, 17.0, 22.0, 24.8, 24.1, 20.1, 14.1, 8.6, 2.5])
	resDataList.append(resData2)'''
	response_data = {'Tokyo' :  [7.0, 6.9, 9.5, 14.5, 18.2, 21.5, 25.2, 26.5, 23.3, 18.3, 13.9, 9.6],
					'NewYork' : [-0.2, 0.8, 5.7, 11.3, 17.0, 22.0, 24.8, 24.1, 20.1, 14.1, 8.6, 2.5]}
	data2 = {'series' :[{ 'name' : 'Rainfall', 'color': '#4572A7','type': 'column','yAxis': 1,
              'data': [49.9, 71.5, 106.4, 129.2, 144.0, 176.0, 135.6, 148.5, 216.4, 194.1, 95.6, 54.4],
              'tooltip' : { 'valueSuffix' : ' mm'} },
			{ 'name' : 'Rainfall','color': '#89A54E', 'type': 'spline',
              'data': [7.0, 6.9, 9.5, 14.5, 18.2, 21.5, 25.2, 26.5, 23.3, 18.3, 13.9, 9.6],
              'tooltip': { 'valueSuffix': 'C' } }]}
	data3 = {
		'name' : 'Rainfall',
		'color': '#89A54E',
        'type': 'spline',
        'data': [7.0, 6.9, 9.5, 14.5, 18.2, 21.5, 25.2, 26.5, 23.3, 18.3, 13.9, 9.6],
        'tooltip': { 'valueSuffix': 'C' }
	}
	data4 = []
	d = ChartData('name', 'Rainfall')
	data4.append(d.__toDict__())
	d = ChartData('color', '#89A54E')
	data4.append(d.__toDict__())
	d = ChartData('type', 'spline')
	data4.append(d.__toDict__())
	d = ChartData('data', [7.0, 6.9, 9.5, 14.5, 18.2, 21.5, 25.2, 26.5, 23.3, 18.3, 13.9, 9.6])
	data4.append(d.__toDict__())
	d = ChartData('tooltip', { 'valueSuffix': 'C' })
	data4.append(d.__toDict__())
	st = "zoomType: 'xy' "
	print st
	data5 = []
	d1 = {'name' : 'Tokyo', 'data' : [7.0, 6.9, 9.5, 14.5, 18.2, 21.5, 25.2, 26.5, 23.3, 18.3, 13.9, 9.6]}
	d2 = {'name' : 'NewYork', 'data' : [-0.2, 0.8, 5.7, 11.3, 17.0, 22.0, 24.8, 24.1, 20.1, 14.1, 8.6, 2.5]}
	d3 = []
	d3.append(d1)
	d3.append(d2)
	d5 = {'series': d3}
	print d5

	d11 = {'chart' : "zoomType : 'xy'"}
	d11['subtitle'] = {'text' : 'Source: WorldClimate.com'}
	d11['title'] = {'text': 'Average Monthly Temperature and Rainfall in Tokyo'}
	d11['xAxis'] = [{'categories': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
					'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']}]
	d21 = {'style' : {'color':'#89A54E'}}
	d22 = {'format' : '{value}C'}
	d23 = {'style' : {'color':'#89A54E'}}
	d11['style'] = d23['style']
	d11['chart2'] = {'chart' : {'zoomType' : 'xy'}}

	d11['format'] = '{value}C'
	#response_data['Tokyo'] = [7.0, 6.9, 9.5, 14.5, 18.2, 21.5, 25.2, 26.5, 23.3, 18.3, 13.9, 9.6]
	#response_data['NewYork'] = [-0.2, 0.8, 5.7, 11.3, 17.0, 22.0, 24.8, 24.1, 20.1, 14.1, 8.6, 2.5]
	#response_data['Berlin'] = [-0.9, 0.6, 3.5, 8.4, 13.5, 17.0, 18.6, 17.9, 14.3, 9.0, 3.9, 1.0]
	#response_data['London'] = [3.9, 4.2, 5.7, 8.5, 11.9, 15.2, 17.0, 16.6, 14.2, 10.3, 6.6, 4.8]
	return HttpResponse(json.dumps(d11), content_type="application/json")

def highchart(request):
	lu = { 'categories' : [ 'Fall 2008', 'Spring 2009','Fall 2009', 'Spring 2010', 'Fall 2010', 'Spring 2011'],\
			'undergrad' : [18, 22, 30, 34, 40, 47],\
			'grad' : [1, 2, 4, 4, 5, 7],\
			'employee' : [2, 3, 0, 1, 1, 2] }
	lu['total_enrolled'] = [sum(a) for a in zip(lu['undergrad'], lu['grad'],lu['employee'])]
	return render_to_string('enrollment_chart.html', lu )

class ChartData:
	def __init__(self, iKey, iValue):
		self.Key = iKey
		self.Value = iValue

	def __toDict__(self):
		data = {}
		data['Key'] = self.Key
		data['Value'] = self.Value
		return data


class FileItem:
    def __init__(self, fname):
        self.fname = fname

    def __repr__(self):
        return json.dumps(self.__dict__)
