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
import pdb

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
    monthcount = 1
    if 'monthcount' in request.GET:
        monthcount = request.GET['monthcount']

    print 'monthcount = %s' % (monthcount)
    url = 'http://www.tdcc.com.tw/smWeb/QryStock.jsp'
    sub = "%ACd%B8%DF"
    values = {}
    url_data = urllib.urlencode(values)
    req = urllib2.Request(url, url_data)
    response = urllib2.urlopen(req)
    soup = BeautifulSoup(response,from_encoding="utf-8")
    options = [option.string for option in soup.findAll('option')]
    print options

    pdb.set_trace() #中斷點
    stock_ids = StockId.objects.all()
    cnt = 1
    for dateStr in options:
        for stock_id in stock_ids:
            stock_symbol = stock_id.symbol
            print 'process %s %s' % (dateStr, stock_symbol)
            dateForKey = dateStr[:6]
            key = '%s_%s_%s' % (dateForKey,stock_symbol,'person')
            obj = ShareholderStructure.objects.values('surrogate_key').filter(surrogate_key=key)
            print 'query length = %d' % (len(obj))
            if len(obj) < 1:
                values = {
                    'SCA_DATE':dateStr, 'SqlMethod':'StockNo', 'StockNo':stock_symbol, 
                    'StockName': '', 'sub': urllib.unquote(sub)
                }
                url_data = urllib.urlencode(values)
                req = urllib2.Request(url, url_data)
                response = urllib2.urlopen(req)
                soup = BeautifulSoup(response,from_encoding="utf-8")
                dataList = [td.string for td in soup.findAll('td', {'align' : 'right'})]
                person = []
                share = []
                ratio = []
                if len(dataList) < 10:
                    continue
                for i in range(0, 16):
                    person.append(dataList[i*3].replace(',',''))
                    share.append(dataList[1 + i*3].replace(',',''))
                    ratio.append(dataList[2 + i*3].replace(',',''))

                shareholderStructure = ShareholderStructure()
                shareholderStructure.surrogate_key = '%s_%s_%s' % (dateForKey,stock_symbol,'person')
                shareholderStructure.date = dateForKey
                shareholderStructure.symbol = stock_symbol
                shareholderStructure.data_kind = 'person'
                shareholderStructure.value0_1 = person[0]
                shareholderStructure.value1_5 = person[1]
                shareholderStructure.value5_10 = person[2]
                shareholderStructure.value10_15 = person[3]
                shareholderStructure.value15_20 = person[4]
                shareholderStructure.value20_30 = person[5]
                shareholderStructure.value30_40 = person[6]
                shareholderStructure.value40_50 = person[7]
                shareholderStructure.value50_100 = person[8]
                shareholderStructure.value100_200 = person[9]
                shareholderStructure.value200_400 = person[10]
                shareholderStructure.value400_600 = person[11]
                shareholderStructure.value600_800 = person[12]
                shareholderStructure.value800_1000 = person[13]
                shareholderStructure.value1000 = person[14]
                shareholderStructure.value_sum = person[15]
                shareholderStructure.save()

                shareholderStructure = ShareholderStructure()
                shareholderStructure.surrogate_key = '%s_%s_%s' % (dateForKey,stock_symbol,'share')
                shareholderStructure.date = dateForKey
                shareholderStructure.symbol = stock_symbol
                shareholderStructure.data_kind = 'share'
                shareholderStructure.value0_1 = share[0]
                shareholderStructure.value1_5 = share[1]
                shareholderStructure.value5_10 = share[2]
                shareholderStructure.value10_15 = share[3]
                shareholderStructure.value15_20 = share[4]
                shareholderStructure.value20_30 = share[5]
                shareholderStructure.value30_40 = share[6]
                shareholderStructure.value40_50 = share[7]
                shareholderStructure.value50_100 = share[8]
                shareholderStructure.value100_200 = share[9]
                shareholderStructure.value200_400 = share[10]
                shareholderStructure.value400_600 = share[11]
                shareholderStructure.value600_800 = share[12]
                shareholderStructure.value800_1000 = share[13]
                shareholderStructure.value1000 = share[14]
                shareholderStructure.value_sum = share[15]
                shareholderStructure.save()

                shareholderStructure = ShareholderStructure()
                shareholderStructure.surrogate_key = '%s_%s_%s' % (dateForKey,stock_symbol,'ratio')
                shareholderStructure.date = dateForKey
                shareholderStructure.symbol = stock_symbol
                shareholderStructure.data_kind = 'ratio'
                shareholderStructure.value0_1 = ratio[0]
                shareholderStructure.value1_5 = ratio[1]
                shareholderStructure.value5_10 = ratio[2]
                shareholderStructure.value10_15 = ratio[3]
                shareholderStructure.value15_20 = ratio[4]
                shareholderStructure.value20_30 = ratio[5]
                shareholderStructure.value30_40 = ratio[6]
                shareholderStructure.value40_50 = ratio[7]
                shareholderStructure.value50_100 = ratio[8]
                shareholderStructure.value100_200 = ratio[9]
                shareholderStructure.value200_400 = ratio[10]
                shareholderStructure.value400_600 = ratio[11]
                shareholderStructure.value600_800 = ratio[12]
                shareholderStructure.value800_1000 = ratio[13]
                shareholderStructure.value1000 = ratio[14]
                shareholderStructure.value_sum = ratio[15]
                shareholderStructure.save()
                print 'save %s %s !!!' % (dateStr, stock_symbol)
        cnt += 1
        if cnt > monthcount:
            break
    # print response.read()
    return HttpResponse(dataList[0])


def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)

