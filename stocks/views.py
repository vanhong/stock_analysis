#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib, datetime
from django.http import HttpResponse
from HTMLParser import HTMLParser
from bs4 import BeautifulSoup
import time
from decimal import Decimal
from stocks.models import StockId, MonthRevenue, SeasonProfit, Dividend, SeasonRevenue
from financial.models import SeasonIncomeStatement
from django.db.models import Sum

def update_stock_id(request):
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

def update_month_revenue(request):
    stock_ids = StockId.objects.all()
    today = datetime.date.today()
    for stock_id in stock_ids:
        stock_symbol = stock_id.symbol
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

def update_season_revenue(request):
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
    stock_ids = StockId.objects.all()
    for stock_id in stock_ids:
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

    return HttpResponse("update dividend")