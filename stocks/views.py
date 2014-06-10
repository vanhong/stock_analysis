#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib, urllib2, datetime
from django.http import HttpResponse
from HTMLParser import HTMLParser
from bs4 import BeautifulSoup
import time
from decimal import Decimal
from stocks.models import StockId, MonthRevenue, SeasonProfit, Dividend, SeasonRevenue
from financial.models import SeasonIncomeStatement
from django.db.models import Sum
import pdb

class ObjStock:
    def __init__(self, symbol, name):
        self.symbol = symbol
        self.name = name
    def __str__(self):
        return u'%s %s' % (self.symbol, self.name)

def update_stock_id(request):
    url = "http://www.emega.com.tw/js/StockTable.htm"
    webcode = urllib.urlopen(url)
    if webcode.code != 200:
        return HttpResponse("Update failed")
    req = urllib2.Request(url)
    response = urllib2.urlopen(req)
    soup = BeautifulSoup(response, from_encoding="big-5")
    datas = soup.find_all("table", {'class' : 'TableBorder'})

    twod_list = []
    tr_datas = datas[0].tr
    # pdb.set_trace()
    isSymbol = True
    while(tr_datas):
        stockNum = 0
        for data in tr_datas:
            if hasattr(data, 'b'):
                if isSymbol:
                    if data.b:
                        symbol = data.b.string.replace(u'\xa0','').encode('utf-8')
                        isSymbol = False
                    elif data.string:
                        symbol = data.string.replace(u'\xa0','').encode('utf-8')
                        isSymbol = False
                else:
                    if data.b:
                        name = data.b.string.replace(u'\xa0','').encode('utf-8')
                        stock = ObjStock(symbol, name)
                        isSymbol = True
                    elif data.string:
                        name = data.string.replace(u'\xa0','').encode('utf-8')
                        stock = ObjStock(symbol, name)
                        isSymbol = True
                    elif data.font:
                        name = data.next.string.replace(u'\xa0','').encode('utf-8')
                        stock = ObjStock(symbol, name)
                        isSymbol = True
                    if isSymbol:
                        if stock.symbol != '':
                            if len(twod_list) > stockNum:
                                twod_list[stockNum].append(stock)
                            else:
                                twod_list.append([])
                                twod_list[stockNum].append(stock)
                            stockNum = stockNum + 1
        tr_datas = tr_datas.next_sibling.next_sibling
    marketType = ''
    company_type = ''
    for stockList in twod_list:
        for stock in stockList:
            if stock.symbol == r'上市' or stock.symbol == r'上櫃':
                marketType = stock.symbol
                companyType = stock.name
            else:
                stockid = StockId(symbol = stock.symbol, name = stock.name.strip(),
                                  market_type = marketType, company_type = companyType)
                stockid.save()
    # pdb.set_trace()

    return HttpResponse('update stock id')

def old_update_stock_id(request):
    StockType = [2, 4]

    for i in xrange(0, len(StockType)):
        url = "http://brk.twse.com.tw:8000/isin/C_public.jsp?strMode=" + str(StockType[i])

        webcode = urllib.urlopen(url)
        stock = ParseStockId()
        if webcode.code == 200:
            stock.feed(webcode.read())
            webcode.close()
        else:
            return HttpResponse("Update Failed")
        for i in xrange(len(stock.totaldata)):
            totaldata = stock.totaldata[i]
            stockid = StockId(symbol = totaldata[0].decode("cp950").encode("utf-8"), name = totaldata[1].decode("cp950").encode("utf-8"),
                              market_type = totaldata[2].decode("cp950").encode("utf-8"), company_type = totaldata[3].decode("cp950").encode("utf-8"))
            stockid.save()
            print (totaldata[0].decode("cp950").encode("utf-8") + " " + totaldata[1].decode("cp950").encode("utf-8") + " " +
                   totaldata[2].decode("cp950").encode("utf-8") + " " + totaldata[3].decode("cp950").encode("utf-8"))
    return HttpResponse("Update StockId")

class ParseStockId(HTMLParser):
    def reset(self):
        HTMLParser.reset(self)
        self.stockinfo = False
        self.datainfo = False
        self.stock_name = ''
        self.stock_symbol = ''
        self.market_type = ''
        self.company_type = ''
        self.cell = 0
        self.stockdata = []
        self.totaldata = []

    def handle_starttag(self, tag, attrs):
        if tag == 'td':
            if attrs[0][0] == 'bgcolor' and attrs[0][1] == '#FAFAD2':
                self.stockinfo = True
                self.cell += 1
                self.cell %= 7

    def handle_endtag(self, tag):
        if tag == 'tr':
            self.stockinfo = False
            self.cell = 0

    def handle_data(self, text):
        if self.stockinfo:
            if self.cell == 1:
                data = text.strip().split("    ")
                if data[0].isalnum() and len(data[0]) == 4:
                    self.stockdata.append(data[0].strip())
                    self.stockdata.append(data[1].strip())
                    self.datainfo = True
                else:
                    self.datainfo = False
            elif self.cell == 4 and self.datainfo == True:
                self.stockdata.append(text.strip())
            elif self.cell == 5 and self.datainfo == True:
                self.stockdata.append(text.strip())
                self.totaldata.append(self.stockdata)
                self.stockdata = []

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

def update_season_profit(request):
    stock_ids = StockId.objects.all()
    today = datetime.date.today()
    for stock_id in stock_ids:
        stock_symbol = stock_id.symbol
        (last_season_year, last_season_season) = last_season(today)
        revenueInDb = SeasonProfit.objects.filter(symbol=stock_symbol, year=last_season_year, season=last_season_season)
        if revenueInDb:
            continue
        else:
            url = "http://jsjustweb.jihsun.com.tw/z/zc/zch/zcha_" + stock_symbol + ".djhtm"
            webcode = urllib.urlopen(url)
            soup = BeautifulSoup(webcode, from_encoding='utf-8')
            seasons = soup.find_all('td', {'class':'t3n0'})
            print 'stockid ' + stock_symbol + ' loaded'
            for season_data in seasons:
                year = int(season_data.string.split("Q")[0].split(".")[0]) + 1911
                season = int(season_data.string.split("Q")[0].split(".")[1])
                profit = SeasonProfit()
                profit.surrogate_key = stock_symbol + "_" + str(year) + str(season).zfill(2)
                profit.year = year
                profit.season = season
                if season == 1:
                    profit.date = datetime.date(year, 1, 1)
                elif season == 2:
                    profit.date = datetime.date(year, 4, 1)
                elif season == 3:
                    profit.date = datetime.date(year, 7, 1)
                elif season == 4:
                    profit.date = datetime.date(year, 10, 1)
                profit.symbol = stock_symbol
                next = season_data.next_sibling
                if next.string and next.string != 'N/A':
                    profit.profit = Decimal(next.string.replace(",", ""))
                next = next.next_sibling
                if next.string and next.string != 'N/A':
                    profit.season_growth_rate = Decimal(next.string.replace("%", "").replace(",", ""))
                next = next.next_sibling
                if next.string and next.string != 'N/A':
                    profit.last_year_profit = Decimal(next.string.replace(",", ""))
                next = next.next_sibling
                if next.string and next.string != 'N/A':
                    profit.year_growth_rate = Decimal(next.string.replace("%", "").replace(",", ""))
                next = next.next_sibling
                if next.string and next.string != 'N/A':
                    profit.acc_profit = Decimal(next.string.replace(",", ""))
                next = next.next_sibling
                if next.string and next.string != 'N/A':
                    profit.acc_year_growth_rate = Decimal(next.string.replace("%", "").replace(",", ""))
                profit.save()
    return HttpResponse("update revenue")

def is_decimal(s):
    try:
        Decimal(s)
    except:
        return False
    return True

def update_month_revenue(request):
    today = datetime.date.today() 
    year = today.year
    month = today.month
    if month == 1:
        year = year - 1
        month = 12
    else:
        month = month - 1
    if 'year' in request.GET:
        year = int(request.GET['year'])
    if 'month' in request.GET:
        month = int(request.GET['month'])
    market = ['otc', 'sii']
    for i in range(len(market)):
        url = "http://mops.twse.com.tw/t21/" + market[i] + "/t21sc03_" + str(year-1911) + "_" + str(month) + ".html"
        req = urllib2.Request(url)
        response = urllib2.urlopen(req)
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
                    if is_decimal(revenue_data.string.strip().replace(',', '')):
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
                    # revenue.revenue = datas1[0].strip().replace(',', '')
                    # revenue.last_year_revenue = datas2[0].strip().replace(',', '')
                    # revenue.year_growth_rate = datas2[1].strip().replace(',', '')
                    # revenue.acc_revenue = datas1[2].strip().replace(',', '')
                    # revenue.acc_year_growth_rate = datas2[3].strip().replace(',', '')
                    # revenue.save()
    return HttpResponse('update month revenue year:' + str(year) + " month:" + str(month))

def old_update_month_revenue(request):
    stock_ids = StockId.objects.all()
    today = datetime.date.today()
    for stock_id in stock_ids:
        stock_symbol = stock_id.symbol
        if today.month == 1:
            revenueInDb = MonthRevenue.objects.filter(symbol=stock_symbol, year=today.year-1, month=12)
        else:
            revenueInDb = MonthRevenue.objects.filter(symbol=stock_symbol, year=today.year, month=today.month-1)
        if revenueInDb:
            continue
        else:
            url = "http://jsjustweb.jihsun.com.tw/z/zc/zch/zch_" + stock_symbol + ".djhtm"
            webcode = urllib.urlopen(url)
            soup = BeautifulSoup(webcode, from_encoding='utf-8')
            months = soup.find_all('td', {'class':'t3n0'})
            print 'stockid ' + stock_symbol + ' loaded'
            for month_data in months:
                year = int(month_data.string.split("/")[0]) + 1911
                month = int(month_data.string.split("/")[1])
                revenue = MonthRevenue()
                revenue.surrogate_key = stock_symbol + "_" + str(year) + str(month).zfill(2)
                revenue.year = year
                revenue.month = month
                revenue.date = datetime.date(year, month, 1)
                revenue.symbol = stock_symbol
                next = month_data.next_sibling
                if next.string:
                    revenue.revenue = Decimal(next.string.replace(",", ""))
                next = next.next_sibling
                if next.string:
                    revenue.month_growth_rate = Decimal(next.string.replace("%", "").replace(",", ""))
                next = next.next_sibling
                if next.string:
                    revenue.last_year_revenue = Decimal(next.string.replace(",", ""))
                next = next.next_sibling
                if next.string:
                    revenue.year_growth_rate = Decimal(next.string.replace("%", "").replace(",", ""))
                next = next.next_sibling
                if next.string:
                    revenue.acc_revenue = Decimal(next.string.replace(",", ""))
                next = next.next_sibling
                if next.string:
                    revenue.acc_year_growth_rate = Decimal(next.string.replace("%", "").replace(",", ""))
                revenue.save()
    return HttpResponse("update revenue")

def new_update_dividendupdate_season_revenue(request):
    return HttpResponse("update season revenue")

def update_season_revenue(request):
    if 'year' in request.GET:
        year = int(request.GET['year'])
    else:
        return HttpResponse('please input year')
    if 'season' in request.GET:
        season = int(request.GET['season'])
    else:
        return HttpResponse('please input season')
    if season == 1:
        startMonth = 1
    elif season == 2:
        startMonth = 4
    elif season == 3:
        startMonth = 7
    elif season == 4:
        startMonth = 10
    else:
        return HttpResponse('please input correct season')

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
        revenue = SeasonRevenue()
        revenue.surrogate_key = symbol + '_' + str(year) + str(season).zfill(2)
        revenue.year = year
        revenue.season = season
        revenue.date = date
        revenue.symbol = symbol
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
        print symbol

    return HttpResponse('update season revenue year:' + str(year) + " season:" + str(season))

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

def update_dividend(request):
    print 'hello'
    today = datetime.date.today() 
    year = today.year
    year = 2013
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

def new_update_dividend(request):
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