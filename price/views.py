#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib
import urllib2
from django.http import HttpResponse
from django.db.models import Min, Max
from HTMLParser import HTMLParser
import time
import StringIO
import string
import sys
from datetime import *
from datetime import timedelta
from decimal import Decimal
from stocks.models import StockId
from price.models import *
from price.pivotal_state import *
from bs4 import BeautifulSoup
import pdb
import csv
import ssl
import xmlrpclib

INIT_PIVOTAL_STATE = 'init_pivotal_state'
UPWARD_TREND_STATE = 'upward_trend_state'
DOWNWARD_TREND_STATE = 'downward_trend_state'
NATURAL_REACTION_STATE = 'natural_reaction_state'
NATURAL_RALLY_STATE = 'natural_rally_state'
SECONDARY_REACTION_STATE = 'secondary_reaction_state'
SECONDARY_RALLY_STATE = 'secondary_rally_state'

def show_price(request):
	# a=月份-1(1月:00)
	# b=日期(2日:02)
	# c=年
	# d=月份-1(1月:00)
	# e=日期(2日:02)
	# f=年
	url = 'http://ichart.yahoo.com/table.csv?s=6146.two&a=00&b=01&c=2014&d=12&e=31&f=2015&g=w&ignore=.csv'
	#url = 'http://chart.finance.yahoo.com/table.csv?s=2330.TW&a=2&b=3&c=2016&d=2&e=3&f=2017&g=w&ignore=.csv'
	#url = 'https://finance.yahoo.com/quote/8109.TWO/history?period1=1463992416&period2=1495528416&interval=1d&filter=history&frequency=1d'
	url = 'https://finance.yahoo.com/quote/2330.TW/history?period1=1211558400&period2=9999999999&interval=1wk&filter=history&frequency=1wk'
	#context = ssl._create_unverified_context()
	headers = {'User-Agent': 'Mozilla/5.0'}
	req = urllib2.Request(url)
	response = urllib2.urlopen(req)
	#response = urllib2.urlopen(url)
	data = response.read()
	#array = string.split(data, '\n')
	return HttpResponse(data)

def update_price_by_stockid(request):
	# 如果需要更新，至少更新60天的資料
	try:
		beginValue = request.GET['begin']
		input_begin = datetime.strptime(beginValue, "%Y%m%d")
	except:
		input_begin = date(2008, 1, 2)

	begin = input_begin
	end = datetime.today()
	stockID = request.GET["stockid"]
	lastest_price_date = Price.objects.filter(symbol=stockID).aggregate(Max("date"))
	earliest_price_date = Price.objects.filter(symbol=StockID).aggregate(Min("date"))

	if (earliest_price_date["date__min"]) == None:
		begin = date(2008, 1, 2)
	elif (lastest_price_date["date__max"] < input_begin.date()):
		pass
	else:
		begin = lastest_price_date - timedelta(days=60)

	if not StockId.objects.filter(symbol=stockID):
		return HttpResponse("{0} is not exist".format(stockID))
	# check first day 2008-01-01
	if Price.objects.filter(surrogate_key=stockID+"_"+begin.strftime("%Y%m%d")) and Price.objects.filter(surrogate_key=stockID+"_"+end.strftime("%Y%m%d")):
		return HttpResponse("{0}'s price already exist".format(stockID))
	stock = StockId.objects.get(symbol=stockID)
	if stock.market_type == u"sii":
		inputStock = stockID + ".TW"
	else:
		inputStock = stockID + ".TWO"
	url = 'http://ichart.yahoo.com/table.csv?s={0}&a={1}&b={2}&c={3}&d={4}&e={5}&f={6}&g=w&ignore=.csv'\
		  .format(inputStock, "%02d" %(begin.month-1), begin.day, begin.year, "%02d" %(end.month-1), end.day, end.year)
	response = urllib.urlopen(url)
	data = response.read()
	array = string.split(data, '\n')
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
			priceObj.date = datetime.strptime(dataArr[0], "%Y-%m-%d").date()
			priceObj.symbol = stockID
			priceObj.open_price = dataArr[1]
			priceObj.high_price = dataArr[2]
			priceObj.low_price = dataArr[3]
			priceObj.close_price = dataArr[4]
			priceObj.volume = dataArr[5]
			priceObj.adj_close_price = dataArr[6]
			priceObj.save()
		except :
			print "Exception:", sys.exc_info()[0]
			continue

	return HttpResponse('update {0} history price'.format(stockID))

def update_price(request):
	except_list = ["3266", "3437", "3661", "4171"]
	try:
		input_begin = datetime.strptime(request.GET['begin'], "%Y%m%d")
	except:
		input_begin = date(2008, 1, 2)
	end = datetime.today()
	stock_ids = StockId.objects.all()
	for stock_id in stock_ids:
		begin = input_begin
		lastest_price_date = Price.objects.filter(symbol=stock_id.symbol).aggregate(Max("date"))
		earliest_price_date = Price.objects.filter(symbol=stock_id.symbol).aggregate(Min("date"))
		if (earliest_price_date["date__min"] == None):
			begin = date(2008, 1, 2)
		elif (lastest_price_date["date__max"] < input_begin):
			pass
		else:
			begin = lastest_price_date["date__max"] - timedelta(days=63)
		if stock_id.market_type == u"sii":
			inputStock = stock_id.symbol + ".TW"
		else:
			inputStock = stock_id.symbol + ".TWO"
		if stock_id.symbol in except_list:
			if stock_id.market_type == u"sii":
				inputStock = stock_id.symbol + ".TWO"
			else:
				inputStock = stock_id.symbol + ".TW"
		context = ssl._create_unverified_context()
		url = 'http://ichart.yahoo.com/table.csv?s={0}&a={1}&b={2}&c={3}&d={4}&e={5}&f={6}&g=w&ignore=.csv'\
		  .format(inputStock, "%02d" %(begin.month-1), begin.day, begin.year, "%02d" %(end.month-1), end.day, end.year)
		response = urllib.urlopen(url, context=context)
		data = response.read()
		array = string.split(data, '\n')
		cnt = 0;
		for line in array:
			try:
				if not line:
					continue
				if 'Sorry' in line:
					break
				if 'doctype html public' in line:
					break
				# print 'Ready to save {0}, {1}'.format(stock_id.symbol, line)
				dataArr = line.split(',')
				if dataArr[0] == 'Date':
					continue
				priceObj = Price()
				priceObj.surrogate_key = stock_id.symbol + '_' + dataArr[0].replace('-','')
				priceObj.date = datetime.strptime(dataArr[0], "%Y-%m-%d").date()
				priceObj.symbol = stock_id.symbol
				priceObj.open_price = dataArr[1]
				priceObj.high_price = dataArr[2]
				priceObj.low_price = dataArr[3]
				priceObj.close_price = dataArr[4]
				priceObj.volume = dataArr[5]
				priceObj.adj_close_price = dataArr[6]
				priceObj.save()
				cnt += 1
			except :
				print "Exception:", sys.exc_info()[0]
				continue
		print ('update {0} history price, there has {1} datas'.format(stock_id.symbol, cnt))
	return HttpResponse('update all history price')

def update_pivotal_state_by_stockid(request):
	stock_id = request.GET['stockid']
	stock_prices = Price.objects.filter(symbol=stock_id).order_by('date')
	pivotal_state = InitPivotalState(date=stock_prices[0].date.strftime('%Y-%m-%d'), price=0, symbol=stock_id, prev_state='init_pivotal_state', upward_trend=0 ,\
	                                 downward_trend=0, natural_reaction=0, natural_rally=0, secondary_rally=0, secondary_reaction=0)
	for stock_price in stock_prices:
		pivotal_state = pivotal_state.next(stock_price.close_price, stock_price.date.strftime('%Y-%m-%d'))
		pivotal_state.save_to_db()

	return HttpResponse('update {0} privtal state'.format(stock_id))

def update_pivotal_state(request):
	stock_ids = StockId.objects.all()
	for stock_id in stock_ids:
		cnt = 0
		pivotal_point_count = PivotalPoint.objects.filter(symbol=stock_id.symbol).count()
		if pivotal_point_count < 10:
			stock_prices = Price.objects.filter(symbol=stock_id.symbol).order_by('date')
			if stock_prices.count() == 0:
				print ("update {0} pivotal error, there is no price data".format(stock_id))
				continue
			pivotal_state = InitPivotalState(date=stock_prices[0].date.strftime('%Y-%m-%d'), price=0, symbol=stock_id.symbol, prev_state='init_pivotal_state', upward_trend=0 ,\
	                                         downward_trend=0, natural_reaction=0, natural_rally=0, secondary_rally=0, secondary_reaction=0)
			for stock_price in stock_prices:
				cnt += 1
				pivotal_state = pivotal_state.next(stock_price.close_price, stock_price.date.strftime('%Y-%m-%d'))
				pivotal_state.save_to_db()
			print ('update {0} pivotal state, there has {1} datas'.format(stock_id.symbol, cnt))
		else:
			pivotal_state = PivotalPoint.objects.filter(symbol=stock_id.symbol).order_by("-date")[10]
			stock_prices = Price.objects.filter(symbol=stock_id.symbol, date__gte=pivotal_state.date).order_by("date")
			if (pivotal_state.date != stock_prices[0].date):
				print ("update {0} pivotal error date is not the same".format(stock_id))
			else:
				if pivotal_state.state == INIT_PIVOTAL_STATE:
					pivotal_state = InitPivotalState(date=pivotal_state.date.strftime('%Y-%m-%d'), price=pivotal_state.price, symbol=stock_id.symbol, prev_state=pivotal_state.prev_state, \
													 upward_trend=pivotal_state.upward_trend_point , downward_trend=pivotal_state.downward_trend_point, natural_reaction=pivotal_state.natural_reaction_point, \
													 natural_rally=pivotal_state.natural_rally_point, secondary_rally=pivotal_state.secondary_rally_point, secondary_reaction=pivotal_state.secondary_reaction_point)
				elif pivotal_state.state == UPWARD_TREND_STATE:
					pivotal_state = UpwardTrendState(date=pivotal_state.date.strftime('%Y-%m-%d'), price=pivotal_state.price, symbol=stock_id.symbol, prev_state=pivotal_state.prev_state, \
													 upward_trend=pivotal_state.upward_trend_point , downward_trend=pivotal_state.downward_trend_point, natural_reaction=pivotal_state.natural_reaction_point, \
													 natural_rally=pivotal_state.natural_rally_point, secondary_rally=pivotal_state.secondary_rally_point, secondary_reaction=pivotal_state.secondary_reaction_point)
				elif pivotal_state.state == DOWNWARD_TREND_STATE:
					pivotal_state = DownwardTrendState(date=pivotal_state.date.strftime('%Y-%m-%d'), price=pivotal_state.price, symbol=stock_id.symbol, prev_state=pivotal_state.prev_state, \
													 upward_trend=pivotal_state.upward_trend_point , downward_trend=pivotal_state.downward_trend_point, natural_reaction=pivotal_state.natural_reaction_point, \
													 natural_rally=pivotal_state.natural_rally_point, secondary_rally=pivotal_state.secondary_rally_point, secondary_reaction=pivotal_state.secondary_reaction_point)
				elif pivotal_state.state == NATURAL_RALLY_STATE:
					pivotal_state = NaturalRallyState(date=pivotal_state.date.strftime('%Y-%m-%d'), price=pivotal_state.price, symbol=stock_id.symbol, prev_state=pivotal_state.prev_state, \
													 upward_trend=pivotal_state.upward_trend_point , downward_trend=pivotal_state.downward_trend_point, natural_reaction=pivotal_state.natural_reaction_point, \
													 natural_rally=pivotal_state.natural_rally_point, secondary_rally=pivotal_state.secondary_rally_point, secondary_reaction=pivotal_state.secondary_reaction_point)
				elif pivotal_state.state == NATURAL_REACTION_STATE:
					pivotal_state = NaturalReactionState(date=pivotal_state.date.strftime('%Y-%m-%d'), price=pivotal_state.price, symbol=stock_id.symbol, prev_state=pivotal_state.prev_state, \
													 upward_trend=pivotal_state.upward_trend_point , downward_trend=pivotal_state.downward_trend_point, natural_reaction=pivotal_state.natural_reaction_point, \
													 natural_rally=pivotal_state.natural_rally_point, secondary_rally=pivotal_state.secondary_rally_point, secondary_reaction=pivotal_state.secondary_reaction_point)
				elif pivotal_state.state == SECONDARY_RALLY_STATE:
					pivotal_state = SecondaryRallyState(date=pivotal_state.date.strftime('%Y-%m-%d'), price=pivotal_state.price, symbol=stock_id.symbol, prev_state=pivotal_state.prev_state, \
													 upward_trend=pivotal_state.upward_trend_point , downward_trend=pivotal_state.downward_trend_point, natural_reaction=pivotal_state.natural_reaction_point, \
													 natural_rally=pivotal_state.natural_rally_point, secondary_rally=pivotal_state.secondary_rally_point, secondary_reaction=pivotal_state.secondary_reaction_point)
				elif pivotal_state.state == SECONDARY_REACTION_STATE:
					pivotal_state = SecondaryReactionState(date=pivotal_state.date.strftime('%Y-%m-%d'), price=pivotal_state.price, symbol=stock_id.symbol, prev_state=pivotal_state.prev_state, \
													 upward_trend=pivotal_state.upward_trend_point , downward_trend=pivotal_state.downward_trend_point, natural_reaction=pivotal_state.natural_reaction_point, \
													 natural_rally=pivotal_state.natural_rally_point, secondary_rally=pivotal_state.secondary_rally_point, secondary_reaction=pivotal_state.secondary_reaction_point)
				else:
					print ("update {0} pivotal error: can't find state".format(stock_id))
				for stock_price in stock_prices:
					if (stock_price.date != pivotal_state.date):
						pivotal_state = pivotal_state.next(stock_price.close_price, stock_price.date.strftime('%Y-%m-%d'))
						pivotal_state.save_to_db()
						# print ('update {0} pivotal state, there has {1} datas'.format(stock_id.symbol, cnt))
						cnt += 1
				if cnt != 11:
					print ('update {0} pivotal state, there has {1} datas'.format(stock_id.symbol, cnt))
	return HttpResponse('update pivotal state')

def download_csv2(request):
	encode = request.GET.get('encode', 'big5')

	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename="test.csv"'

	writer = csv.writer(response, delimiter=',', quotechar='"')
	header = [u'H1', u'H2', u'H3']
	writer.writerow([x.encode(encode) for x in header])
	return response

#201201開始
def download_csv(request):
	start_date = date(2016, 1, 1)
	pivotal_point = PivotalPoint.objects.filter(date__gte=start_date)
	sample_points = pivotal_point.filter(symbol='2330').order_by('date')
	encode = request.GET.get('encode', 'big5')

	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename="test.csv"'

	writer = csv.writer(response, delimiter=',', quotechar='"')
	header = ['StockID','Name']
	for p in sample_points:
		header.append(p.date)
	header.append('current')
	writer.writerow([x for x in header])
	stock_ids = ['2610','2618','2612','2606','2208',
			'2330','6286','2337','3041','2458',
			'5483','3556',
			'2353','2324','3231','2382','2376',
			'2357','4938','2395','3022','6206',
			'2474','2387','6121','8210','3611',
			'2308','2420','2457','2327','2428',
			'6269','2383','3044','3037','2462',
			'6224','6279','3299','8042','8091',
			'3390','2317','6192','6146','3552',
			'3563','2393','6278','2486','2374',
			'5392','3454','3615','6231','5209',
			'3546','5478','2412','3045','4904',
			'2450','2345','2455','5388','3068',
			'3234','6143','6263','3702','3010',
			'6281','1535','1521','1525','1531',
			'4526','4532','8374','1580','6122',
			'1558','3379','8083','4528','2002',
			'1101','1102','1301','1303','1304',
			'1308','1326','1307','1325','6508',
			'1723','1710','1704','4725','1742',
			'2103','2105','2106','2108','6505',
			'6184','9904','9939','9925','9917',
			'9921','9914','9941','9924','5312',
			'1216','1201','1227','1232','1233',
			'1231','4205','1402','1477','1476',
			'4401','2912','5904','1707','1733',
			'3164','1788','4126','8940','2201',
			'2207','2548','5522','2820','2881','2886','2449','1452','6202']
	for stock_id in stock_ids:
		if (StockId.objects.filter(symbol__contains=stock_id)):
			stockId = StockId.objects.get(symbol=stock_id)
			prev_point_state = ''
			body = [stock_id]
			body.append(stockId.name)
			points = pivotal_point.filter(symbol=stock_id).order_by('date')
			if (points.count() < sample_points.count()):
				for i in range(sample_points.count() - points.count()):
					body.append('')
			for p in points:
				if (p.state != prev_point_state):
					body.append(str(p.price) + u'_' + p.state)
				else:
					body.append(str(p.price))
				prev_point_state = p.state
			body.append(p.state)
			writer.writerow([x.encode("cp950") for x in body])
	#body =['2330']
	#for b in sample_points:
	#	if (b.state != prev_point_state):
	#		body.append(str(b.price) + u'_' + b.state)
	#	else:
	#		body.append(str(b.price))
	#	prev_point_state = b.state
	#body.append(b.state)
	#writer.writerow([x for x in body])
	return response












