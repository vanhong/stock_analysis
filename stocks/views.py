#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib, urllib2, datetime
from urllib2 import URLError, HTTPError
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from HTMLParser import HTMLParser
from bs4 import BeautifulSoup
import time, json
from decimal import Decimal
from stocks.models import StockId, MonthRevenue, SeasonProfit, Dividend, SeasonRevenue, UpdateManagement, WatchList
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
    StockType = [2, 4]
    cnt = 0
    for i in xrange(0, len(StockType)):
        url = "http://isin.twse.com.tw/isin/C_public.jsp?strMode=" + str(StockType[i])
        webcode = urllib.urlopen(url)
        if webcode.code != 200:
            return HttpResponse("Update failed")
        req = urllib2.Request(url)
        response = urllib2.urlopen(req)
        soup = BeautifulSoup(response, from_encoding="big-5")
        datas = soup.find('tr')
        while(datas.next_sibling):
            data = datas.next_sibling.td.next
            try:
                if data.next.next_sibling.next_sibling.next_sibling.next_sibling.string.split()[0] == 'ESVUFR' or\
                   data.next.next_sibling.next_sibling.next_sibling.next_sibling.string.split()[0] == 'ESVTFR':
                    symbol,name = data.split()
                    name = name.encode('utf8')
                    print symbol
                    listing_date = datetime.datetime.strptime(data.next.next_sibling.string.split()[0], "%Y/%m/%d").date()
                    market_type = data.next.next_sibling.next_sibling.string.split()[0]
                    company_type = data.next.next_sibling.next_sibling.next_sibling.string.split()[0]
                    company_type = company_type.encode('utf8')
                    stockid = StockId(symbol = symbol, name = name, market_type = market_type,
                                      company_type = company_type, listing_date = listing_date)
                    stockid.save()
                    cnt += 1
                datas = datas.next_sibling
            except:
                datas = datas.next_sibling
    
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
    updateCnt = 0
    for i in range(len(market)):
        # url example http://mops.twse.com.tw/t21/sii/t21sc03_99_1.html
        if year >= 2015:
            url = "http://mops.twse.com.tw/nas/t21/" + market[i] + "/t21sc03_" + str(year-1911) + "_" + str(month) + "_0.html"
        elif year == 2014 and month >= 11:
            url = "http://mops.twse.com.tw/nas/t21/" + market[i] + "/t21sc03_" + str(year-1911) + "_" + str(month) + "_0.html"
        else:
            url = "http://mops.twse.com.tw/t21/" + market[i] + "/t21sc03_" + str(year-1911) + "_" + str(month) + "_0.html"
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
                    updateCnt = updateCnt + 1
                    revenue.save()
    print ("update %d symbol") %updateCnt
    cnt = MonthRevenue.objects.filter(year=year, month=month).count()
    lastDate = MonthRevenue.objects.all().aggregate(Max('date'))['date__max']
    lastDateDataCnt = MonthRevenue.objects.filter(date=lastDate).count()
    updateManagement = UpdateManagement(name = "mr", last_update_date = datetime.date.today(), 
                                        last_data_date = lastDate, notes="There is " + str(lastDateDataCnt) + " datas")
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

def show_dividend(request):
    if 'year' in request.GET:
        input_year = int(request.GET['year'])
    else:
        input_year = 2016
    stockids = StockId.objects.all()
    #stockids = ['6274']
    for stockid in stockids:
        revenueInDb = Dividend.objects.filter(symbol=stockid.symbol, year=int(input_year))
        if revenueInDb:
            continue
        print 'update ' + stockid.symbol + ' dividend'
        url = "http://jsjustweb.jihsun.com.tw/z/zc/zcc/zcc_" + stockid.symbol + ".djhtm"
        req = urllib2.Request(url)
        response = urllib2.urlopen(req)
        soup = BeautifulSoup(response, 'html.parser')
        dividend_datas = soup.find_all("td", {"class": ['t3n0', 't3n1']})
        for data in dividend_datas:
            if(data['class'][0]=='t3n0' and data.string):
                try:
                    dividend = Dividend()
                    year = int(data.string)
                    dividend.year = year
                    dividend.date = datetime.date(year, 1, 1)
                    dividend.symbol = stockid.symbol
                    dividend.surrogate_key = stockid.symbol + "_" + str(year)
                    data = data.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling
                    dividend.cash_dividends = Decimal(data.string)
                    data = data.next_sibling.next_sibling
                    dividend.stock_dividends_from_retained_earnings = Decimal(data.string)
                    data = data.next_sibling.next_sibling
                    dividend.stock_dividends_from_capital_reserve = Decimal(data.string)
                    data = data.next_sibling.next_sibling
                    dividend.stock_dividends = Decimal(data.string)
                    data = data.next_sibling.next_sibling
                    dividend.total_dividends = Decimal(data.string)
                    data = data.next_sibling.next_sibling
                    dividend.employee_stock_rate = Decimal(data.string)
                    dividend.save()
                except:
                    pass
    return HttpResponse("update dividend")

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
    updateData = {}
    if all_data.filter(name='stockID').count() > 0:
        data = UpdateManagement.objects.get(name='stockID')
        updateData['stockID'] = UpdateData(data.last_update_date.strftime("%y-%m-%d"), data.last_data_date.strftime("%y-%m-%d"), data.notes)

    if all_data.filter(name='mr').count() > 0:
        data = UpdateManagement.objects.get(name='mr')
        updateData['mr'] = UpdateData(data.last_update_date.strftime("%y-%m-%d"), data.last_data_date.strftime("%y-%m-%d"), data.notes)

    if all_data.filter(name='sr').count() > 0:
        data = UpdateManagement.objects.get(name='sr')
        updateData['sr'] = UpdateData(data.last_update_date.strftime("%y-%m-%d"), data.last_data_date.strftime("%y-%m-%d"), data.notes)

    if all_data.filter(name='sis').count() > 0:
        data = UpdateManagement.objects.get(name='sis')
        updateData['sis'] = UpdateData(data.last_update_date.strftime("%y-%m-%d"), data.last_data_date.strftime("%y-%m-%d"), data.notes)

    if all_data.filter(name='sbs').count() > 0:
        data = UpdateManagement.objects.get(name='sbs')
        updateData['sbs'] = UpdateData(data.last_update_date.strftime("%y-%m-%d"), data.last_data_date.strftime("%y-%m-%d"), data.notes)

    if all_data.filter(name='scf').count() > 0:
        data = UpdateManagement.objects.get(name='scf')
        updateData['scf'] = UpdateData(data.last_update_date.strftime("%y-%m-%d"), data.last_data_date.strftime("%y-%m-%d"), data.notes)

    if all_data.filter(name='sfr').count() > 0:
        data = UpdateManagement.objects.get(name='sfr')
        updateData['sfr'] = UpdateData(data.last_update_date.strftime("%y-%m-%d"), data.last_data_date.strftime("%y-%m-%d"), data.notes)

    if all_data.filter(name='yis').count() > 0:
        data = UpdateManagement.objects.get(name='yis')
        updateData['yis'] = UpdateData(data.last_update_date.strftime("%y-%m-%d"), data.last_data_date.strftime("%y-%m-%d"), data.notes)

    if all_data.filter(name='yfr').count() > 0:
        data = UpdateManagement.objects.get(name='yfr')
        updateData['yfr'] = UpdateData(data.last_update_date.strftime("%y-%m-%d"), data.last_data_date.strftime("%y-%m-%d"), data.notes)

    if all_data.filter(name='ycf').count() > 0:
        data = UpdateManagement.objects.get(name='ycf')
        updateData['ycf'] = UpdateData(data.last_update_date.strftime("%y-%m-%d"), data.last_data_date.strftime("%y-%m-%d"), data.notes)
    return render_to_response('analysis/update.html', 
            {'updateData': updateData}, context_instance=RequestContext(request))

def update_watchlist(request):
    stock_ids = ['2610','2618','2612','2606','2208',
            '2330','2337','3041','2458',
            '5483','3556',
            '2353','2324','3231','2382','2376',
            '2357','4938','2395','3022','6206',
            '2474','2387','6121','8210','3611',
            '2308','2420','2457','2327','2428',
            '6269','2383','3044','3037','2462',
            '6224','6279','3299','8042','8091',
            '3390','2317','6192','6146','3552',
            '3563','2393','6278','2486','2374',
            '5392','3454','3615','6231','5209',
            '3546','5478','2412','3045','4904',
            '2450','2345','2455','5388','3068',
            '3234','6143','6263','3702','3010',
            '6281','1535','1521','1525','1531',
            '4526','4532','8374','1580','6122',
            '1558','3379','8083','4528','2002',
            '1101','1102','1301','1303','1304',
            '1308','1326','1307','1325','6508',
            '1723','1710','1704','4725','1742',
            '2103','2105','2106','2108','6505',
            '6184','9904','9939','9925','9917',
            '9921','9914','9941','9924','5312',
            '1216','1201','1227','1232','1233',
            '1231','4205','1402','1477','1476',
            '4401','2912','5904','1707','1733',
            '3164','1788','4126','8940','2201',
            '2207','2548','5522','2820','2881', '2886']
    for stockid in stock_ids:
        watchlist = WatchList()
        watchlist.surrogate_key = 'wawa_' + stockid
        watchlist.user = 'wawa'
        watchlist.symbol = stockid
        watchlist.rank = -1
        watchlist.save()
    stock_ids = ['2449','1452','6202','6449','6274','8109','2421','6224','3617']
    for stockid in stock_ids:
        watchlist = WatchList()
        watchlist.surrogate_key = 'vk_' + stockid
        watchlist.user = 'vk'
        watchlist.symbol = stockid
        watchlist.rank = -1
        watchlist.save()
    return HttpResponse('update watchlist')

class UpdateData(object):
    def __init__(self, updateDate, dataDate, notes):
        self.updateDate, self.dataDate, self.notes = updateDate, dataDate, notes

