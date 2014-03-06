#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib
import urllib2
from django.http import HttpResponse
from HTMLParser import HTMLParser
import time
from datetime import *
from decimal import Decimal
from stocks.models import StockId
from chip.models import *
from bs4 import BeautifulSoup

# Create your views here.
def update_corp_trade(request):
    print 'Ready to update_corp_trade'
    dateFrom = ''
    dateTo = ''
    if 'to' in request.GET and  'from' in request.GET:
        dateFrom = request.GET['from']
        dateTo = request.GET['to']
    elif 'from' in request.GET:
        dateFrom = request.GET['from']
        dateTo = dateFrom
    else:
        dateFrom = (date.today() - timedelta(1)).strftime('%Y-%m-%d')
        dateTo = dateFrom
    d = datetime.strptime(dateFrom,'%Y-%m-%d').date()
    end_date = datetime.strptime(dateTo,'%Y-%m-%d').date()
    delta = timedelta(days=1)
    while d <= end_date:
        dateFrom = d.strftime("%Y-%m-%d")

        print('Start to Fetch ' + dateFrom + ' Data')
        d += delta
        #Dealer
        url = 'http://www.twse.com.tw/en/trading/fund/TWT43U/TWT43U.php'
        values = {'qdate' : dateFrom.replace('-','/'), 'Submit22222' : 'Query'}
        data = urllib.urlencode(values)
        req = urllib2.Request(url, data)
        response = urllib2.urlopen(req)
        the_page = response.read()
        #print(the_page)
        soup = BeautifulSoup(the_page)
        securityIdList = [td.string for td in soup.findAll('td', {'align' : 'center'})]
        buyCnt = 0 
        sellCnt = 0
        dataDic = {}
        for security in securityIdList:
            securityStr = security.strip()
            if securityStr == '':
                continue
            buyCnt = security.next.string.replace(',','')
            sellCnt = security.next.next_sibling.string.replace(',','')
            dataObj = CorpTradeData(dateFrom.replace('-','') + '_' + securityStr, dateFrom.replace('-',''), security, buyCnt, sellCnt,'0','0','0','0' )
            dataDic[securityStr] = dataObj
            #print('%s, %s, %s' % (security, dataDic[securityStr].dealer_buy, dataDic[securityStr].dealer_sell))

        print('After parsing Dealer, stock count=' + str(len(dataDic)))

        #security trust
        url = 'http://www.twse.com.tw/en/trading/fund/TWT44U/genpage/A441{}.php'.format(dateFrom.replace('-',''))
        response = urllib.urlopen(url)
        the_page = response.read()
        soup = BeautifulSoup(the_page)
        securityIdList = [div.string for div in soup.findAll('div', {'align' : 'center'})]

        #print(securityIdList)
        start = False
        for security in securityIdList:
            if security == 'Difference':
                start = True

            if start is False or security == 'Difference':
                continue

            securityStr = security.strip()
            if securityStr == '':
                continue
            buyCnt = security.next.next.string.replace(',','')
            sellCnt = security.next.next.next_sibling.string.replace(',','')
            if dataDic.has_key(securityStr) is False:
                dataObj = CorpTradeData(dateFrom.replace('-','') + '_' + security, dateFrom.replace('-',''), security, '0', '0', buyCnt, sellCnt,'0','0' )
                dataDic[securityStr] = dataObj
            else:
                dataDic[securityStr].security_buy = buyCnt
                dataDic[securityStr].security_sell = sellCnt
            #print('no=', securityStr)
            #print('buy=', buyCnt)
            #print('sell=', sellCnt)
            #print('%s, %s, %s' % (security, dataDic[securityStr].security_buy, dataDic[securityStr].security_sell))
        print('After parsing Trust, stock count=' + str(len(dataDic)))

        #foreign http://www.twse.com.tw/en/trading/fund/TWT38U/TWT38U.php
        url = 'http://www.twse.com.tw/en/trading/fund/TWT38U/TWT38U.php'
        values = {'qdate' : dateFrom.replace('-','/'), 'Submit22222' : 'Query'}
        data = urllib.urlencode(values)
        req = urllib2.Request(url, data)
        response = urllib2.urlopen(req)
        the_page = response.read()
        #print(the_page)
        soup = BeautifulSoup(the_page)
        securityIdList = [td.string for td in soup.findAll('td', {'align' : 'center'})]
        for security in securityIdList:
            securityStr = security.strip()
            if securityStr == '':
                continue
            buyCnt = security.next.string.replace(',','')
            sellCnt = security.next.next_sibling.string.replace(',','')
            if dataDic.has_key(securityStr) is False:
                dataObj = CorpTradeData(dateFrom.replace('-','') + '_' + securityStr, dateFrom.replace('-',''), security, '0', '0','0','0',buyCnt,sellCnt )
                dataDic[securityStr] = dataObj
            else:
                dataDic[securityStr].foreign_buy = buyCnt
                dataDic[securityStr].foreign_sell = sellCnt

        print('After parsing Foreign, stock count=' + str(len(dataDic)))

        ### Insert DB
        for key, value in dataDic.items():
            if value.symbol == '' or value.symbol == '*':
                continue
            corpTrade = CorpTrade()
            corpTrade.surrogate_key = value.surrogate_key
            corpTrade.date = datetime.strptime(value.trade_date, '%Y%m%d')
            corpTrade.symbol = value.symbol
            corpTrade.dealer_buy = value.dealer_buy
            corpTrade.dealer_sell    = value.dealer_sell
            corpTrade.security_buy = value.security_buy
            corpTrade.security_sell = value.security_sell
            corpTrade.foreign_buy = value.foreign_buy
            corpTrade.foreign_sell = value.foreign_sell
            corpTrade.save()
            #print ('update ' + value.trade_date + ', ' + key + ' corp trade')
        
    return HttpResponse('%s, %s, %s' % (securityIdList[0], securityIdList[0].next, securityIdList[0].next.next_sibling))

def update_shareholder_structure(request):

    if 'date' in request.GET:
        query_date = request.GET['date']
    else:
        now = datetime.now()
        query_date = str(now.year) + str(now.month) + '02'

    url = 'http://www.tdcc.com.tw/smWeb/QryStock.jsp'
    sub = "%ACd%B8%DF"
    stock_ids = StockId.objects.all()
    print stock_ids
    for stock_id in stock_ids:
        stock_symbol = stock_id.symbol
        values = {
            'SCA_DATE':query_date, 'SqlMethod':'StockNo', 'StockNo':stock_symbol, 
            'StockName': '', 'sub': urllib.unquote(sub)
        }
        print values
        url_data = urllib.urlencode(values)
        req = urllib2.Request(url, url_data)
        response = urllib2.urlopen(req)
        #print response.read()
        the_page = response.read()

    return HttpResponse(the_page)

def test_chip(request):
    url = 'http://www.tdcc.com.tw/smWeb/QryStock.jsp'
    sub = "%ACd%B8%DF"
    print sub
    values = {
        'SCA_DATE':'20131202', 'SqlMethod':'StockNo', 'StockNo':'2330', 
        'StockName': '', 'sub': urllib.unquote(sub)
    }
    url_data = urllib.urlencode(values)
    req = urllib2.Request(url, url_data)
    response = urllib2.urlopen(req)
    # print response.read()
    return HttpResponse(response.read())

def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)

