#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib
import datetime
from django.http import HttpResponse
from HTMLParser import HTMLParser
import time
from decimal import Decimal
from stocks.models import StockId, RevenueName, Revenue

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

def update_revenue(request):
    stockids = StockId.objects.all()
    today = datetime.date.today()
    if today.day >= 10:
        last_revenue_day = today.replace(month=today.month-1)
    else:
        last_revenue_day = today.replace(month=today.month-2)
    for stockid in stockids:
        revenue_in_db = Revenue.objects.filter(symbol=stockid.symbol, year=last_revenue_day.year, month=last_revenue_day.month)
        print str(stockid) + ' ' + str(last_revenue_day.year) + ' ' + str(last_revenue_day.month)

        if revenue_in_db:
            print 'stockid ' + stockid.symbol + ' exists'

        if not revenue_in_db:
            symbol = stockid.symbol
            url = "http://jsjustweb.jihsun.com.tw/z/zc/zch/zch_" + symbol + ".djhtm"
            webcode = urllib.urlopen(url)
            revenues = ParseStockRevenue()
            if webcode.code == 200:
                revenues.feed(webcode.read())
                webcode.close()
            else:
                return HttpResponse("update revenue failed")

            if not revenues.totaldata:
                time.sleep(0.5)
                webcode = urllib.urlopen(url)
                revenues = ParseStockRevenue()  

            if revenues.totaldata:
                revenue_name = RevenueName()
                for i in xrange(len(revenues.totaldata)):
                    totaldata = revenues.totaldata[i]
                    print(totaldata)
                    year = int(totaldata[0].split("/")[0]) + 1911
                    month = int(totaldata[0].split("/")[1])
                    key = symbol + '_' + str(year) + str(month).zfill(2) + '_M_'
                    revenue = Revenue()
                    revenue.symbol = symbol
                    revenue.year = year
                    revenue.season = 0
                    revenue.month = month
                    revenue.time_type = 'M'
                    if totaldata[1] != 'nil':
                        revenue.name = revenue_name.revenue
                        revenue.surrogate_key = key + revenue.name
                        revenue.value = str(Decimal(totaldata[1].replace(",", "")) * 1000)
                        revenue.save()
                    if totaldata[2] != 'nil':
                        revenue.name = revenue_name.growth_rate
                        revenue.surrogate_key = key + revenue.name
                        revenue.value = str(Decimal(totaldata[2].replace("%", "").replace(",", "")) / 100)
                        revenue.save()
                    if totaldata[3] != 'nil':
                        revenue.name = revenue_name.last_year_revenue
                        revenue.surrogate_key = key + revenue.name
                        revenue.value = str(Decimal(totaldata[3].replace(",", "")) * 1000)
                        revenue.save()
                    if totaldata[4] != 'nil':
                        revenue.name = revenue_name.year_growth_rate
                        revenue.surrogate_key = key + revenue.name
                        revenue.value = str(Decimal(totaldata[4].replace("%", "").replace(",", "")) / 100)
                        revenue.save()
                    if totaldata[5] != 'nil':
                        revenue.name = revenue_name.acc_revenue
                        revenue.surrogate_key = key + revenue.name
                        revenue.value = str(Decimal(totaldata[5].replace(",", "")) * 1000)
                        revenue.save()
                    if totaldata[6] != 'nil':
                        revenue.name = revenue_name.acc_year_growth_rate
                        revenue.surrogate_key = key + revenue.name
                        revenue.value = str(Decimal(totaldata[6].replace("%", "").replace(",", "")) / 100)
                        revenue.save()
            print("update " + symbol)
    return HttpResponse("update revenue")

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
                
