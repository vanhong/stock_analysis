# Create your views here.
import urllib
import urllib2
from django.http import HttpResponse
from HTMLParser import HTMLParser
import time
import StringIO
import string
from datetime import *
from decimal import Decimal
from stocks.models import StockId
from price.models import *
from bs4 import BeautifulSoup

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
				print 'Ready to save ' + no + ', ' + line
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
				print line + ", Exception:" + sys.exc_info()[0]
				continue

		#print the_page
		'''soup = BeautifulSoup(the_page)

		dataDic = {}
		for security in securityIdList:
			securityStr = security.strip()
			buyCnt = security.next.string.replace(',','')
			sellCnt = security.next.next_sibling.string.replace(',','')
			dataObj = CorpTradeData(dateFrom.replace('-','') + '_' + security, dateFrom.replace('-',''), security, buyCnt, sellCnt,'0','0','0','0' )
			dataDic[securityStr] = dataObj
			#print('%s, %s, %s' % (security, dataDic[securityStr].dealer_buy, dataDic[securityStr].dealer_sell))

		print('After parsing Dealer, stock count=' + str(len(dataDic)))'''