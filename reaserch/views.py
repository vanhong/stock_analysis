# -*- coding: utf-8 -*-
# Create your views here.


#找出籌碼跟股價 持續 高度相關的
def chip_price_relation(cnt, score, chip_type):
	strDate = 'date'
	strSymbol = 'symbol'
	strYoy = 'year_growth_rate'
	if revenue_type == 'month':
		filter_model = MonthRevenue
		table = 'stocks.stocks_monthrevenue'
	elif revenue_type == 'season':
		filter_model = SeasonRevenue
		table = 'stocks.stocks_seasonrevenue'
	else:
		return Nonetio
	dates = filter_model.objects.values(strDate).distinct().order_by('-' + strDate).values_list(strDate, flat=True)
	cursor = connection.cursor()
	#get the symbols which haven't updated the latest data
	pre_date_str = get_condition_str(dates, 2, cnt+2)
	#print pre_date_str
	query_str = ('SELECT * FROM ( SELECT symbol, AVG(year_growth_rate) avg_yoy from ' + table + ' A'
				' WHERE date in ' + pre_date_str + ' group by symbol) AS A  WHERE avg_yoy >= ' + str(growth_rate))
	cursor.execute(query_str)
	not_update_lists = cursor.fetchall()

	pre_date_str = get_condition_str(dates, 1, cnt+1)
	#print pre_date_str
	query_str = ('SELECT * FROM ( SELECT symbol, AVG(year_growth_rate) avg_yoy from ' + table + ' A'
				' WHERE date in ' + pre_date_str + ' group by symbol) AS B WHERE avg_yoy >= ' + str(growth_rate))
	cursor.execute(query_str)
	update_lists = cursor.fetchall()
	
	print '------Before Union-------'
	results = list(set(update_lists).union(set(not_update_lists)))
	result_symbols = map(lambda item: item[0], results)
	return result_symbols