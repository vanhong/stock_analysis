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
	filter_list = []
	for key, value in conditions.iteritems(): #逐一條件做篩選
		if key == 'reveune_ann_growth_rate': #月營收連續幾個月年增率>多少
			#參數名需與前端對應
			cnt = int(value['cnt'])
			value = int(value['value'])
			print str(cnt) + ';' + str(value)
			if cnt == '' or value == '':
				continue
			update_lists = query_reveune_ann_growth_rate(cnt, value, 'month')
			filter_list.append(update_lists)
		elif key == 'reveune_s_ann_growth_rate':
			cnt = int(value['cnt'])
			value = int(value['value'])
			if cnt == '' or value == '':
				continue
			update_lists = query_reveune_ann_growth_rate(cnt, value, 'season')
			filter_list.append(update_lists)
		elif key == 'opm_s':
			# print 'start to check ' + stockid.symbol + ' OPM'
			cnt = int(value['cnt'])
			value = value['value']
			if cnt == '' or value == '' :
				continue
			update_lists = check_season_data(cnt, 'over', 'operating_profit_margin', value)
			print thisList
			filter_list.append(thisList)
		elif key == 'gpm_s':
			# print 'start to check ' + stockid.symbol + ' GPM'
			cnt = int(value['cnt'])
			value = value['value']
			if cnt == '' or value == '' :
				continue
			update_lists = check_season_data(cnt, 'over', 'gross_profit_margin', value)
			print thisList
			filter_list.extend(thisList)
		elif key == 'CorpOverBuy':
			cnt = int(value['cnt'])
			value = value['value']
			if cnt == '' or value == '':
				continue
			dates = CorpTrade.objects.values('trade_date').distinct().order_by('-trade_date')[:cnt]
			
			print 'hello'


	filterIntersection = []
	if len(filter_list) == 1:
		filterIntersection = filter_list[0]
	elif len(filter_list) >= 2:
		filterIntersection = list(set(filter_list[0]).intersection(set(filter_list[1])))
		if len(filter_list) > 2:
			for i in range(2,len(filter_list)-1):
				filterIntersection = list(set(filterIntersection).intersection(set(thisSymbols)))

	print filterIntersection
	results_dic = {}
	for item in filterIntersection.sort():
		results_dic[item] = ''

	return render_to_response(
				'filter/filter_result.html', {
				"results": results_dic},
				context_instance = RequestContext(request))


def check_season_data(cnt, overunder, condition, conditionValue):
	filter_list = []
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
				filter_list.append(item['symbol'])

		return filter_list

def query_reveune_ann_growth_rate(con_cnt, growth_rate, revenue_type):
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
				   date__gte=dates[len(dates)-2][strDate], date__lte=dates[0][strDate]).\
				   annotate(symbol_count=Count(strSymbol)).filter(symbol_count=con_cnt).values_list(strSymbol, flat=True)
	update_lists = list(set(update_lists).union(set(not_update_lists)))
	return update_lists

def query_financial_ratio(cnt, value, field, time_type):

	print 'todo'

def query_gross_profit_margin_gtn_pre_avg(request):
	strDate = 'date'
	strSymbol = 'symbol'
	avg_cnt = 4
	filter_model = SeasonFinancialRatio
	dates = filter_model.objects.values(strDate).distinct().order_by('-'+strDate).values_list(strDate, flat=True)

	#get the symbols which haven't updated the latest data
	all_symbols = stock_ids = StockId.objects.all().values_list(strSymbol,flat=True)
	latest_symbols = filter_model.objects.filter(date=dates[0]).values_list(strSymbol, flat=True)
	no_latest_symbols = [item for item in all_symbols if item not in latest_symbols]
	#print no_latest_symbols
	no_latest_symbols_str = get_condition_str(no_latest_symbols, 0, len(no_latest_symbols)-1)
	pre_date_str = get_condition_str(dates, 2, avg_cnt+2)
	query_str = ('SELECT * from stocks.financial_seasonfinancialratio A'
				' inner join '
				' (SELECT symbol, avg(gross_profit_margin) as preAvg FROM stocks.financial_seasonfinancialratio WHERE date in ' + pre_date_str + ' group by symbol ) as B'
				' on A.symbol = B.symbol '
				'where date = \'' + str(dates[1]) + '\' and gross_profit_margin > preAvg'
		)
	not_update_lists = filter_model.objects.raw(query_str)

	pre_date_str = get_condition_str(dates, 1, avg_cnt+1)
	query_str = ('SELECT * from stocks.financial_seasonfinancialratio A'
				' inner join '
				' (SELECT symbol, avg(gross_profit_margin) as preAvg FROM stocks.financial_seasonfinancialratio WHERE date in ' + pre_date_str + ' group by symbol ) as B'
				' on A.symbol = B.symbol '
				'where date = \'' + str(dates[0]) + '\' and gross_profit_margin > preAvg'
		)
	update_lists = filter_model.objects.raw(query_str)
	
	results = list(set(update_lists).union(set(not_update_lists)))
	result_symbols = map(lambda item: item.symbol, results)
	print result_symbols
	# pre_avg_query = filter_model.objects.filter(date__gte=dates[avg_cnt], date__lte=dates[1]).values('symbol').annotate(preAvg = Avg('gross_profit_margin'))
	return HttpResponse(';'.join(result_symbols))
	# strDate = 'date'
	# strSymbol = 'symbol'
	# con_cnt = 4
	# dates = SeasonFinancialRatio.objects.values(strDate).distinct().order_by('-'+strDate)[:con_cnt+1]
	# symbol_list = []
	# if dates:
	# 	avg_gross_profit_margins = SeasonFinancialRatio.objects.filter(date__gte=dates[len(dates)-1][strDate], date__lte=dates[0][strDate]).\
	# 		    				   values('symbol').annotate(gross_profit_margin_avg=Avg('gross_profit_margin'))
	# 	# print SeasonFinancialRatio.objects.filter(date=dates[0][strDate]).prefetch_related('avg_gross_profit_margins__symbol')
	# 	update_lists = SeasonFinancialRatio.objects.filter(date=dates[0][strDate])
	# 	not_update_lists = SeasonFinancialRatio.objects.filter(date=dates[1][strDate]).\
	# 					   exclude(symbol__in=SeasonFinancialRatio.objects.filter(date=dates[0][strDate]))
	# 	# for margin in avg_gross_profit_margins:
	# 	# 	try:
	# 	# 		if update_lists.filter(symbol=margin[strSymbol], gross_profit_margin__gte=margin['gross_profit_margin_avg']):
	# 	# 			symbol_list.append(margin[strSymbol])
	# 	# 		elif not_update_lists.filter(symbol=margin[strSymbol], gross_profit_margin__gte=margin['gross_profit_margin_avg']):
	# 	# 			symbol_list.append(margin[strSymbol])
	# 	# 	except:
	# 	# 		pass
	# return HttpResponse('todo')


def query_season_revenue_ann_growth_rate(request):
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

def query_month_revenue_ann_growth_rate(request):
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

def get_condition_str(dataList, indexFrom, indexTo):
	condition_str = '('
	for i in range(indexFrom, indexTo):
		condition_str += '\'' + str(dataList[i]) + '\','
	condition_str = condition_str[:-1] + ')'
	return condition_str

def daterange(start_date, end_date):
	for n in range(int ((end_date - start_date).days)):
		yield start_date + timedelta(n)