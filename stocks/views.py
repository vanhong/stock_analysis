#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib, datetime
from django.http import HttpResponse
from HTMLParser import HTMLParser
from bs4 import BeautifulSoup
import time
from decimal import Decimal
from stocks.models import StockId, MonthRevenue, SeasonProfit, Dividend

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

def update_month_revenue(request):
    stock_ids = StockId.objects.all()
    today = datetime.date.today()
    if today.day >= 10:
        last_revenue_day = today.replace(month=today.month-1)
    else:
        last_revenue_day = today.replace(month=today.month-2)
    for stock_id in stock_ids:
        stock_symbol = stock_id.symbol
        revenueInDb = MonthRevenue.objects.filter(symbol=stock_symbol, year=last_revenue_day.year, month=last_revenue_day.month)
        if revenueInDb:
            print 'stockid ' + stock_symbol + ' exists'
        else:
            url = "http://jsjustweb.jihsun.com.tw/z/zc/zch/zch_" + stock_symbol + ".djhtm"
            webcode = urllib.urlopen(url)
            revenue = ParseStockRevenue()
            if webcode.code == 200:
                revenue.feed(webcode.read())
                webcode.close()
            else:
                return HttpResponse("update revenue failed")
            
            if not revenue.totaldata:
                time.sleep(0.5)
                webcode = urllib.urlopen(url)
                revenue.feed(webcode.read())
                webcode.close()

            if revenue.totaldata:
                for i in xrange(len(revenue.totaldata)):
                    totaldata = revenue.totaldata[i]
                    year = int(totaldata[0].split("/")[0]) + 1911
                    month = int(totaldata[0].split("/")[1])
                    monthRevenue = MonthRevenue()
                    monthRevenue.surrogate_key = stock_symbol + "_" + str(year) + str(month).zfill(2)
                    monthRevenue.year = year
                    monthRevenue.month = month
                    monthRevenue.symbol = stock_symbol
                    if totaldata[1] != "nil":
                        monthRevenue.revenue = Decimal(totaldata[1].replace(",", ""))
                    if totaldata[2] != "nil":
                        monthRevenue.month_growth_rate = Decimal(totaldata[2].replace("%", "").replace(",", ""))
                    if totaldata[3] != "nil":
                        monthRevenue.last_year_revenue = Decimal(totaldata[3].replace(",", ""))
                    if totaldata[4] != "nil":
                        monthRevenue.year_growth_rate = Decimal(totaldata[4].replace("%", "").replace(",", ""))
                    if totaldata[5] != "nil":
                        monthRevenue.acc_revenue = Decimal(totaldata[5].replace(",", ""))
                    if totaldata[6] != "nil":
                        monthRevenue.acc_year_growth_rate = Decimal(totaldata[6].replace("%", "").replace(",", ""))
                    monthRevenue.save()
                    """print(str(year) + " " + str(month) + " " + totaldata[1].decode("cp950").encode("utf-8") + " " +
                      totaldata[2].decode("cp950").encode("utf-8") + " " + totaldata[3].decode("cp950").encode("utf-8") + " " +
                      totaldata[4].decode("cp950").encode("utf-8") + " " + totaldata[5].decode("cp950").encode("utf-8") + " " +
                      totaldata[6].decode("cp950").encode("utf-8"))"""
                print("update " + stock_symbol)
    return HttpResponse("update revenue")

def update_season_revenue(request):
    symbol = '1558'
    statements = SeasonIncomeStatement.objects.filter(symbol=symbol).order_by('surrogate_key')
    for statement in statements:
        if statement.season == 1:
            last_season_statement = statements.get(year=statement.year-1, season=4)
        else:
            last_season_statement = statements.get(year=statement.year, season=statement.season-1)
        revenue = SeasonRevenue()
        revenue.year = statement.year
        revenue.season = statement.season
        revenue.symbol = symbol
        revenue.revenue = statement.operating_revenue
    return HttpResponse('not finish')

def update_dividend_new(request):
    stock_symbol = '2454'
    url = "http://jsjustweb.jihsun.com.tw/z/zc/zcc/zcc_" + stock_symbol + ".djhtm"
    web = urllib.urlopen(url)
    soup = BeautifulSoup(web)
    dividend_datas = soup.find_all("td", { "class": "t2" })
    for dividend_data in dividend_datas:
        try:
            year = int(dividend_data.contents[0])
            cash_dividends = dividend_data.next_sibling
            print year
            print cash_dividends
        except:
            print "error"

    return HttpResponse("update dividend")

def update_dividend(request):
    stock_ids = StockId.objects.all()
    for stock_id in stock_ids:
        stock_symbol = stock_id.symbol
        url = "http://jsjustweb.jihsun.com.tw/z/zc/zcc/zcc_" + stock_symbol + ".djhtm"
        web = urllib.urlopen(url)
        dividend_page = ParseDividend()
        if web.code == 200:
            dividend_page.feed(web.read())
            web.close()
        else:
            return HttpResponse("update dividend error")
        if not dividend_page.totaldata:
            time.sleep(0.5)
            web = urllib.urlopen(url)
            dividend_page.feed(web.read())
            web.close()
        if dividend_page.totaldata:
            for i in xrange(len(dividend_page.totaldata)):
                totaldata = dividend_page.totaldata[i]
                dividend = Dividend()
                year = int(totaldata[0]) + 1911
                dividend.year = year
                dividend.surrogate_key = stock_symbol + "_" + str(year)
                dividend.symbol = stock_symbol
                dividend.cash_dividends = Decimal(totaldata[1])
                dividend.stock_dividends_from_retained_earnings = Decimal(totaldata[2])
                dividend.stock_dividends_from_capital_reserve = Decimal(totaldata[3])
                dividend.stock_dividends = Decimal(totaldata[4])
                dividend.total_dividends = Decimal(totaldata[5])
                dividend.employee_stock_rate = Decimal(totaldata[6])
                dividend.save()
            print("update dividend " + stock_symbol)
    return HttpResponse("update dividend")

class ParseDividend(HTMLParser):
    def reset(self):
        HTMLParser.reset(self)
        self.dividendinfo = False
        self.cell = 0
        self.dividenddata = []
        self.totaldata = []

    def handle_starttag(self, tag, attrs):
        if tag == 'td':
            if attrs[0][1] == 't2':
                self.dividendinfo = True
                self.cell %= 7
                self.cell += 1
            elif attrs[0][1] == 't3n1':
                self.dividendinfo = True
                self.cell %= 7
                self.cell += 1
    def handle_endtag(self, tag):
        if tag == 'tr':
            self.dividendinfo = False
            self.cell = 0
        if tag == 'td':
            self.dividendinfo = False
    def handle_data(self, text):
        if self.dividendinfo:
            if text:
                try:
                    data = Decimal(text)
                    self.dividenddata.append(data)
                except:
                    self.cell = 0
                    self.dividenddata = []
                    self.dividendinfo = False
                if self.cell == 7:
                    self.totaldata.append(self.dividenddata)
                    self.dividenddata = []

class ParseStockRevenue(HTMLParser):
    def reset(self):
        HTMLParser.reset(self)
        self.revenueinfo = False
        self.cell = 0
        self.revenuedata = []
        self.totaldata = []

    def handle_starttag(self, tag, attrs):
        if tag == 'td':
            if attrs[0][1] == 't3n0':
                self.revenueinfo = True
                self.cell %= 7
                self.cell += 1
            elif self.revenueinfo == True:
                self.cell %= 7
                self.cell += 1

    def handle_endtag(self, tag):
        if tag == 'tr':
            self.revenueinfo = False
            self.cell = 0
        if self.revenueinfo == True and tag == 'td' and len(self.revenuedata) != 0:
            if len(self.revenuedata) < self.cell:
                self.revenuedata.append("nil")
                if len(self.revenuedata) == 7:
                    self.totaldata.append(self.revenuedata)
                    self.revenuedata = []

    def handle_data(self, text):
        if self.revenueinfo:
            if self.cell < 7:
                if text == []:
                    self.revenuedata.append("nil")
                else:
                    self.revenuedata.append(text.strip())
            elif self.cell == 7:
                if text == []:
                    self.revenuedata.append("nil")
                else:
                    self.revenuedata.append(text.strip())
                self.totaldata.append(self.revenuedata)
                self.revenuedata = []

def update_season_profit(request):
    stock_ids = StockId.objects.all()
    season_revenue = SeasonProfit.objects.all()
    for stock_id in stock_ids:
        stock_symbol = stock_id.symbol
        url = "http://jsjustweb.jihsun.com.tw/z/zc/zch/zcha_" + stock_symbol + ".djhtm"
        webcode = urllib.urlopen(url)
        revenue = ParseStockSeasonRevenue()
        if webcode.code == 200:
            revenue.feed(webcode.read())
            webcode.close()
        else:
            return HttpResponse("update season revenue failed")

        if not revenue.total_data:
            time.sleep(0.5)
            webcode = urllib.urlopen(url)
            revenue.feed(webcode.read())
            webcode.close()
        
        if revenue.total_data:
            for i in xrange(len(revenue.total_data)):
                totaldata = revenue.total_data[i]
                year = int(totaldata[0].split("Q")[0].split(".")[0]) + 1911
                season = int(totaldata[0].split("Q")[0].split(".")[1])
                season_revenue = SeasonProfit()
                season_revenue.surrogate_key = stock_symbol + "_" + str(year) + str(season).zfill(2)
                season_revenue.year = year
                season_revenue.season = season
                season_revenue.symbol = stock_symbol
                if totaldata[1] != "nil" and totaldata[1] != "N/A":
                    season_revenue.profit = Decimal(totaldata[1].replace(",", ""))
                if totaldata[2] != "nil" and totaldata[2] != "N/A":
                    season_revenue.season_growth_rate = Decimal(totaldata[2].replace("%", "").replace(",", ""))
                if totaldata[3] != "nil" and totaldata[3] != "N/A":
                    season_revenue.last_year_profit = Decimal(totaldata[3].replace(",", ""))
                if totaldata[4] != "nil" and totaldata[4] != "N/A":
                    season_revenue.year_growth_rate = Decimal(totaldata[4].replace("%", "").replace(",", ""))
                if totaldata[5] != "nil" and totaldata[5] != "N/A":
                    season_revenue.acc_profit = Decimal(totaldata[5].replace(",", ""))
                if totaldata[6] != "nil" and totaldata[6] != "N/A":
                    season_revenue.acc_year_growth_rate = Decimal(totaldata[6].replace("%", "").replace(",", ""))
                season_revenue.save()
                """print(totaldata[0].decode("cp950").encode("utf-8") + " " + totaldata[1].decode("cp950").encode("utf-8") + " " +
                      totaldata[2].decode("cp950").encode("utf-8") + " " + totaldata[3].decode("cp950").encode("utf-8") + " " +
                      totaldata[4].decode("cp950").encode("utf-8") + " " + totaldata[5].decode("cp950").encode("utf-8") + " " +
                      totaldata[6].decode("cp950").encode("utf-8"))"""
            print("update " + stock_symbol + "season revenue")
    return HttpResponse("update season revenue")

class ParseStockSeasonRevenue(HTMLParser):
    def reset(self):
        HTMLParser.reset(self)
        self.season_revenue_info = False
        self.cell = 0
        self.revenue_data = []
        self.total_data = []

    def handle_starttag(self, tag, attrs):
        if tag == 'td':
            if attrs[0][1] == 't3n0':
                self.season_revenue_info = True
                self.cell %= 7
                self.cell += 1
            elif self.season_revenue_info:
                self.cell %= 7
                self.cell += 1

    def handle_endtag(self, tag):
        if tag == 'tr':
            self.season_revenue_info = False
            self.cell = 0
        if self.season_revenue_info and tag == 'td' and self.revenue_data:
            if len(self.revenue_data) < self.cell:
                self.revenue_data.append('nil')
                if len(self.revenue_data) == 7:
                    self.total_data.append(self.revenue_data)
                    self.revenue_data = []

    def handle_data(self, text):
        if self.season_revenue_info:
            if self.cell < 7:
                self.revenue_data.append(text.strip())
            elif self.cell == 7:
                self.revenue_data.append(text.strip())
                self.total_data.append(self.revenue_data)
                self.revenue_data = []
                

