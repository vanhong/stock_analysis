# -*- coding: utf-8 -*-

# Create your views here.
from decimal import *
from django.http import HttpResponse, Http404
from django.template.loader import get_template
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.template import Context
from django.db.models import Count
from django.db.models import Q
from stock_analysis.settings import STATIC_URL

from stocks.models import StockId, MonthRevenue, Dividend, SeasonProfit, SeasonRevenue
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from financial.models import SeasonFinancialRatio

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
		#print len(conditions[condition])

	results = {}

	passed = True
	dataArr = []
	filterList = []
	for key, value in conditions.iteritems(): #逐一條件做篩選
		if key == 'MonthRevenueContinuousAnnualGrowth': #月營收連續幾個月年增率>多少
			# print 'start to check ' + stockid.symbol + ' MonthRevenueContinuousAnnualGrowth'
			data = ''
			cnt = int(value['MonthCnt'])
			MonthRevenueAnnualGrowth = value['MonthRevenueAnnualGrowth']
			if cnt == '' or MonthRevenueAnnualGrowth == '':
				continue

			dates = MonthRevenue.objects.values('year', 'month').distinct().order_by('-year', '-month')
			print str(dates[0]['year']) + '-' + str(dates[0]['month'])

			if len(dates) >= cnt:
				yearStr = ''
				monthStr = ''
				for i in range(0, int(cnt)):
					yearStr += str(dates[i]['year']) +','
					monthStr += str(dates[i]['month']) + ','
				yearStr = yearStr[:-1]
				monthStr = monthStr[:-1]
				whereStr = 'stocks_monthrevenue.year in (' + yearStr + ') and stocks_monthrevenue.month in (' + monthStr + ') and stocks_monthrevenue.year_growth_rate > ' + MonthRevenueAnnualGrowth
				# print whereStr
				queryset = MonthRevenue.objects.extra(where=[whereStr]).values('symbol').annotate(mycount = Count('symbol'))
				# print 'after query len=' + str(len(queryset))
				for item in queryset:
					if item['mycount'] >= cnt:
						filterList.append(item['symbol'])
				print filterList
		elif key == 'SeasonRevenueContinuousAnnualGrowth':
			data = ''
			cnt = int(value['SeasonCnt'])
			SeasonRevenueAnnualGrowth = value['SeasonRevenueAnnualGrowth']
			if cnt == '' or SeasonRevenueAnnualGrowth == '':
				continue
			datas = SeasonRevenue.objects.values('year', 'season').distinct().order_by('-year', '-season')
			if len(dates) >= cnt:
				print 'not yet'
		elif key == 'SeasonOPM':
			# print 'start to check ' + stockid.symbol + ' OPM'
			cnt = int(value['SeasonCnt'])
			SeasonOPM = value['SeasonOPM']
			overunder = value['OverUnder']
			if cnt == '' or SeasonOPM == '' or overunder == '':
				continue
			dates = SeasonFinancialRatio.objects.values('year', 'season').distinct().order_by('-year', '-season')
			if len(dates) >= cnt:
				year_str = ''
				season_str = ''
				for i in range(0, cnt):
					year_str += str(dates[i]['year']) +','
					season_str += str(dates[i]['season']) + ','
				year_str = year_str[:-1]
				season_str = season_str[:-1]
				if overunder == 'over':
					whereStr = 'financial_seasonfinancialratio.year in (' + year_str + ') and financial_seasonfinancialratio.season in (' + season_str + ') and financial_seasonfinancialratio.operating_profit_margin > ' + SeasonOPM
				else:
					whereStr = 'financial_seasonfinancialratio.year in (' + year_str + ') and financial_seasonfinancialratio.season in (' + season_str + ') and financial_seasonfinancialratio.operating_profit_margin < ' + SeasonOPM
				queryset = SeasonFinancialRatio.objects.extra(where=[whereStr]).values('symbol').annotate(mycount = Count('symbol'))
				# print 'after query len=' + str(len(queryset))
				for item in queryset:
					if item['mycount'] >= cnt:
						filterList.append(item['symbol'])
				print filterList
		elif key == 'SeasonGPM':
			# print 'start to check ' + stockid.symbol + ' GPM'
			cnt = int(value['SeasonCnt'])
			SeasonOPM = value['SeasonGPM']
			overunder = value['OverUnder']
			if cnt == '' or SeasonOPM == '' or overunder == '':
				continue
			dates = SeasonFinancialRatio.objects.values('year', 'season').distinct().order_by('-year', '-season')
			if len(dates) >= cnt:
				year_str = ''
				season_str = ''
				for i in range(0, cnt):
					year_str += str(dates[i]['year']) +','
					season_str += str(dates[i]['season']) + ','
				year_str = year_str[:-1]
				season_str = season_str[:-1]
				if overunder == 'over':
					whereStr = 'financial_seasonfinancialratio.year in (' + year_str + ') and financial_seasonfinancialratio.season in (' + season_str + ') and financial_seasonfinancialratio.gross_profit_margin > ' + SeasonOPM
				else:
					whereStr = 'financial_seasonfinancialratio.year in (' + year_str + ') and financial_seasonfinancialratio.season in (' + season_str + ') and financial_seasonfinancialratio.gross_profit_margin < ' + SeasonOPM
				queryset = SeasonFinancialRatio.objects.extra(where=[whereStr]).values('symbol').annotate(mycount = Count('symbol'))
				# print 'after query len=' + str(len(queryset))
				for item in queryset:
					if item['mycount'] >= cnt:
						filterList.append(item['symbol'])
				print filterList
		elif key == 'CorpOverBuy':
			print 'hello'
	for item in filterList:
		if results.has_key(item):
			results[item] += 1
		else:
			results[item] = 1
	finalResults = {}
	for key, value in results.items():
		if value >= len(conditions):
			finalResults[key] = ''
			print 'get ' + key

	return render_to_response(
				'filter/filter_result.html', {
				"results": finalResults},
				context_instance = RequestContext(request))

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

def query_con_season_revenue_ann_growth_rate(request):
	con_cnt = 2
	growth_rate = 10
	seasons = SeasonRevenue.objects.values('year', 'season').distinct().order_by('-year', '-season')[:con_cnt]
	for season in seasons:
		print season
	symbols = SeasonRevenue.objects.values('symbol').filter(year_growth_rate__gt=growth_rate, year__gte=seasons[len(seasons)-1]['year']).exclude(year=seasons[len(seasons)-1]['year'], season__lt=seasons[len(seasons)-1]['season']).annotate(symbol_count=Count('symbol')).filter(symbol_count=con_cnt)
	for symbol in symbols:
		print symbol['symbol']
	return HttpResponse('test')

def daterange(start_date, end_date):
	for n in range(int ((end_date - start_date).days)):
		yield start_date + timedelta(n)