# -*- coding: utf-8 -*-

# Create your views here.
from decimal import *
from django.http import HttpResponse, Http404
from django.template.loader import get_template
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.template import Context
from django.db.models import Count
from stock_analysis.settings import STATIC_URL

from stocks.models import StockId, MonthRevenue, Dividend, SeasonProfit
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
		keySplit = key.split('-')
		condition = keySplit[0];
		para = keySplit[1];
		#取得不同篩選條件(condition)的參數(para)並設定值(value)
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
			#參數名需與前端對應
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
		elif key == 'MonthRevenueAnnualGrowthBecomeBetter':
			Cnt = int(value['Cnt'])
			AnnualGrowthLowerBound = value['AnnualGrowthLowerBound']
			if Cnt == '' or AnnualGrowthLowerBound == '':
				continue

			dates = MonthRevenue.objects.values('year', 'month').distinct().order_by('-year', '-month')
			print str(dates[0]['year']) + '-' + str(dates[0]['month'])

			if len(dates) >= Cnt:
				yearStr = ''
				monthStr = ''
				for i in range(0, Cnt):
					yearStr += str(dates[i]['year']) +','
					monthStr += str(dates[i]['month']) + ','
				yearStr = yearStr[:-1]
				monthStr = monthStr[:-1]
				whereStr = 'stocks_monthrevenue.year in (' + yearStr + ') and stocks_monthrevenue.month in (' + monthStr + ') and stocks_monthrevenue.year_growth_rate > ' + AnnualGrowthLowerBound
				# print whereStr
				queryset = MonthRevenue.objects.extra(where=[whereStr]).order_by('symbol','-year','-month').values('symbol').annotate(mycount = Count('symbol'))
				# print 'after query len=' + str(len(queryset))
				for item in queryset:
					if item['mycount'] >= Cnt:
						filterList.append(item['symbol'])
				print filterList
		elif key == 'SeasonOPM':
			# print 'start to check ' + stockid.symbol + ' OPM'
			cnt = int(value['SeasonCnt'])
			SeasonOPM = value['SeasonOPM']
			OverUnder = value['OverUnder']
			if cnt == '' or SeasonOPM == '' or OverUnder == '':
				continue
			thisList = check_season_data(cnt, OverUnder, 'operating_profit_margin', SeasonOPM)
			print thisList
			filterList.extend(thisList)

		elif key == 'SeasonGPM':
			# print 'start to check ' + stockid.symbol + ' GPM'
			cnt = int(value['SeasonCnt'])
			SeasonOPM = value['SeasonGPM']
			OverUnder = value['OverUnder']
			if cnt == '' or SeasonOPM == '' or OverUnder == '':
				continue
			thisList = check_season_data(cnt, OverUnder, 'gross_profit_margin', SeasonOPM)
			print thisList
			filterList.extend(thisList)
			# dates = SeasonFinancialRatio.objects.values('year', 'season').distinct().order_by('-year', '-season')
			# if len(dates) >= cnt:
			# 	year_str = ''
			# 	season_str = ''
			# 	for i in range(0, cnt):
			# 		year_str += str(dates[i]['year']) +','
			# 		season_str += str(dates[i]['season']) + ','
			# 	year_str = year_str[:-1]
			# 	season_str = season_str[:-1]
			# 	if overunder == 'over':
			# 		whereStr = 'financial_seasonfinancialratio.year in (' + year_str + ') and financial_seasonfinancialratio.season in (' + season_str + ') and financial_seasonfinancialratio.gross_profit_margin > ' + SeasonOPM
			# 	else:
			# 		whereStr = 'financial_seasonfinancialratio.year in (' + year_str + ') and financial_seasonfinancialratio.season in (' + season_str + ') and financial_seasonfinancialratio.gross_profit_margin < ' + SeasonOPM
			# 	queryset = SeasonFinancialRatio.objects.extra(where=[whereStr]).values('symbol').annotate(mycount = Count('symbol'))
			# 	# print 'after query len=' + str(len(queryset))
			# 	for item in queryset:
			# 		if item['mycount'] >= cnt:
			# 			filterList.append(item['symbol'])
			# 	print filterList
		elif key == 'CorpOverBuy':
			DayCnt = int(value['DayCnt'])
			NumOverTrade = value['NumOverTrade']
			OverUnder = value['OverUnder']
			if DayCnt == '' or NumOverTrade == '' or OverUnder == '':
				continue
			dates = CorpTrade.objects.values('trade_date').distinct().order_by('-trade_date')[:DayCnt]
			
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


def check_season_data(cnt, overunder, condition, conditionValue):
	filterList = []
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
			whereStr = 'financial_seasonfinancialratio.year in (' + year_str + ') and financial_seasonfinancialratio.season in (' + season_str + ') and financial_seasonfinancialratio.' + condition  + ' > ' + conditionValue
		else:
			whereStr = 'financial_seasonfinancialratio.year in (' + year_str + ') and financial_seasonfinancialratio.season in (' + season_str + ') and financial_seasonfinancialratio.' + condition  + ' < ' + conditionValue
		queryset = SeasonFinancialRatio.objects.extra(where=[whereStr]).values('symbol').annotate(mycount = Count('symbol'))
		# print 'after query len=' + str(len(queryset))
		for item in queryset:
			if item['mycount'] >= cnt:
				filterList.append(item['symbol'])

		return filterList


def daterange(start_date, end_date):
	for n in range(int ((end_date - start_date).days)):
		yield start_date + timedelta(n)