# -*- coding: utf-8 -*-

# Create your views here.
from decimal import *
from django.http import HttpResponse, Http404
from django.template.loader import get_template
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.template import Context
from django.db.models import Count
from django.db.models import Avg
from django.db.models import Q, F
from stock_analysis.settings import STATIC_URL

from stocks.models import StockId, MonthRevenue, Dividend, SeasonProfit, SeasonRevenue
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from financial.models import SeasonFinancialRatio
from django.db.models import Avg
from django.core import serializers

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

	passed = True
	filterList = []
	for key, value in conditions.iteritems(): #逐一條件做篩選
		if key == 'MonthRevenueContinuousAnnualGrowth': #月營收連續幾個月年增率>多少
			# print 'start to check ' + stockid.symbol + ' MonthRevenueContinuousAnnualGrowth'
			data = ''
			#參數名需與前端對應
			cnt = int(value['Cnt'])
			MonthRevenueAnnualGrowth = value['MonthRevenueAnnualGrowth']
			if cnt == '' or MonthRevenueAnnualGrowth == '':
				continue
			months = MonthRevenue.objects.values('year', 'month').distinct().order_by('-year', '-month')[:cnt + 1]
			not_update_symbols = MonthRevenue.objects.values('symbol').filter(year_growth_rate__gt=MonthRevenueAnnualGrowth, 
								 year__gte=months[len(months)-1]['year']).exclude(year=months[len(months)-1]['year'], 
								 month__lt=months[len(months)-1]['month']).exclude(year=months[0]['year'], 
								 month=months[0]['month']).annotate(symbol_count=Count('symbol')).filter(symbol_count=cnt)
			not_update_lists = []
			update_lists = []
			newest_update_lists = []
			for symbol in not_update_symbols:
				not_update_lists.append(symbol['symbol'])
			update_symbols = MonthRevenue.objects.values('symbol').filter(year=months[0]['year'], 
							 month=months[0]['month'])
			for symbol in update_symbols:
				update_lists.append(symbol['symbol'])
			not_update_lists = list(set(not_update_lists).difference(set(update_lists)))
			symbols = MonthRevenue.objects.values('symbol').filter(year_growth_rate__gt=MonthRevenueAnnualGrowth, 
					  year__gte=months[len(months)-2]['year']).exclude(year=months[len(months)-2]['year'], 
					  month__lt=months[len(months)-2]['month']).annotate(symbol_count=Count('symbol')).\
					  filter(symbol_count=cnt)
			for symbol in symbols:
				newest_update_lists.append(symbol['symbol'])
			newest_update_lists = list(set(newest_update_lists).union(set(not_update_lists)))
			print newest_update_lists
			filterList.append(newest_update_lists)
		elif key == 'MonthRevenueAnnualGrowthBecomeBetter':
			Cnt = int(value['Cnt'])
			AnnualGrowthLowerBound = value['AnnualGrowthLowerBound']
			if Cnt == '' or AnnualGrowthLowerBound == '':
				print 'todo'
		elif key == 'SeasonRevenueContinuousAnnualGrowth':
			data = ''
			cnt = int(value['Cnt'])
			SeasonRevenueAnnualGrowth = value['SeasonRevenueAnnualGrowth']
			seasons = SeasonRevenue.objects.values('year', 'season').distinct().order_by('-year', '-season')[:cnt + 1]
			not_update_symbols = SeasonRevenue.objects.values('symbol').filter(year_growth_rate__gt=SeasonRevenueAnnualGrowth, 
								 year_gte=seasons[len(seasons)-1]['year']).exclude(year=seasons[len(season)-1]['year'], 
								 season__lt=seasons[len(seasons)-1]['season']).exclude(year=seasons[0]['year'], 
								 season=seasons[0]['season']).annotate(symbol_count=Count('symbol')).filter(symbol_count=cnt)
			not_update_lists = []
			update_lists = []
			newest_update_lists = []
			for symbol in not_update_symbols:
				not_update_lists.append(symbol['symbol'])
			update_symbols = SeasonRevenue.objects.values('symbol').filter(year=seasons[0]['year'], 
							 month=seasons[0]['season'])
			for symbol in update_symbols:
				update_lists.append(symbol['symbol'])
			not_update_lists = list(set(not_update_lists).difference(set(update_lists)))
			symbols = SeasonRevenue.objects.values('symbol').filter(year_growth_rate__gt=SeasonRevenueAnnualGrowth, 
					  year__gte=seasons[len(seasons)-2]['year']).exclude(year=seasons[len(seasons)-2]['year'], 
					  season__lt=seasons[len(seasons)-2]['season']).annotate(symbol_count=Count('symbol')).\
					  filter(symbol_count=cnt)
			for symbol in symbols:
				newest_update_lists.append(symbol['symbol'])
			newest_update_lists = list(set(newest_update_lists).union(set(not_update_lists)))
			filterList.append(symbols)
		elif key == 'SeasonOPM':
			# print 'start to check ' + stockid.symbol + ' OPM'
			cnt = int(value['Cnt'])
			SeasonOPM = value['SeasonOPM']
			OverUnder = value['OverUnder']
			if cnt == '' or SeasonOPM == '' or OverUnder == '':
				continue
			thisList = check_season_data(cnt, OverUnder, 'operating_profit_margin', SeasonOPM)
			print thisList
			filterList.extend(thisList)

		elif key == 'SeasonGPM':
			# print 'start to check ' + stockid.symbol + ' GPM'
			cnt = int(value['Cnt'])
			SeasonOPM = value['SeasonGPM']
			OverUnder = value['OverUnder']
			if cnt == '' or SeasonOPM == '' or OverUnder == '':
				continue
			thisList = check_season_data(cnt, OverUnder, 'gross_profit_margin', SeasonOPM)
			print thisList
			filterList.extend(thisList)
		elif key == 'CorpOverBuy':
			DayCnt = int(value['Cnt'])
			NumOverTrade = value['NumOverTrade']
			OverUnder = value['OverUnder']
			if DayCnt == '' or NumOverTrade == '' or OverUnder == '':
				continue
			dates = CorpTrade.objects.values('trade_date').distinct().order_by('-trade_date')[:DayCnt]
			
			print 'hello'


	filterIntersection = []
	if len(filterList) == 1:
		filterIntersection = filterList[0]
	elif len(filterList) >= 2:
		filterIntersection = list(set(filterList[0]).intersection(set(filterList[1])))
		if len(filterList) > 2:
			for i in range(2,len(filterList)-1):
				filterIntersection = list(set(filterIntersection).intersection(set(thisSymbols)))

	print filterIntersection
	finalResults = {}
	for item in filterIntersection:
		finalResults[item] = ''

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

def query_con_reveune_ann_growth_rate(con_cnt, growth_rate, revenue_type):
	strDate = 'date'
	strSymbol = 'symbol'
	if revenue_type == 'month':
		revenue_model = MonthRevenue
	elif revenue_type == 'season':
		revenue_model = SeasonRevenue
	else:
		return None
	dates = revenue_model.objects.values(strDate).distinct().order_by('-'+strDate)[:con_cnt + 1]
	not_update_lists = revenue_model.objects.values(strSymbol).filter(year_growth_rate__gte=growth_rate, 
					   date__gte=dates[len(dates)-1][strDate], date__lte=dates[1][strDate]).\
					   annotate(symbol_count=Count(strSymbol)).filter(symbol_count=con_cnt).\
					   exclude(symbol__in=revenue_model.objects.filter(date=dates[0][strDate]).values_list(strSymbol, flat=True)).\
					   values_list(strSymbol, flat=True)
	update_lists = revenue_model.objects.values(strSymbol).filter(year_growth_rate__gte=growth_rate, 
				   date__gte=seasons[len(seasons)-2][strDate], date__lte=seasons[0][strDate]).\
				   annotate(symbol_count=Count(strSymbol)).filter(symbol_count=con_cnt).values_list(strSymbol, flat=True)
	update_lists = list(set(update_lists).union(set(not_update_lists)))
	return update_lists

def query_gross_profit_margin_gtn_pre_avg(request):
	strDate = 'date'
	strSymbol = 'symbol'
	con_cnt = 4
	dates = SeasonFinancialRatio.objects.values(strDate).distinct().order_by('-'+strDate)[:con_cnt+1]
	symbol_list = []
	if dates:
		avg_gross_profit_margins = SeasonFinancialRatio.objects.filter(date__gte=dates[len(dates)-1][strDate], date__lte=dates[0][strDate]).\
			    				   values('symbol').annotate(gross_profit_margin_avg=Avg('gross_profit_margin'))
		# print SeasonFinancialRatio.objects.filter(date=dates[0][strDate]).prefetch_related('avg_gross_profit_margins__symbol')
		update_lists = SeasonFinancialRatio.objects.filter(date=dates[0][strDate])
		not_update_lists = SeasonFinancialRatio.objects.filter(date=dates[1][strDate]).\
						   exclude(symbol__in=SeasonFinancialRatio.objects.filter(date=dates[0][strDate]))
		# for margin in avg_gross_profit_margins:
		# 	try:
		# 		if update_lists.filter(symbol=margin[strSymbol], gross_profit_margin__gte=margin['gross_profit_margin_avg']):
		# 			symbol_list.append(margin[strSymbol])
		# 		elif not_update_lists.filter(symbol=margin[strSymbol], gross_profit_margin__gte=margin['gross_profit_margin_avg']):
		# 			symbol_list.append(margin[strSymbol])
		# 	except:
		# 		pass
	return HttpResponse('todo')


def query_con_season_revenue_ann_growth_rate(request):
	strDate = 'date'
	strSymbol = 'symbol'
	con_cnt = 10
	growth_rate = 10
	dates = SeasonRevenue.objects.values(strDate).distinct().order_by('-'+strDate)[:con_cnt + 1]
	not_update_lists = SeasonRevenue.objects.values(strSymbol).filter(year_growth_rate__gte=growth_rate, 
					   date__gte=dates[len(dates)-1][strDate], date__lte=dates[1][strDate]).\
					   annotate(symbol_count=Count(strSymbol)).filter(symbol_count=con_cnt).\
					   exclude(symbol__in=SeasonRevenue.objects.filter(date=dates[0][strDate]).values_list(strSymbol, flat=True)).\
					   values_list(strSymbol, flat=True)
	update_lists = SeasonRevenue.objects.values(strSymbol).filter(year_growth_rate__gte=growth_rate, 
				   date__gte=seasons[len(seasons)-2][strDate], date__lte=seasons[0][strDate]).\
				   annotate(symbol_count=Count(strSymbol)).filter(symbol_count=con_cnt).values_list(strSymbol, flat=True)
	update_lists = list(set(update_lists).union(set(not_update_lists)))
	return HttpResponse('test')

def query_con_month_revenue_ann_growth_rate(request):
	strDate = 'date'
	strSymbol = 'symbol'
	con_cnt = 10
	growth_rate = 10
	revenue_model = MonthRevenue
	dates = revenue_model.objects.values(strDate).distinct().order_by('-'+strDate)[:con_cnt + 1]
	not_update_lists = revenue_model.objects.values(strSymbol).filter(year_growth_rate__gte=growth_rate, 
					   date__gte=dates[len(dates)-1][strDate], date__lte=dates[1][strDate]).\
					   annotate(symbol_count=Count(strSymbol)).filter(symbol_count=con_cnt).\
					   exclude(symbol__in=revenue_model.objects.filter(date=dates[0][strDate]).values_list(strSymbol, flat=True)).\
					   values_list(strSymbol, flat=True)
	update_lists = revenue_model.objects.values(strSymbol).filter(year_growth_rate__gt=growth_rate, 
				   date__gte=dates[len(dates)-2][strDate], date__lte=dates[0][strDate]).\
				   annotate(symbol_count=Count(strSymbol)).filter(symbol_count=con_cnt).values_list(strSymbol, flat=True)
	update_lists = list(set(update_lists).union(set(not_update_lists)))
	print update_lists
	return HttpResponse('test')

def test(request):
	strDate = 'date'
	strSymbol = 'symbol'
	avg_cnt = 3
	filter_model = SeasonFinancialRatio
	dates = filter_model.objects.values(strDate).distinct().order_by('-'+strDate).values_list(strDate, flat=True)
	print dates
	latest_date = str(dates[0])
	pre_date_str = '('
	for i in range(1, avg_cnt):
		pre_date_str += '\'' + str(dates[i]) + '\','
	pre_date_str = pre_date_str[:-1] + ')'
	length = len(dates)
	query = filter_model.objects.raw('SELECT * from stocks.financial_seasonfinancialratio A inner join (SELECT symbol, avg(gross_profit_margin) as preAvg FROM stocks.financial_seasonfinancialratio WHERE date in ' + pre_date_str + ' group by symbol ) as B on A.symbol = B.symbol where date = \'' + latest_date + '\' and gross_profit_margin > preAvg')
	for item in query:
		print item.get_all_fields 
	# pre_avg_query = filter_model.objects.filter(date__gte=dates[avg_cnt], date__lte=dates[1]).values('symbol').annotate(preAvg = Avg('gross_profit_margin'))
	# pre_avg_dic = {}
	# for item in pre_avg_query:
	# 	pre_avg_dic[item['symbol']] = item['preAvg']
	# filter_list = filter_model.objects.filter(gross_profit_margin__gt=pre_avg_dic[symbol])
	# print filter_list
	#print pre_avg_dic
	return HttpResponse('mytest')


def daterange(start_date, end_date):
	for n in range(int ((end_date - start_date).days)):
		yield start_date + timedelta(n)