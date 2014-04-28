# Create your views here.
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


# q(quit)：離開
# p [some variable](print)：秀某個變數的值
# n(next line)：下一行
# c(continue)：繼續下去
# s(step into)：進入函式
# r(return): 到本函式的return敘述式
# l(list)：秀出目前所在行號
# !： 改變變數的值

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
		url = 'http://ichart.yahoo.com/table.csv?s={0}.tw&a=01&b=03&c={1}&d=11&e=30&f={2}&g=5&ignore=.csv'.format(no, begin, end)
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
				priceObj.surrogate_key = dataArr[0].replace('-','') + '_' + no
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

		#print the_page