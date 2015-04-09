#!/usr/bin/python
# -*- coding:utf-8 -*-

import urllib, urllib2, datetime
from urllib2 import URLError, HTTPError
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from HTMLParser import HTMLParser
from bs4 import BeautifulSoup
import time, json
from decimal import Decimal
from stocks.models import StockId, MonthRevenue, SeasonProfit, Dividend, SeasonRevenue, UpdateManagement
from financial.models import SeasonIncomeStatement
from django.db.models import Sum, Max
from core.utils import st_to_decimal
import pdb

class ObjStock:
    def __init__(self, symbol, name):
        self.symbol = symbol
        self.name = name
    def __str__(self):
        return u'%s %s' % (self.symbol, self.name)

def update_stock_id(request):
    market_type = [2, 4]
    cnt = 0
    StockId.objects.all().delete()
    for mkt in market_type:
        url = "http://isin.twse.com.tw/isin/C_public.jsp?strMode=" + str(mkt)
        webcode = urllib.urlopen(url)
        if webcode.code != 200:
            return HttpResponse("Update failed")
        if mkt == 2:
            market = 'sii'
        elif mkt == 4:
            market = 'otc'
        req = urllib2.Request(url)
        response = urllib2.urlopen(req)
        html = response.read()
        soup = BeautifulSoup(html.decode("cp950", "ignore"))
        trs = soup.find_all('tr')
        for tr in trs:
            tds = tr.find_all('td')
            if len(tds) == 7:
                if tds[5].string == 'ESVUFR' or tds[5].string == 'ESVTFR':
                    symbol, name = tds[0].string.split()
                    listing_date = datetime.datetime.strptime(tds[2].string.strip(), "%Y/%m/%d").date()
                    company_type = tds[4].string.strip()
                    stockid = StockId(symbol = symbol, name = name, market_type = market,
                                      company_type = company_type, listing_date = listing_date)
                    if symbol is not None:
                        stockid.save()
                        cnt += 1
                        print symbol

    updateManagement = UpdateManagement(name = "stockID", last_update_date = datetime.date.today(), 
                                        last_data_date = datetime.date.today(), notes="There is " + str(cnt) + " stockIds")
    updateManagement.save()
    json_obj = json.dumps({"updateDate": updateManagement.last_update_date.strftime("%y-%m-%d"),
                           "dataDate": updateManagement.last_data_date.strftime("%y-%m-%d"), "notes": updateManagement.notes})
    return HttpResponse(json_obj, content_type="application/json")

def last_season(day):
    year = day.year
    month = day.month
    if month <= 3:
        season = 4
        year -= 1
    elif month >= 4 and month <= 6:
        season = 1
    elif month >= 7 and month <= 9:
        season = 2
    elif month >= 10:
        season = 3
    return year, season

def is_decimal(s):
    try:
        Decimal(s)
    except:
        return False
    return True

def test_month_revenue(request):
    lastDate = MonthRevenue.objects.all().aggregate(Max('date'))['date__max']
    return HttpResponse(lastDate['date__max'])

def update_month_revenue(request):
    today = datetime.date.today() 
    year = today.year
    month = today.month
    if month == 1:
        year = year - 1
        month = 12
    else:
        month = month - 1
    if 'date' in request.GET:
        date = request.GET['date']
        if date != '':
            try:
                str_year, str_month = date.split('-')
                year = int(str_year)
                month = int(str_month)
            except:
                json_obj = json.dumps({"notes": "please input correct date 'yyyy-mm'"})
                return HttpResponse(json_obj, content_type="application/json")
    market = ['otc', 'sii']
    for i in range(len(market)):
        # url example http://mops.twse.com.tw/t21/sii/t21sc03_99_1.html
        url = "http://mops.twse.com.tw/nas/t21/" + market[i] + "/t21sc03_" + str(year-1911) + "_" + str(month) + "_0.html"
        print url
        req = urllib2.Request(url)
        try:
            response = urllib2.urlopen(req)
        except URLError as e:
            if hasattr(e, 'reason'):
                json_obj = json.dumps({"notes": "Reason: " + e.reason})
                return HttpResponse(json_obj, content_type="application/json")
            elif hasattr(e, 'code'):
                json_obj = json.dumps({"notes": "Error code:" + e.code})
                return HttpResponse(json_obj, content_type="application/json")
        soup = BeautifulSoup(response, from_encoding="utf-8")
        datas = soup.find_all('td', {'align':'center'})
        for data in datas:
            if data.string:
                if data.string != '-':
                    revenue = MonthRevenue()
                    revenue.surrogate_key = data.string + "_" + str(year) + str(month).zfill(2)
                    revenue.year = year
                    revenue.month = month
                    revenue.date = datetime.date(year, month, 1)
                    revenue.symbol = data.string
                    revenue_data = data.next_sibling.next_sibling
                    if is_decimal(st_to_decimal(revenue_data.string)):
                        revenue.revenue = revenue_data.string.strip().replace(',', '')
                    last_year_revenue_data = revenue_data.next_sibling.next_sibling
                    if is_decimal(last_year_revenue_data.string.strip().replace(',', '')):
                        revenue.last_year_revenue = last_year_revenue_data.string.strip().replace(',', '')
                    month_growth_rate_data = last_year_revenue_data.next_sibling
                    if is_decimal(month_growth_rate_data.string.strip().replace(',', '')):
                        revenue.month_growth_rate = month_growth_rate_data.string.strip().replace(',', '')
                    year_growth_rate_data = month_growth_rate_data.next_sibling
                    if is_decimal(year_growth_rate_data.string.strip().replace(',', '')):
                        revenue.year_growth_rate = year_growth_rate_data.string.strip().replace(',', '')
                    acc_revenue_data = year_growth_rate_data.next_sibling
                    if is_decimal(acc_revenue_data.string.strip().replace(',', '')):
                        revenue.acc_revenue = acc_revenue_data.string.strip().replace(',', '')
                    last_acc_revenue_data = acc_revenue_data.next_sibling
                    if is_decimal(last_acc_revenue_data.string.strip().replace(',', '')):
                        revenue.last_acc_revenue = last_acc_revenue_data.string.strip().replace(',', '')
                    acc_year_growth_rate_data = last_acc_revenue_data.next_sibling
                    if is_decimal(acc_year_growth_rate_data.string.strip().replace(',', '')):
                        revenue.acc_year_growth_rate = acc_year_growth_rate_data.string.strip().replace(',', '')
                    print (revenue.symbol)
                    revenue.save()
    cnt = MonthRevenue.objects.filter(year=year, month=month).count()
    lastDate = MonthRevenue.objects.all().aggregate(Max('date'))['date__max']
    lastDateDataCnt = MonthRevenue.objects.filter(date=lastDate).count()
    updateManagement = UpdateManagement(name = "mr", last_update_date = datetime.date.today(), 
                                        last_data_date = lastDate, notes="There is " + str(lastDateDataCnt) + " month_revenues")
    updateManagement.save()
    json_obj = json.dumps({"name": updateManagement.name, "updateDate": updateManagement.last_update_date.strftime("%y-%m-%d"),
                                 "dataDate": lastDate.strftime("%y-%m-%d"), "notes": "Update " + str(cnt) + " month revenue on " + str(year) + "-" + str(month)})
    return HttpResponse(json_obj, content_type="application/json")

def check_month_revenue(request):
    if 'date' in request.GET:
        date = request.GET['date']
        if date != '':
            try:
                str_from, str_to = date.split(':')
                dateFrom = datetime.datetime.strptime(str_from, '%Y-%m').date()
                dateTo = datetime.datetime.strptime(str_to, '%Y-%m').date()
            except:
                json_obj = json.dumps({"notes": "please input correct date 'yyyy-mm:yyyy-mm'"})
                return HttpResponse(json_obj, content_type="application/json")
        else:
            json_obj = json.dumps({"notes": "please input correct date 'yyyy-mm:yyyy-mm'"})
            return HttpResponse(json_obj, content_type="application/json")
    stockIds = StockId.objects.all()
    revenues = MonthRevenue.objects.filter(date__gte=dateFrom, date__lte=dateTo)
    monthNum = month_between(dateFrom, dateTo) + 1
    errorStockIDs = []
    for stockId in stockIds:
        revenue = revenues.filter(symbol=stockId.symbol)
        if stockId.listing_date >= dateFrom and stockId.listing_date <= dateTo:
            if len(revenue) == 0:
                errorStockIDs.append(stockId.symbol)
            else:
                minMonth = revenue.order_by('date')[0].date
                if minMonth > stockId.listing_date:
                    minMonth = stockId.listing_date
                newMonthNum = month_between(minMonth, dateTo) + 1
                if (len(revenue) != newMonthNum):
                    errorStockIDs.append(stockId.symbol)
        elif stockId.listing_date < dateFrom:
            if (len(revenue) != monthNum):
                errorStockIDs.append(stockId.symbol)
    if len(errorStockIDs) > 0:
        strError = ""
        for stockID in errorStockIDs:
            strError = strError + stockID + ","
        json_obj = json.dumps({"notes" : strError})
        return HttpResponse(json_obj, content_type="application/json")

    json_obj = json.dumps({"notes": "check month revenue ok"})

    return HttpResponse(json_obj, content_type="application/json")

def month_between(startDate, endDate):
    return (endDate.year - startDate.year) * 12 + endDate.month - startDate.month

def new_update_dividendupdate_season_revenue(request):
    return HttpResponse("update season revenue")

def update_season_revenue(request):
    if 'date' in request.GET:
        date = request.GET['date']
        if date != '':
            try:
                str_year, str_season = date.split('-')
                year = int(str_year)
                season = int(str_season)
            except:
                json_obj = json.dumps({"notes": "please input correct season 'year-season'"})
                return HttpResponse(json_obj, content_type="application/json")
        else:
            json_obj = json.dumps({"notes": "please input correct season 'year-season'"})
            return HttpResponse(json_obj, content_type="application/json")
    else:
        json_obj = json.dumps({"notes": "please input correct season 'year-season'"})
        return HttpResponse(json_obj, content_type="application/json")

    if season == 1:
        startMonth = 1
    elif season == 2:
        startMonth = 4
    elif season == 3:
        startMonth = 7
    elif season == 4:
        startMonth = 10
    else:
        json_obj = json.dumps({"notes": "please input correct season 'year-season'"})
        return HttpResponse(json_obj, content_type="application/json")
    firtMonthStockIds = MonthRevenue.objects.filter(year=year, month=startMonth).values_list('symbol', flat=True)
    secondMonthStockIds = MonthRevenue.objects.filter(year=year, month=startMonth+1).values_list('symbol', flat=True)
    thirdMonthStockIds = MonthRevenue.objects.filter(year=year, month=startMonth+2).values_list('symbol', flat=True)
    firstMonthRevenues = MonthRevenue.objects.filter(year=year, month=startMonth)
    secondMonthRevenues = MonthRevenue.objects.filter(year=year, month=startMonth+1)
    thirdMonthRevenues = MonthRevenue.objects.filter(year=year, month=startMonth+2)
    date = datetime.date(year, startMonth, 1)
    lastYear, lastSeason = last_season(date)
    lastSeasonRevenues = SeasonRevenue.objects.filter(year=lastYear, season=lastSeason)
    symbols = list(set(firtMonthStockIds).intersection(set(secondMonthStockIds)).intersection(set(thirdMonthStockIds)))
    for symbol in symbols:
        print symbol
        revenue = SeasonRevenue()
        revenue.surrogate_key = symbol + '_' + str(year) + str(season).zfill(2)
        revenue.year = year
        revenue.season = season
        revenue.date = date
        revenue.symbol = symbol
        try:
            revenue.revenue = firstMonthRevenues.get(symbol=symbol).revenue +\
                              secondMonthRevenues.get(symbol=symbol).revenue +\
                              thirdMonthRevenues.get(symbol=symbol).revenue
            revenue.last_year_revenue = firstMonthRevenues.get(symbol=symbol).last_year_revenue +\
                                        secondMonthRevenues.get(symbol=symbol).last_year_revenue +\
                                        thirdMonthRevenues.get(symbol=symbol).last_year_revenue
            if revenue.last_year_revenue > 0:
                revenue.year_growth_rate = revenue.revenue / revenue.last_year_revenue * 100 - 100
            if lastSeasonRevenues.filter(symbol=symbol):
                last_season_revenue = lastSeasonRevenues.get(symbol=symbol).revenue
                if last_season_revenue > 0:
                    revenue.season_growth_rate = revenue.revenue / last_season_revenue * 100 - 100
            revenue.acc_revenue = thirdMonthRevenues.get(symbol=symbol).acc_revenue
            revenue.acc_year_growth_rate = thirdMonthRevenues.get(symbol=symbol).acc_year_growth_rate
            revenue.save()
        except:
            pass
    cnt = SeasonRevenue.objects.filter(year=year, season=season).count()
    lastDate = SeasonRevenue.objects.all().aggregate(Max('date'))['date__max']
    if lastDate == None:
        json_obj = json.dumps({"notes": "There is no data in SeasonRevenue"})
        return HttpResponse(json_obj, content_type="application/json")
    lastDateDataCnt = SeasonRevenue.objects.filter(date=lastDate).count()
    updateManagement = UpdateManagement(name = "sr", last_update_date = datetime.date.today(), 
                                        last_data_date = lastDate, notes="There is " + str(lastDateDataCnt) + " datas")
    updateManagement.save()
    json_obj = json.dumps({"name": updateManagement.name, "updateDate": updateManagement.last_update_date.strftime("%y-%m-%d"),
                                 "dataDate": lastDate.strftime("%y-%m-%d"), "notes": "Update " + str(cnt) + " season revenue on " + str(year) + "-" + str(season)})
    return HttpResponse(json_obj, content_type="application/json")

def old_update_season_revenue(request):
    stock_ids = StockId.objects.all()
    for stockid in stock_ids:
        symbol = stockid.symbol
        statements = SeasonIncomeStatement.objects.filter(symbol=symbol).order_by('date')
        if statements:
            for statement in statements:
                season_revenue = SeasonRevenue.objects.filter(symbol=symbol, year=statement.year, season=statement.season)
                if not season_revenue:
                    if statement.season == 1:
                        if statements.filter(year=statement.year-1, season=4):
                            last_season_statement = statements.get(year=statement.year-1, season=4)
                        else:
                            last_season_statement = None
                    else:
                        if statements.filter(year=statement.year, season=statement.season-1):
                            last_season_statement = statements.get(year=statement.year, season=statement.season-1)
                        else:
                            last_season_statement = None
                    if statements.filter(year=statement.year-1, season=statement.season):
                        last_year_statement = statements.get(year=statement.year-1, season=statement.season)
                    else:
                        last_year_statement = None
                    revenue = SeasonRevenue()
                    revenue.surrogate_key = symbol + "_" + str(statement.year) + str(statement.season).zfill(2)
                    revenue.year = statement.year
                    revenue.season = statement.season
                    if revenue.season == 1:
                        revenue.date = datetime.date(revenue.year, 1, 1)
                    elif revenue.season == 2:
                        revenue.date = datetime.date(revenue.year, 4, 1)
                    elif revenue.season == 3:
                        revenue.date = datetime.date(revenue.year, 7, 1)
                    elif revenue.season == 4:
                        revenue.date = datetime.date(revenue.year, 10, 1)
                    revenue.symbol = symbol
                    revenue.revenue = statement.operating_revenue
                    if last_season_statement:
                        if last_season_statement.operating_revenue > 0:
                            revenue.season_growth_rate = Decimal(((revenue.revenue / last_season_statement.operating_revenue) - 1) * 100)
                    if last_year_statement:
                        revenue.last_year_revenue = Decimal(last_year_statement.operating_revenue)
                        if revenue.last_year_revenue > 0:
                            revenue.year_growth_rate = Decimal(((revenue.revenue / revenue.last_year_revenue) - 1) * 100)
                    revenue.acc_revenue = SeasonIncomeStatement.objects.filter(symbol=symbol, year=statement.year, season__lte=statement.season).aggregate(Sum('operating_revenue'))['operating_revenue__sum']
                    #revenue.acc_revenue = SeasonIncomeStatement.objects.filter(symbol=symbol, year=statement.year, season__lte=statement.season)
                    if last_year_statement:
                        last_acc_revenue = SeasonIncomeStatement.objects.filter(symbol=symbol, year=statement.year-1, season__lte=statement.season).aggregate(Sum('operating_revenue'))['operating_revenue__sum']
                        #print revenue.acc_revenue
                        #print last_acc_revenue
                        if last_acc_revenue > 0:
                            revenue.acc_year_growth_rate = Decimal(((revenue.acc_revenue / last_acc_revenue) - 1) * 100)
                    revenue.save()
            print symbol + ' season revenue updated'

    return HttpResponse('update season revenue')

def old_update_dividend(request):
    print 'hello'
    today = datetime.date.today() 
    year = today.year
    pdb.set_trace()
    url = "http://mops.twse.com.tw/server-java/t05st09sub"
    values = {'step' : '1', 'TYPEK' : 'otc',
              'YEAR' : '102', 'first' : ''}
    url_data = urllib.urlencode(values)
    req = urllib2.Request(url, url_data)
    response = urllib2.urlopen(req)
    # soup = BeautifulSoup(response, from_encoding="utf-8")
    # datas = soup.find_all('tr', {'class':'even'})
    
    # print response.read()
    return HttpResponse(response.read())

def update_dividend(request):
    if 'year' in request.GET:
        input_year = int(request.GET['year'])
    else:
        input_year = 101
    stock_ids = StockId.objects.all()
    for stock_id in stock_ids:
        revenueInDb = Dividend.objects.filter(symbol=stock_id.symbol, year=int(input_year)+1911)
        if revenueInDb:
            continue
        else:
            stock_symbol = stock_id.symbol
            url = "http://jsjustweb.jihsun.com.tw/z/zc/zcc/zcc_" + stock_symbol + ".djhtm"
            web = urllib.urlopen(url)
            soup = BeautifulSoup(web)
            dividend_datas = soup.find_all("td", { "class": "t2" })
            for dividend_data in dividend_datas:
                try:
                    year = int(dividend_data.string) + 1911
                    dividend = Dividend()
                    dividend.year = year
                    dividend.date = datetime.date(year, 1, 1)
    
                    dividend.surrogate_key = stock_symbol + "_" + str(year)
                    dividend.symbol = stock_symbol
                    next = dividend_data.next_sibling.next_sibling
                    dividend.cash_dividends = Decimal(next.string)
                    next = next.next_sibling.next_sibling
                    dividend.stock_dividends_from_retained_earnings = Decimal(next.string)
                    next = next.next_sibling.next_sibling
                    dividend.stock_dividends_from_capital_reserve = Decimal(next.string)
                    next = next.next_sibling.next_sibling
                    dividend.stock_dividends = Decimal(next.string)
                    next = next.next_sibling.next_sibling
                    dividend.total_dividends = Decimal(next.string)
                    next = next.next_sibling.next_sibling
                    dividend.employee_stock_rate = Decimal(next.string)
                    dividend.save()
                except:
                    pass
            print 'update ' + stock_symbol + ' dividend'

    return HttpResponse("update dividend")

def update(request):
    all_data = UpdateManagement.objects.all()
    stockID = {}
    monthRevenue = {}
    seasonRevenue = {}
    seasonIncomeStatement = {}
    seasonBalanceSheet = {}
    seasonCashflow = {}
    seasonFinancialRatio = {}
    if all_data.filter(name='stockID').count() > 0:
        data = UpdateManagement.objects.get(name='stockID')
        stockID['name'] = data.name
        stockID['updateDate'] = data.last_update_date.strftime("%y-%m-%d")
        stockID['dataDate'] = data.last_data_date.strftime("%y-%m-%d")
        stockID['notes'] = data.notes

    if all_data.filter(name='mr').count() > 0:
        data = UpdateManagement.objects.get(name='mr')
        monthRevenue['updateDate'] = data.last_update_date.strftime("%y-%m-%d")
        monthRevenue['dataDate'] = data.last_data_date.strftime("%y-%m-%d")
        monthRevenue['notes'] = data.notes

    if all_data.filter(name='sr').count() > 0:
        data = UpdateManagement.objects.get(name='sr')
        seasonRevenue['updateDate'] = data.last_update_date.strftime("%y-%m-%d")
        seasonRevenue['dataDate'] = data.last_data_date.strftime("%y-%m-%d")
        seasonRevenue['notes'] = data.notes

    if all_data.filter(name='sis').count() > 0:
        data = UpdateManagement.objects.get(name='sis')
        seasonIncomeStatement['updateDate'] = data.last_update_date.strftime("%y-%m-%d")
        seasonIncomeStatement['dataDate'] = data.last_data_date.strftime("%y-%m-%d")
        seasonIncomeStatement['notes'] = data.notes

    if all_data.filter(name='sbs').count() > 0:
        data = UpdateManagement.objects.get(name='sbs')
        seasonBalanceSheet['updateDate'] = data.last_update_date.strftime("%y-%m-%d")
        seasonBalanceSheet['dataDate'] = data.last_data_date.strftime("%y-%m-%d")
        seasonBalanceSheet['notes'] = data.notes

    if all_data.filter(name='scf').count() > 0:
        data = UpdateManagement.objects.get(name='scf')
        seasonCashflow['updateDate'] = data.last_update_date.strftime("%y-%m-%d")
        seasonCashflow['dataDate'] = data.last_data_date.strftime("%y-%m-%d")
        seasonCashflow['notes'] = data.notes

    if all_data.filter(name='sfr').count() > 0:
        data = UpdateManagement.objects.get(name='sfr')
        seasonFinancialRatio['updateDate'] = data.last_update_date.strftime("%y-%m-%d")
        seasonFinancialRatio['dataDate'] = data.last_data_date.strftime("%y-%m-%d")
        seasonFinancialRatio['notes'] = data.notes


    return render_to_response('analysis/update.html', 
            {'stockid': stockID, 'mr': monthRevenue, 'sr': seasonRevenue,
             'sis': seasonIncomeStatement, 'sbs' : seasonBalanceSheet,
             'scf': seasonCashflow, 'sfr' : seasonFinancialRatio}, context_instance=RequestContext(request))



