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