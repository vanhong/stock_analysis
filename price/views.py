#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib
import urllib2
from django.http import HttpResponse
from HTMLParser import HTMLParser
import time
import StringIO
import string
import sys
from datetime import *
from decimal import Decimal
from stocks.models import StockId
from price.models import *
from bs4 import BeautifulSoup
import pdb

def show_price(request):
	# a=月份-1(1月:00)
	# b=日期(2日:02)
	# c=年
	# d=月份-1(1月:00)
	# e=日期(2日:02)
	# f=年
	url = 'http://ichart.yahoo.com/table.csv?s=6146.two&a=00&b=01&c=2014&d=12&e=31&f=2015&g=d&ignore=.csv'
	response = urllib.urlopen(url)
	data = response.read()
	array = string.split(data, '\n')
	return HttpResponse(array)

def update_price_by_stockid(request):
	try:
		beginValue = request.GET['begin']
		begin = datetime.strptime(beginValue, "%Y%m%d")
	except:
		today = datetime.today()
		begin = date(today.year-1, today.month, today.day)
	end = datetime.today()
	stockID = request.GET['stockid']
	if not StockId.objects.filter(symbol=stockID):
		return HttpResponse("{0} is not exist".format(stockID))
	if Price.objects.filter(surrogate_key=stockID+"_"+begin.strftime("%Y%m%d")) and Price.objects.filter(surrogate_key=stockID+"_"+end.strftime("%Y%m%d")):
		return HttpResponse("{0}'s price already exist".format(stockID))
	stock = StockId.objects.get(symbol=stockID)
	if stock.market_type == u"上市":
		inputStock = stockID + ".TW"
	else:
		inputStock = stockID + ".TWO"
	url = 'http://ichart.yahoo.com/table.csv?s={0}&a={1}&b={2}&c={3}&d={4}&e={5}&f={6}&g=d&ignore=.csv'\
		  .format(inputStock, "%02d" %(begin.month-1), begin.day, begin.year, "%02d" %(end.month-1), end.day, end.year)
	response = urllib.urlopen(url)
	data = response.read()
	array = string.split(data, '\n')
	pdb.set_trace()
	for line in array:
		try:
			if not line:
				continue
			if 'Sorry' in line:
				break
			if 'doctype html public' in line:
				break
			print 'Ready to save {0}, {1}'.format(stockID, line)
			dataArr = line.split(',')
			if dataArr[0] == 'Date':
				continue
			priceObj = Price()
			priceObj.surrogate_key = stockID + '_' + dataArr[0].replace('-','')
			priceObj.trade_date = dataArr[0].replace('-','')
			priceObj.symbol = stockID
			priceObj.openp = dataArr[1]
			priceObj.highp = dataArr[2]
			priceObj.lowp = dataArr[3]
			priceObj.closep = dataArr[4]
			priceObj.quantity = dataArr[5]
			priceObj.adjp = dataArr[6]
			priceObj.save()
		except :
			print "Exception:", sys.exc_info()[0]
			continue

	return HttpResponse('update {0} history price'.format(stockID))


def update_price(request):
	begin = request.GET['begin']
	end = request.GET['end']
	startNo = 0
	if 'no' in request.GET:
		startNo = request.GET['no']

	print 'Ready to update_price, begin=' + begin + ', end=' + end
	stock_ids = StockId.objects.all()
	for stock_id in stock_ids:
		no = stock_id.symbol
		
		if no < startNo:
			print no + 'continue'
			continue
	# a=月份-1(1月:00)
	# b=日期(2日:02)
	# c=年
	# d=月份-1(1月:00)
	# e=日期(2日:02)
	# f=年
		url = 'http://ichart.yahoo.com/table.csv?s={0}.two&a=00&b=31&c={1}&d=12&e=31&f={2}&g=5&ignore=.csv'.format(no, begin, end)
		response = urllib.urlopen(url)
		data = response.read()

		array = string.split(data, '\n')
		#line = buf.readline()
		print len(array)
		for line in array:
			try:
				if not line:
					continue
				if 'Sorry' in line:
					break
				if 'doctype html public' in line:
					break;
				print 'Ready to save {0}, {1}'.format(no, line)
				#pdb.set_trace()
				dataArr = line.split(',')
				if dataArr[0] == 'Date':
					continue
				priceObj = Price()
				priceObj.surrogate_key = no + '_' + dataArr[0].replace('-','')
				priceObj.trade_date = dataArr[0].replace('-','')
				priceObj.symbol = no
				priceObj.openp = dataArr[1]
				priceObj.highp = dataArr[2]
				priceObj.lowp = dataArr[3]
				priceObj.closep = dataArr[4]
				priceObj.quantity = dataArr[5]
				priceObj.adjp = dataArr[6]
				priceObj.save()
				print 'save ' + priceObj.surrogate_key
			except :
				print "Exception:", sys.exc_info()[0]
				continue
	return HttpResponse('update_price')