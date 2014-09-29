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
from django.db import connection
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.db.models import Avg
import json

from exceptions import NotImplementedError
from abc import ABCMeta, abstractmethod

from stock_analysis.settings import STATIC_URL
from stocks.models import StockId, MonthRevenue, Dividend, SeasonProfit, SeasonRevenue
from financial.models import SeasonFinancialRatio
from price.models import Price
from chip.models import *

import inspect
import pdb

class BaseFilter():

    def __init__(self, params):
        self.cnt = int(params['cnt'])
        self.value = int(params['value'])
        self.time_type = params['timetype']
        self.overunder = params['overunder']
        if params['matchcnt'] != '':
            self.matchcnt = int(params['matchcnt'])
        else:
            self.matchcnt = cnt
        #raise NotImplementedError('This is abstract class')

    @abstractmethod
    def filter(self, input1):
        pass


#定義各filter class
class FilterClasses():
    #必須有的參數: cnt, value, matchcnt, overunder, timetype

    class RevenueYoY(BaseFilter):
        #月營收 近X個月有Y個月年增率 > N%
        def __init__(self, params):
            print 'Initialize RevenueYoY'
            #self.base = super(type(self), self)
            BaseFilter.__init__(self, params) # __init__ method of the superclass is not done implicitly
            print 'self.cnt = %s' % (self.cnt)

        def filter(self, params):
            print params
            print 'cnt=%s, matchcnt=%s, time_type=%s, overunder=%s, value=%s' % (self.cnt, self.matchcnt, self.time_type, self.overunder, self.value)
            results = query_revenue_ann_growth_rate(self.cnt, self.matchcnt, self.overunder, self.value, self.time_type)
            return results

    class FinancialRatio(BaseFilter):
        #check financial ratio
        def __init__(self):
            print 'Initialize FinancialRatio'
            BaseFilter.__init__(self, params)

        def filter(self, params):
            print params

@csrf_exempt
def filter_start(request):
    print '%s, get json = %s' % ('Start to Filter (new version)', request.body)
    filter_list = [] #array
    json_data = json.loads(request.body)
    #pdb.set_trace()
    for item in json_data:
        #create filter object according to the class name
        targetClass = getattr(FilterClasses, item['class'])
        if inspect.isclass(targetClass): #check does the class exist
            instance = targetClass(item)
            results = instance.filter(item)
            filter_list.append(results)
    new_list = sorted(filter_list)
    results_dic = {}
    for item in new_list:
        for symbol in item:
            results_dic[symbol] = StockId.objects.get(symbol=symbol).name
    #print results_dic
    return render_to_response(
                'filter/filter_result.html', {
                "results": results_dic},
                context_instance = RequestContext(request))

@csrf_exempt
def filter_start2(request):

    print 'Start to Filter2'
    conditions = {}

    #處理前端post的條件參數
    #參數名需與前端template對應
    for key, value in request.POST.iteritems():
        keySplit = key.split('-')
        condition = keySplit[0];
        para = keySplit[1];
        #取得不同篩選條件(condition)的參數(para)並設定值(value)
        if conditions.has_key(condition) is False:
            conditions[condition] = {para: value}
        else:
            conditions[condition][para] = value
        #print 'condition=' + condition + ', para=' + para + ', value=' + value
        #print len(conditions[condition])
    print 'params are as follow:'
    print conditions
    filter_list = []
    for key, value in conditions.iteritems(): #逐一條件做篩選
        if key == 'RevenueYoY': #月營收連續幾個月年增率>
            cnt = int(value['cnt'])
            value = int(value['value'])
            update_lists = query_revenue_ann_growth_rate(cnt, cnt, 'gte', value, 'month')
            #targetClass = getattr(FilterClasses, key)
            #instance = targetClass()
            #results = instance.filter(value)
            filter_list.append(update_lists)
        elif key == 'revenue_avg_ann_growth_rate': #月營收平均N個月的營收年增率>
            cnt = int(value['cnt'])
            value = int(value['value'])
            if cnt == '' or value == '':
                continue
            print cnt
            update_lists = query_revenue_avg_ann_growth_rate(cnt, value, 'month')
            #print update_lists
            filter_list.append(update_lists)
        elif key == 'revenue_s_ann_growth_rate': #季營收連續幾季年增率>
            print 'revenue_s_ann_growth_rate'
            cnt = int(value['cnt'])
            value = int(value['value'])
            if cnt == '' or value == '':
                continue
            update_lists = query_revenue_ann_growth_rate(cnt, cnt, 'gte', value, 'season')
            print 'revenue_s_ann_growth_rate'
            #print update_lists
            filter_list.append(update_lists)
        elif key == 'revenue_s_avg_ann_growth_rate': #季營收連續幾季年增率>
            cnt = int(value['cnt'])
            value = int(value['value'])
            if cnt == '' or value == '':
                continue
            update_lists = query_revenue_avg_ann_growth_rate(cnt, value, 'season')
            print 'revenue_s_avg_ann_growth_rate'
            #print update_lists
            filter_list.append(update_lists)
        elif key == 'opm_s': #季OPM連續幾季>
            # print 'start to check ' + stockid.symbol + ' OPM'
            cnt = int(value['cnt'])
            value = int(value['value'])
            if cnt == '' or value == '' :
                continue
            update_lists = query_financial_ratio(cnt, value, 'operating_profit_margin', 'season')
            print 'opm_s'
            #print update_lists
            filter_list.append(update_lists)
        elif key == 'gpm_s':
            # print 'start to check ' + stockid.symbol + ' GPM'
            cnt = int(value['cnt'])
            value = int(value['value'])
            if cnt == '' or value == '' :
                continue
            update_lists = check_season_data(cnt, 'over', 'gross_profit_margin', value)
            filter_list.append(update_lists)
        elif key == 'gpm_s_gtn_pre_avg': #季GPM大於前幾季平均
            cnt = int(value['cnt'])
            if cnt == '' :
                continue
            update_lists = query_gpm_s_gtn_pre_avg(cnt)
            print 'gpm_s_gtn_pre_avg'
            #print update_lists
            filter_list.append(update_lists)
        elif key == 'CorpOverBuy':
            cnt = int(value['cnt'])
            value = value['value']
            if cnt == '' or value == '':
                continue
            dates = CorpTrade.objects.values('trade_date').distinct().order_by('-trade_date')[:cnt]
        elif key == 'yield_rate':
            cnt = int(value['cnt'])
            value = value['value']
            if cnt == '' or value == '':
                continue
            update_lists = query_yield_rate(cnt, value)

    
    filterIntersection = []
    if len(filter_list) == 1:
        filterIntersection = filter_list[0]
    elif len(filter_list) >= 2:
        filterIntersection = list(set(filter_list[0]).intersection(set(filter_list[1])))
        if len(filter_list) > 2:
            for i in range(2,len(filter_list)):
                filterIntersection = list(set(filterIntersection).intersection(set(filter_list[i])))

    print 'Print filterIntersection'
    print filterIntersection
    new_list = sorted(filterIntersection)    
    results_dic = {}
    for item in new_list:
        if StockId.objects.filter(symbol=item):
            results_dic[item] = StockId.objects.get(symbol=item).name
    return render_to_response(
                'filter/filter_result.html', {
                "results": sorted(results_dic.iteritems())},
                context_instance = RequestContext(request))

#not used
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
            whereStr = 'financial_seasonfinancialratio.year in (' + str(year_str) + ') and financial_seasonfinancialratio.season in (' + season_str + ') and financial_seasonfinancialratio.' + condition  + ' > ' + str(conditionValue)
        else:
            whereStr = 'financial_seasonfinancialratio.year in (' + str(year_str) + ') and financial_seasonfinancialratio.season in (' + season_str + ') and financial_seasonfinancialratio.' + condition  + ' < ' + str(conditionValue)
        queryset = SeasonFinancialRatio.objects.extra(where=[whereStr]).values('symbol').annotate(mycount = Count('symbol'))
        # print 'after query len=' + str(len(queryset))
        for item in queryset:
            if item['mycount'] >= cnt:
                filter_list.append(item['symbol'])

        return filter_list

def query_financial_ratio_avg(cnt, value, field, time_type, query_type):
    strDate = 'date'
    strSymbol = 'symbol'
    filter_value = values
    filter_field = field
    if time_type == 'season':
        financial_model = SeasonFinancialRatio
    elif time_type == 'year':
        financial_model = YearFinancialRatio
    kwargs = {
        '{0}__{1}'.format('field_avg', query_type):filter_value
    }
    #get recent cnt+1 date
    dates = financial_model.objects.values(strDate).distinct().order_by('-'+strDate)[:cnt+1]
    not_update_lists = financial_model.objects.values(strSymbol).filter(date__gte=dates[len(dates)-1][strDate],
                       date__lte=dates[1][strDate]).annotate(field_avg=Avg(filter_field)).\
                       filter(**kwargs).values_list(strSymbol, flat=True)
    update_lists = financial_model.objects.values(strSymbol).filter(date__gte=dates[len(dates)-2][strDate],
                   date__lte=dates[0][strDate]).annotate(field_avg=Avg(filter_field)).\
                   filter(**kwargs).values_list(strSymbol, flat=True)
    update_lists = list(set(update_lists).union(set(not_update_lists)))
    return update_lists


def query_chip_flow(cnt, data_kind, diff):
	strDate = 'date'
	strSymbol = 'symbol'
	table = 'stocks.chip_shareholderstructure'
	dates = ShareholderStructure.objects.values(strDate).distinct().order_by('-' + strDate).values_list(strDate, flat=True)
	cursor = connection.cursor()
	#get the symbols which haven't updated the latest data
	second_date_str = str(dates[1])
	latest_date_str = str(dates[0])

	for i in range(0,cnt-1):
		#print pre_date_str
		query_str = (' SELECT A.symbol, A.data_kind, ThisSum-PreSum AS diff FROM (\n '
					' (SELECT symbol,data_kind, value400_600+value600_800+value800_1000+value1000 AS ThisSum FROM\n '
					' chip_shareholderstructure where  date=' + latest_date_str  + ') A \n'
					' inner join\n '
					' (SELECT symbol,data_kind, value400_600+value600_800+value800_1000+value1000 as PreSum FROM\n '
					' chip_shareholderstructure where  date=' + second_date_str  + ') B\n '
					' on A.symbol = B.symbol and A.data_kind = B.data_kind )')
		#print query_str
		cursor.execute(query_str)
		result = cursor.fetchall()

		for item in result:
			if item[2] > diff and item[1] == 'ratio':
				print item[0]

	return ''

def query_financial_ratio_avg(cnt, value, field, time_type, query_type):
	strDate = 'date'
	strSymbol = 'symbol'
	filter_value = values
	filter_field = field
	if time_type == 'season':
		financial_model = SeasonFinancialRatio
	elif time_type == 'year':
		financial_model = YearFinancialRatio
	#get field condition like ratio bigger than
	kwargs = {
		'{0}__{1}'.format('field_avg', query_type):filter_value
	}
	#get recent cnt+1 date
	dates = financial_model.objects.values(strDate).distinct().order_by('-'+strDate)[:cnt+1]
	not_update_lists = financial_model.objects.values(strSymbol).filter(date__gte=dates[len(dates)-1][strDate],
					   date__lte=dates[1][strDate]).annotate(field_avg=Avg(filter_field)).\
					   exclude(symbol__in=revenue_model.objects.filter(date=dates[0][strDate]).values_list(strSymbol, flat=True)).\
					   filter(**kwargs).values_list(strSymbol, flat=True)
	update_lists = financial_model.objects.values(strSymbol).filter(date__gte=dates[len(dates)-2][strDate],
				   date__lte=dates[0][strDate]).annotate(field_avg=Avg(filter_field)).\
				   filter(**kwargs).values_list(strSymbol, flat=True)
	update_lists = list(set(update_lists).union(set(not_update_lists)))
	return update_lists

def query_corp_trade(cnt, value, over_under):
    date_str = 'trade_date'
    symbol_str = 'symbol'
    update_lists = []
    kwargs = {
        '{0}__{1}'.format('field_avg', query_type):filter_value
    }
    dates = financial_model.objects.values(date_str).distinct().order_by('-'+date_str)[:cnt].values_list(date_str, flat=True)
    update_lists = CorpTrade.objects.values(symbol_str).filter(date__gte=dates[len(dates)])
    return update_lists

def query_financial_ratio(cnt, value, field, time_type):
    strDate = 'date'
    strSymbol = 'symbol'
    con_cnt = cnt
    filter_value = value
    filter_field = field
    if time_type == 'season':
        financial_model = SeasonFinancialRatio
    elif time_type == 'year':
        financial_model = YearFinancialRatio
    dates = financial_model.objects.values(strDate).distinct().order_by('-'+strDate)[:con_cnt+1]
    not_update_kwargs = {
        '{0}__{1}'.format(filter_field, 'gte'):filter_value,
        '{0}__{1}'.format('date', 'gte'):dates[len(dates)-1][strDate],
        '{0}__{1}'.format('date', 'lte'):dates[1][strDate]
    }
    update_kwargs = {
        '{0}__{1}'.format(filter_field, 'gte'):filter_value,
        '{0}__{1}'.format('date', 'gte'):dates[len(dates)-2][strDate],
        '{0}__{1}'.format('date', 'lte'):dates[0][strDate]
    }
    not_update_lists = financial_model.objects.values(strSymbol).filter(**not_update_kwargs).\
                   annotate(symbol_count=Count(strSymbol)).filter(symbol_count=con_cnt).\
                   exclude(symbol__in=financial_model.objects.filter(date=dates[0][strDate]).values_list(strSymbol, flat=True)).\
                   values_list(strSymbol, flat=True)
    update_lists = financial_model.objects.values_list(strSymbol).filter(**update_kwargs).\
                   annotate(symbol_count=Count(strSymbol)).filter(symbol_count=con_cnt).values_list(strSymbol, flat=True)
    update_lists = list(set(update_lists).union(set(not_update_lists)))

    return update_lists

def query_revenue_ann_growth_rate(cnt, matchcnt, overunder, growth_rate, revenue_type):
    strDate = 'date'
    strSymbol = 'symbol'
    if revenue_type == 'month':
        revenue_model = MonthRevenue
    elif revenue_type == 'season':
        revenue_model = SeasonRevenue
    else:
        return None
    #print 'overunder = ' + overunder
    dates = revenue_model.objects.values(strDate).distinct().order_by('-'+strDate)[:cnt + 1]
    not_update_kwargs = {
        '{0}__{1}'.format('year_growth_rate', overunder):growth_rate,
        '{0}__{1}'.format('date', 'gte'):dates[len(dates)-1][strDate],
        '{0}__{1}'.format('date', 'lte'):dates[1][strDate]
    }
    update_kwargs = {
        '{0}__{1}'.format('year_growth_rate', overunder):growth_rate,
        '{0}__{1}'.format('date', 'gte'):dates[len(dates)-2][strDate],
        '{0}__{1}'.format('date', 'lte'):dates[0][strDate]
    }
    not_update_lists = revenue_model.objects.values(strSymbol).filter(**not_update_kwargs).\
                       annotate(symbol_count=Count(strSymbol)).filter(symbol_count__gte=matchcnt).\
                       exclude(symbol__in=revenue_model.objects.filter(date=dates[0][strDate]).values_list(strSymbol, flat=True)).\
                       values_list(strSymbol, flat=True)
    print 'not_update_lists'
    print not_update_lists
    update_lists = revenue_model.objects.values(strSymbol).filter(**update_kwargs).\
                   annotate(symbol_count=Count(strSymbol)).filter(symbol_count__gte=matchcnt).values_list(strSymbol, flat=True)
    update_lists = list(set(update_lists).union(set(not_update_lists)))
    return update_lists

def query_revenue_avg_ann_growth_rate2(cnt, growth_rate, revenue_type):
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

    dates = filter_model.objects.values(strDate).distinct().order_by('-' + strDate).values_list(strDate, flat=True)
    cursor = connection.cursor()
    #get the symbols which haven't updated the latest data
    pre_date_str = get_condition_str(dates, 1, cnt+2)
    #print pre_date_str
    query_str = ('SELECT * FROM ( SELECT symbol, AVG(year_growth_rate) avg_yoy from ' + table + ' A'
                ' WHERE date in ' + pre_date_str + ' group by symbol) AS A  WHERE avg_yoy >= ' + str(growth_rate))
    cursor.execute(query_str)
    not_update_lists = cursor.fetchall()

    pre_date_str = get_condition_str(dates, 0, cnt+1)
    #print pre_date_str
    query_str = ('SELECT * FROM ( SELECT symbol, AVG(year_growth_rate) avg_yoy from ' + table + ' A'
                ' WHERE date in ' + pre_date_str + ' group by symbol) AS B WHERE avg_yoy >= ' + str(growth_rate))
    cursor.execute(query_str)
    update_lists = cursor.fetchall()
    
    print '------Before Union-------'
    results = list(set(update_lists).union(set(not_update_lists)))
    result_symbols = map(lambda item: item[0], results)
    return result_symbols

def query_revenue_avg_ann_growth_rate(cnt, growth_rate, revenue_type):
    strDate = 'date'
    strSymbol = 'symbol'
    if revenue_type == 'month':
        revenue_model = MonthRevenue
    elif revenue_type == 'season':
        revenue_model = SeasonRevenue
    else:
        return None
    con_cnt = cnt
    dates = revenue_model.objects.values(strDate).distinct().order_by('-'+strDate)[:con_cnt + 1]
    kwargs = {
        '{0}__{1}'.format('field_avg', 'gte'):growth_rate
    }
    dates = revenue_model.objects.values(strDate).distinct().order_by('-'+strDate)[:cnt+1]
    not_update_lists = revenue_model.objects.values(strSymbol).filter(date__gte=dates[len(dates)-1][strDate],
                       date__lte=dates[1][strDate]).annotate(field_avg=Avg('year_growth_rate')).\
                       exclude(symbol__in=revenue_model.objects.filter(date=dates[0][strDate]).values_list(strSymbol, flat=True)).\
                       filter(**kwargs).values_list(strSymbol, flat=True)
    update_lists = revenue_model.objects.values(strSymbol).filter(date__gte=dates[len(dates)-2][strDate],
                   date__lte=dates[0][strDate]).annotate(field_avg=Avg('year_growth_rate')).\
                   filter(**kwargs).values_list(strSymbol, flat=True)
    update_lists = list(set(update_lists).union(set(not_update_lists)))
    return update_lists


def old_query_revenue_avg_ann_growth_rate(cnt, growth_rate, revenue_type):
	strDate = 'date'
	strSymbol = 'symbol'
	strYoy = 'year_growth_rate'
	if revenue_type == 'month':
		filter_model = MonthRevenue
		table = 'stock_analysis.stocks_monthrevenue'
	elif revenue_type == 'season':
		filter_model = SeasonRevenue
		table = 'stock_analysis.stocks_seasonrevenue'
	else:
		return Nonetio

	dates = filter_model.objects.values(strDate).distinct().order_by('-' + strDate).values_list(strDate, flat=True)
	cursor = connection.cursor()
	#get the symbols which haven't updated the latest data
	latest_date_str = '\'' + str(dates[0]) + '\''
	print latest_date_str
	pre_date_str = get_condition_str(dates, 1, cnt+1)
	query_str = ('SELECT * FROM ( SELECT symbol, AVG(year_growth_rate) avg_yoy from ' + table + ' A'
				' WHERE date in ' + pre_date_str + ' AND symbol NOT IN (SELECT DISTINCT symbol FROM stock_analysis.stocks_monthrevenue WHERE date = ' + latest_date_str + ' ) group by symbol) AS A  WHERE avg_yoy >= ' + str(growth_rate))
	cursor.execute(query_str)
	not_update_lists = cursor.fetchall()

	pre_date_str = get_condition_str(dates, 0, cnt)

	query_str = ('SELECT * FROM ( SELECT symbol, AVG(year_growth_rate) avg_yoy from ' + table + ' A'
				' WHERE date in ' + pre_date_str + ' group by symbol) AS B WHERE avg_yoy >= ' + str(growth_rate))
	cursor.execute(query_str)
	update_lists = cursor.fetchall()
	
	print '------Before Union-------'
	results = list(set(update_lists).union(set(not_update_lists)))
	result_symbols = map(lambda item: item[0], results)
	return result_symbols


def query_gpm_s_gtn_pre_avg(cnt):
    strDate = 'date'
    strSymbol = 'symbol'
    avg_cnt = cnt
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
    # pre_avg_query = filter_model.objects.filter(date__gte=dates[avg_cnt], date__lte=dates[1]).values('symbol').annotate(preAvg = Avg('gross_profit_margin'))
    return result_symbols

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

	#print dataList
    condition_str = '('
    for i in range(indexFrom, indexTo):
        condition_str += '\'' + str(dataList[i]) + '\','
    condition_str = condition_str[:-1] + ')'
    return condition_str

def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)


@csrf_exempt
def filter_menu(request):
    print 'start'
    if 'kind' in request.POST:
        kind = request.POST['kind']
        print kind
    else:
        print 'nothing'
    return render_to_response('filter/' + 'filter_menu_' + kind + '.html',
                              context_instance = RequestContext(request))
def test(request):
    return render_to_response('test.html', context_instance = RequestContext(request))

def test3(request):
    return render_to_response('filter/test3.html', context_instance = RequestContext(request))

def tree_table(request):
    return render_to_response('filter/test3.html', context_instance = RequestContext(request))

def filter(request):
    return render_to_response('filter/filter.html', context_instance = RequestContext(request))

def filter_test(request):
    return render_to_response('filter/filter.html', context_instance = RequestContext(request))


def filter_index(request):
    return render_to_response(
        'filter/filter_index.html', {},
        context_instance = RequestContext(request))
