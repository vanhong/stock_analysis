#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib2
import urllib
from urllib2 import URLError
from django.http import HttpResponse, Http404
from HTMLParser import HTMLParser
import time
from decimal import Decimal
from stocks.models import StockId
from financial.models import SeasonFinancialRatio, SeasonBalanceSheet, SeasonIncomeStatement, YearFinancialRatio, SeasonCashFlowStatement
from stocks.models import SeasonRevenue
from bs4 import BeautifulSoup
import html5lib
import datetime
import json
from django.db.models import Sum
from core.utils import st_to_decimal, season_to_date, last_season
import pdb

#already got certification's financial report
def test_financial_company(request):
    url = 'http://mops.twse.com.tw/mops/web/t163sb14'
    values = {'encodeURIComponent': '1', 'step': '1', 'firstin': '1', 'off': '1', 
              'TYPEK': 'sii', 'year': '103', 'season': '02'} 
    url_data = urllib.urlencode(values)
    req = urllib2.Request(url, url_data)
    response = urllib2.urlopen(req)
    return HttpResponse(response.read())

#get already update financial report's stockID
def get_updated_id(year, season):
    url = 'http://mops.twse.com.tw/mops/web/t163sb14'
    values = {'encodeURIComponent': '1', 'step': '1', 'firstin': '1', 'off': '1', 
              'TYPEK': 'otc', 'year': str(year-1911), 'season': str(season).zfill(2)} 
    url_data = urllib.urlencode(values)
    req = urllib2.Request(url, url_data)
    try:
        response = urllib2.urlopen(req)
    except URLError, e:
        if hasattr(e, "reason"):
            print("get update stockIDs error" + " Reason:"), e.reason
        elif hasattr(e, "code"):
            print("get update stockIDs error" + " Error code:"), e.code
        return []
    soup = BeautifulSoup(response, from_encoding = "utf-8")
    table = soup.find('table', attrs={'class': 'hasBorder'})
    trs = table.find_all('tr')
    company_list = []
    for tr in trs:
        td = tr.find('td')
        if td and len(td.string) == 4:
            company_list.append(unicode(td.string))

    values = {'encodeURIComponent': '1', 'step': '1', 'firstin': '1', 'off': '1', 
              'TYPEK': 'sii', 'year': str(year-1911), 'season': str(season).zfill(2)} 
    url_data = urllib.urlencode(values)
    req = urllib2.Request(url, url_data)
    try:
        response = urllib2.urlopen(req)
    except URLError, e:
        if hasattr(e, "reason"):
            print("get update stockIDs error" + " Reason:"), e.reason
        elif hasattr(e, "code"):
            print("get update stockIDs error" + " Error code:"), e.code
        return []
    soup = BeautifulSoup(response, from_encoding = "utf-8")
    table = soup.find('table', attrs={'class': 'hasBorder'})
    trs = table.find_all('tr')
    for tr in trs:
        td = tr.find('td')
        if td and len(td.string) == 4:
            company_list.append(unicode(td.string))
    return company_list

#income statement from TWSE 綜合損益表
def show_season_income_statement(request):
    url = 'http://mops.twse.com.tw/mops/web/ajax_t163sb04'
    values = {'encodeURIComponent' : '1', 'step' : '1', 'firstin' : '1', 'off' : '1',
              'TYPEK' : 'sii', 'year' : '102', 'season' : '01'}
    url_data = urllib.urlencode(values)
    req = urllib2.Request(url, url_data)
    response = urllib2.urlopen(req)
    return HttpResponse(response.read())

#綜合損益表
def update_season_income_statement(request):
    if 'date' in request.GET:
        date = request.GET['date']
        if date != '':
            try:
                str_year, str_season = date.split('-')
                year = int(str_year)
                season = int(str_season)
            except:
                json_obj = json.dumps({"notes": "please input correct season 'year-season'"})
                return HttpResponse(json_obj, content_type="application/json")
        else:
            json_obj = json.dumps({"notes": "please input correct season 'year-season'"})
            return HttpResponse(json_obj, content_type="application/json")
    else:
        json_obj = json.dumps({"notes": "please input correct season 'year-season'"})
        return HttpResponse(json_obj, content_type="application/json")
    # if 'year' in request.GET and  'season' in request.GET:
    #     year = int(request.GET['year'])
    #     season = int(request.GET['season'])
    # else:
    #     today = datetime.datetime.now()
    #     year, season = last_season(today)
    stockIDs = get_updated_id(year, season)
    #stock_ids = StockId.objects.all()
    if season == 4:
        incomeStatementsSeason1 = SeasonIncomeStatement.objects.filter(year=year, season=1)
        incomeStatementsSeason2 = SeasonIncomeStatement.objects.filter(year=year, season=2)
        incomeStatementsSeason3 = SeasonIncomeStatement.objects.filter(year=year, season=3)
    for stockID in stockIDs:
        stock_symbol = stockID
        if not (SeasonIncomeStatement.objects.filter(symbol=stock_symbol, year=year, season=season)):
            url = 'http://mops.twse.com.tw/mops/web/ajax_t164sb04'
            # values = {'encodeURIComponent' : '1', 'step' : '1', 'firstin' : '1', 'off' : '1',
            # 'keyword4' : '','code1' : '','TYPEK2' : '','checkbtn' : '',
            # 'queryName':'co_id', 'TYPEK':'all', 'isnew':'false', 'co_id' : stock_symbol, 'year' : year, 'season' : str(season).zfill(2) }
            values = {'encodeURIComponent' : '1', 'id' : '', 'key' : '', 'TYPEK' : 'sii', 'step' : '2',
                      'year' : str(year-1911), 'season' : str(season).zfill(2), 'co_id' : stock_symbol, 'firstin' : '1'}
            url_data = urllib.urlencode(values)
            headers = {'User-Agent': 'Mozilla/5.0'}
            req = urllib2.Request(url, url_data, headers)
            try:
                response = urllib2.urlopen(req)
                soup = BeautifulSoup(response,from_encoding="utf-8")
                season_income_datas = soup.find_all("td", {'style' : 'text-align:left;white-space:nowrap;'})
                busy_msg = soup.find('table', attrs = {'width':'80%', 'border':'0','cellspacing':'8'})
            except URLError, e:
                time.sleep(20)
                busy_msg = True
                if hasattr(e, "reason"):
                    print(stock_symbol + " Reason:"), e.reason
                    print stock_symbol + 'time sleep' 
                elif hasattr(e, "code"):
                    print(stock_symbol + " Error code:"), e.code
                    print stock_symbol + 'time sleep' 
            # 如果連線正常，還得再確認是否因查詢頻繁而給空表格；若有，則先sleep再重新連線
            while busy_msg:
                response.close()
                headers = {'User-Agent': 'Mozilla/4.0'}
                req = urllib2.Request(url, url_data, headers)
                try:
                    response = urllib2.urlopen(req)
                    soup = BeautifulSoup(response,from_encoding="utf-8")
                    season_income_datas = soup.find_all("td", {'style' : 'text-align:left;white-space:nowrap;'})
                    busy_msg = soup.find('table', attrs = {'width':'80%', 'border':'0','cellspacing':'8'})
                except URLError, e:
                    busy_msg = True
                    if hasattr(e, "reason"):
                        print(stock_symbol + " Reason:"), e.reason
                        print stock_symbol + 'time sleep' 
                    elif hasattr(e, "code"):
                        print(stock_symbol + " Error code:"), e.code
                        print stock_symbol + 'time sleep' 
                if busy_msg:
                    print stock_symbol + 'time sleep' 
                    time.sleep(20)

            income_statement = SeasonIncomeStatement()
            income_statement.symbol = stock_symbol
            income_statement.year = year
            income_statement.season = season
            income_statement.surrogate_key = stock_symbol + '_' + str(year) + str(season).zfill(2)

            income_statement.date = season_to_date(year, season)
            owners_of_parent = 0
            print stock_symbol + ' loaded'
            symbolSeason1 = None
            symbolSeason2 = None
            symbolSeason3 = None
            hasPrevSeasons = False
            if season == 4:
                if incomeStatementsSeason1:
                    if incomeStatementsSeason1.filter(symbol=stock_symbol):
                        symbolSeason1 = incomeStatementsSeason1.get(symbol=stock_symbol)
                if incomeStatementsSeason2:
                    if incomeStatementsSeason2.filter(symbol=stock_symbol):
                        symbolSeason2 = incomeStatementsSeason2.get(symbol=stock_symbol)
                if incomeStatementsSeason3:
                    if incomeStatementsSeason3.filter(symbol=stock_symbol):
                        symbolSeason3 = incomeStatementsSeason3.get(symbol=stock_symbol)
                if symbolSeason1 and symbolSeason2 and symbolSeason3:
                    hasPrevSeasons = True
            for data in season_income_datas:
                if r'營業收入合計' in data.string.encode('utf-8') or r'收入合計' == data.string.encode('utf-8') or r'淨收益' == data.string.encode('utf-8') or r'收益合計' == data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    if not hasPrevSeasons:
                        income_statement.total_operating_revenue = st_to_decimal(next_data.string)
                    elif symbolSeason1.total_operating_revenue is not None and symbolSeason2.total_operating_revenue is not None and symbolSeason3.total_operating_revenue is not None:
                        income_statement.total_operating_revenue = st_to_decimal(next_data.string) - symbolSeason1.total_operating_revenue - symbolSeason2.total_operating_revenue - symbolSeason3.total_operating_revenue
                elif r'營業成本合計' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    if not hasPrevSeasons:
                        income_statement.total_operating_cost = st_to_decimal(next_data.string)
                    elif symbolSeason1.total_operating_cost is not None and symbolSeason2.total_operating_cost is not None and symbolSeason3.total_operating_cost is not None:
                        income_statement.total_operating_cost = st_to_decimal(next_data.string) - symbolSeason1.total_operating_cost - symbolSeason2.total_operating_cost - symbolSeason3.total_operating_cost
                elif r'營業毛利（毛損）' == data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    if not hasPrevSeasons:
                        income_statement.gross_profit_loss_from_operations = st_to_decimal(next_data.string)
                    elif symbolSeason1.gross_profit_loss_from_operations is not None and symbolSeason2.gross_profit_loss_from_operations is not None and symbolSeason3.gross_profit_loss_from_operations is not None:
                        income_statement.gross_profit_loss_from_operations = st_to_decimal(next_data.string) - symbolSeason1.gross_profit_loss_from_operations - symbolSeason2.gross_profit_loss_from_operations - symbolSeason3.gross_profit_loss_from_operations
                elif r'未實現銷貨（損）益' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    if not hasPrevSeasons:
                        income_statement.unrealized_profit_loss_from_sales = st_to_decimal(next_data.string)
                    elif symbolSeason1.unrealized_profit_loss_from_sales is not None and symbolSeason2.unrealized_profit_loss_from_sales is not None and symbolSeason3.unrealized_profit_loss_from_sales is not None:
                        income_statement.unrealized_profit_loss_from_sales = st_to_decimal(next_data.string) - symbolSeason1.unrealized_profit_loss_from_sales - symbolSeason2.unrealized_profit_loss_from_sales - symbolSeason3.unrealized_profit_loss_from_sales
                elif r'已實現銷貨（損）益' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    if not hasPrevSeasons:
                        income_statement.realized_profit_loss_from_sales = st_to_decimal(next_data.string)
                    elif symbolSeason1.realized_profit_loss_from_sales is not None and symbolSeason2.realized_profit_loss_from_sales is not None and symbolSeason3.realized_profit_loss_from_sales is not None:
                        income_statement.realized_profit_loss_from_sales = st_to_decimal(next_data.string) - symbolSeason1.realized_profit_loss_from_sales - symbolSeason2.realized_profit_loss_from_sales - symbolSeason3.realized_profit_loss_from_sales
                elif r'營業毛利（毛損）淨額' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    if not hasPrevSeasons:
                        income_statement.net_gross_profit_from_operations = st_to_decimal(next_data.string)
                    elif symbolSeason1.net_gross_profit_from_operations is not None and symbolSeason2.net_gross_profit_from_operations is not None and symbolSeason3.net_gross_profit_from_operations is not None:
                        income_statement.net_gross_profit_from_operations = st_to_decimal(next_data.string) - symbolSeason1.net_gross_profit_from_operations - symbolSeason2.net_gross_profit_from_operations - symbolSeason3.net_gross_profit_from_operations
                elif r'推銷費用' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    if not hasPrevSeasons:
                        income_statement.total_selling_expenses = st_to_decimal(next_data.string)
                    elif symbolSeason1.total_selling_expenses is not None and symbolSeason2.total_selling_expenses is not None and symbolSeason3.total_selling_expenses is not None:
                        income_statement.total_selling_expenses = st_to_decimal(next_data.string) - symbolSeason1.total_selling_expenses - symbolSeason2.total_selling_expenses - symbolSeason3.total_selling_expenses
                elif r'管理費用' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    if not hasPrevSeasons:
                        income_statement.administrative_expenses = st_to_decimal(next_data.string)
                    elif symbolSeason1.administrative_expenses is not None and symbolSeason2.administrative_expenses is not None and symbolSeason3.administrative_expenses is not None:
                        income_statement.administrative_expenses = st_to_decimal(next_data.string) - symbolSeason1.administrative_expenses - symbolSeason2.administrative_expenses - symbolSeason3.administrative_expenses
                elif r'研究發展費用' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    if not hasPrevSeasons:
                        income_statement.research_and_development_expenses = st_to_decimal(next_data.string)
                    elif symbolSeason1.research_and_development_expenses is not None and symbolSeason2.research_and_development_expenses is not None and symbolSeason3.research_and_development_expenses is not None:
                        income_statement.research_and_development_expenses = st_to_decimal(next_data.string) - symbolSeason1.research_and_development_expenses - symbolSeason2.research_and_development_expenses - symbolSeason3.research_and_development_expenses
                elif r'營業費用合計' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    if not hasPrevSeasons:
                        income_statement.total_operating_expenses = st_to_decimal(next_data.string)
                    elif symbolSeason1.total_operating_expenses is not None and symbolSeason2.total_operating_expenses is not None and symbolSeason3.total_operating_expenses is not None:
                        income_statement.total_operating_expenses = st_to_decimal(next_data.string) - symbolSeason1.total_operating_expenses - symbolSeason2.total_operating_expenses - symbolSeason3.total_operating_expenses
                elif r'其他收益及費損淨額' in data.string.encode('utf-8'):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        if not hasPrevSeasons:
                            income_statement.net_other_income_expenses = st_to_decimal(next_data.string)
                        elif symbolSeason1.net_other_income_expenses is not None and symbolSeason2.net_other_income_expenses is not None and symbolSeason3.net_other_income_expenses is not None:
                            income_statement.net_other_income_expenses = st_to_decimal(next_data.string) - symbolSeason1.net_other_income_expenses - symbolSeason2.net_other_income_expenses - symbolSeason3.net_other_income_expenses
                elif r'營業利益（損失）' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    if not hasPrevSeasons:
                        income_statement.net_operating_income_loss = st_to_decimal(next_data.string)
                    elif symbolSeason1.net_operating_income_loss is not None and symbolSeason2.net_operating_income_loss is not None and symbolSeason3.net_operating_income_loss is not None:
                        income_statement.net_operating_income_loss = st_to_decimal(next_data.string) - symbolSeason1.net_operating_income_loss - symbolSeason2.net_operating_income_loss - symbolSeason3.net_operating_income_loss
                elif r'其他收入' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    if not hasPrevSeasons:
                        income_statement.other_income = st_to_decimal(next_data.string)
                    elif symbolSeason1.other_income is not None and symbolSeason2.other_income is not None and symbolSeason3.other_income is not None:
                        income_statement.other_income = st_to_decimal(next_data.string) - symbolSeason1.other_income - symbolSeason2.other_income - symbolSeason3.other_income
                elif r'其他利益及損失淨額' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    if not hasPrevSeasons:
                        income_statement.other_gains_and_losses = st_to_decimal(next_data.string)
                    elif symbolSeason1.other_gains_and_losses is not None and symbolSeason2.other_gains_and_losses is not None and symbolSeason3.other_gains_and_losses is not None:
                        income_statement.other_gains_and_losses = st_to_decimal(next_data.string) - symbolSeason1.other_gains_and_losses - symbolSeason2.other_gains_and_losses - symbolSeason3.other_gains_and_losses
                elif r'財務成本淨額' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    if not hasPrevSeasons:
                        income_statement.net_finance_costs = st_to_decimal(next_data.string)
                    elif symbolSeason1.net_finance_costs is not None and symbolSeason2.net_finance_costs is not None and symbolSeason3.net_finance_costs is not None:
                        income_statement.net_finance_costs = st_to_decimal(next_data.string) - symbolSeason1.net_finance_costs - symbolSeason2.net_finance_costs - symbolSeason3.net_finance_costs
                elif r'採用權益法認列之關聯企業及合資損益之份額淨額' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    if not hasPrevSeasons:
                        income_statement.share_of_profit_loss_of_associates_using_equity_method = st_to_decimal(next_data.string)
                    elif symbolSeason1.share_of_profit_loss_of_associates_using_equity_method is not None and symbolSeason2.share_of_profit_loss_of_associates_using_equity_method is not None and symbolSeason3.share_of_profit_loss_of_associates_using_equity_method is not None:
                        income_statement.share_of_profit_loss_of_associates_using_equity_method = st_to_decimal(next_data.string) - symbolSeason1.share_of_profit_loss_of_associates_using_equity_method - symbolSeason2.share_of_profit_loss_of_associates_using_equity_method - symbolSeason3.share_of_profit_loss_of_associates_using_equity_method
                elif r'營業外收入及支出合計' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    if not hasPrevSeasons:
                        income_statement.total_non_operating_income_and_expenses = st_to_decimal(next_data.string)
                    elif symbolSeason1.total_non_operating_income_and_expenses is not None and symbolSeason2.total_non_operating_income_and_expenses is not None and symbolSeason3.total_non_operating_income_and_expenses is not None:
                        income_statement.total_non_operating_income_and_expenses = st_to_decimal(next_data.string) - symbolSeason1.total_non_operating_income_and_expenses - symbolSeason2.total_non_operating_income_and_expenses - symbolSeason3.total_non_operating_income_and_expenses
                elif r'稅前淨利（淨損）' in data.string.encode('utf-8') or r'繼續營業單位稅前淨利（淨損）' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    if not hasPrevSeasons:
                        income_statement.profit_loss_from_continuing_operations_before_tax = st_to_decimal(next_data.string)
                    elif symbolSeason1.profit_loss_from_continuing_operations_before_tax is not None and symbolSeason2.profit_loss_from_continuing_operations_before_tax is not None and symbolSeason3.profit_loss_from_continuing_operations_before_tax is not None:
                        income_statement.profit_loss_from_continuing_operations_before_tax = st_to_decimal(next_data.string) - symbolSeason1.profit_loss_from_continuing_operations_before_tax - symbolSeason2.profit_loss_from_continuing_operations_before_tax - symbolSeason3.profit_loss_from_continuing_operations_before_tax
                elif r'所得稅費用（利益）合計' in data.string.encode('utf-8') or r'所得稅（費用）利益' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    if not hasPrevSeasons:
                        income_statement.total_tax_expense = st_to_decimal(next_data.string)
                    elif symbolSeason1.total_tax_expense is not None and symbolSeason2.total_tax_expense is not None and symbolSeason3.total_tax_expense is not None:
                        income_statement.total_tax_expense = st_to_decimal(next_data.string) - symbolSeason1.total_tax_expense - symbolSeason2.total_tax_expense - symbolSeason3.total_tax_expense
                elif r'繼續營業單位本期淨利（淨損）' in data.string.encode('utf-8') or r'繼續營業單位本期稅後淨利（淨損）' in data.string.encode('utf-8') or r'繼續營業單位淨利（淨損）' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    if not hasPrevSeasons:
                        income_statement.profit_loss_from_continuing_operations = st_to_decimal(next_data.string)
                    elif symbolSeason1.profit_loss_from_continuing_operations is not None and symbolSeason2.profit_loss_from_continuing_operations is not None and symbolSeason3.profit_loss_from_continuing_operations is not None:
                        income_statement.profit_loss_from_continuing_operations = st_to_decimal(next_data.string) - symbolSeason1.profit_loss_from_continuing_operations - symbolSeason2.profit_loss_from_continuing_operations - symbolSeason3.profit_loss_from_continuing_operations
                elif r'本期淨利（淨損）' in data.string.encode('utf-8') or r'本期稅後淨利（淨損）' in data.string.encode('utf-8'):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        if not hasPrevSeasons:
                            income_statement.profit_loss = st_to_decimal(next_data.string)
                        elif symbolSeason1.profit_loss is not None and symbolSeason2.profit_loss is not None and symbolSeason3.profit_loss is not None:
                            income_statement.profit_loss = st_to_decimal(next_data.string) - symbolSeason1.profit_loss - symbolSeason2.profit_loss - symbolSeason3.profit_loss
                elif r'國外營運機構財務報表換算之兌換差額' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    if not hasPrevSeasons:
                        income_statement.exchange_differences_on_translation = st_to_decimal(next_data.string)
                    elif symbolSeason1.exchange_differences_on_translation is not None and symbolSeason2.exchange_differences_on_translation is not None and symbolSeason3.exchange_differences_on_translation is not None:
                        income_statement.exchange_differences_on_translation = st_to_decimal(next_data.string) - symbolSeason1.exchange_differences_on_translation - symbolSeason2.exchange_differences_on_translation - symbolSeason3.exchange_differences_on_translation
                elif r'備供出售金融資產未實現評價損益' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    if not hasPrevSeasons:
                        income_statement.unrealised_gains_losses_for_sale_financial_assets = st_to_decimal(next_data.string)
                    elif symbolSeason1.unrealised_gains_losses_for_sale_financial_assets is not None and symbolSeason2.unrealised_gains_losses_for_sale_financial_assets is not None and symbolSeason3.unrealised_gains_losses_for_sale_financial_assets is not None:
                        income_statement.unrealised_gains_losses_for_sale_financial_assets = st_to_decimal(next_data.string) - symbolSeason1.unrealised_gains_losses_for_sale_financial_assets - symbolSeason2.unrealised_gains_losses_for_sale_financial_assets - symbolSeason3.unrealised_gains_losses_for_sale_financial_assets
                elif r'採用權益法認列之關聯企業及合資之其他綜合損益之份額合計' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    if not hasPrevSeasons:
                        income_statement.total_share_of_other_income_of_associates_using_equity_method = st_to_decimal(next_data.string)
                    elif symbolSeason1.total_share_of_other_income_of_associates_using_equity_method is not None and symbolSeason2.total_share_of_other_income_of_associates_using_equity_method is not None and symbolSeason3.total_share_of_other_income_of_associates_using_equity_method is not None:
                        income_statement.total_share_of_other_income_of_associates_using_equity_method = st_to_decimal(next_data.string) - symbolSeason1.total_share_of_other_income_of_associates_using_equity_method - symbolSeason2.total_share_of_other_income_of_associates_using_equity_method - symbolSeason3.total_share_of_other_income_of_associates_using_equity_method
                elif r'與其他綜合損益組成部分相關之所得稅' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    if not hasPrevSeasons:
                        income_statement.income_tax_related_of_other_comprehensive_income = st_to_decimal(next_data.string)
                    elif symbolSeason1.income_tax_related_of_other_comprehensive_income is not None and symbolSeason2.income_tax_related_of_other_comprehensive_income is not None and symbolSeason3.income_tax_related_of_other_comprehensive_income is not None:
                        income_statement.income_tax_related_of_other_comprehensive_income = st_to_decimal(next_data.string) - symbolSeason1.income_tax_related_of_other_comprehensive_income - symbolSeason2.income_tax_related_of_other_comprehensive_income - symbolSeason3.income_tax_related_of_other_comprehensive_income
                elif r'其他綜合損益（淨額）' in data.string.encode('utf-8') or r'其他綜合損益（稅後）淨額' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    if not hasPrevSeasons:
                        income_statement.net_other_comprehensive_income = st_to_decimal(next_data.string)
                    elif symbolSeason1.net_other_comprehensive_income is not None and symbolSeason2.net_other_comprehensive_income is not None and symbolSeason3.net_other_comprehensive_income is not None:
                        income_statement.net_other_comprehensive_income = st_to_decimal(next_data.string) - symbolSeason1.net_other_comprehensive_income - symbolSeason2.net_other_comprehensive_income - symbolSeason3.net_other_comprehensive_income
                elif r'其他綜合損益' in data.string.encode('utf-8'):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        if not hasPrevSeasons:
                            income_statement.other_comprehensive_income = st_to_decimal(next_data.string)
                        elif symbolSeason1.other_comprehensive_income is not None and symbolSeason2.other_comprehensive_income is not None and symbolSeason3.other_comprehensive_income is not None:
                            income_statement.other_comprehensive_income = st_to_decimal(next_data.string) - symbolSeason1.other_comprehensive_income - symbolSeason2.other_comprehensive_income - symbolSeason3.other_comprehensive_income
                elif r'本期綜合損益總額' in data.string.encode('utf-8') or r'本期綜合損益總額（稅後）' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    if not hasPrevSeasons:
                        income_statement.total_comprehensive_income = st_to_decimal(next_data.string)
                    elif symbolSeason1.total_comprehensive_income is not None and symbolSeason2.total_comprehensive_income is not None and symbolSeason3.total_comprehensive_income is not None:
                        income_statement.total_comprehensive_income = st_to_decimal(next_data.string) - symbolSeason1.total_comprehensive_income - symbolSeason2.total_comprehensive_income - symbolSeason3.total_comprehensive_income
                elif r'母公司業主（淨利／損）' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    if not hasPrevSeasons:
                        income_statement.profit_loss_attributable_to_owners_of_parent = st_to_decimal(next_data.string)
                    elif symbolSeason1.profit_loss_attributable_to_owners_of_parent is not None and symbolSeason2.profit_loss_attributable_to_owners_of_parent is not None and symbolSeason3.profit_loss_attributable_to_owners_of_parent is not None:
                        income_statement.profit_loss_attributable_to_owners_of_parent = st_to_decimal(next_data.string) - symbolSeason1.profit_loss_attributable_to_owners_of_parent - symbolSeason2.profit_loss_attributable_to_owners_of_parent - symbolSeason3.profit_loss_attributable_to_owners_of_parent
                elif r'非控制權益（淨利／損）' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    if not hasPrevSeasons:
                        income_statement.profit_loss_attributable_to_owners_of_parent = st_to_decimal(next_data.string)
                    elif symbolSeason1.profit_loss_attributable_to_owners_of_parent is not None and symbolSeason2.profit_loss_attributable_to_owners_of_parent is not None and symbolSeason3.profit_loss_attributable_to_owners_of_parent is not None:
                        income_statement.profit_loss_attributable_to_owners_of_parent = st_to_decimal(next_data.string) - symbolSeason1.profit_loss_attributable_to_owners_of_parent - symbolSeason2.profit_loss_attributable_to_owners_of_parent - symbolSeason3.profit_loss_attributable_to_owners_of_parent
                elif r'母公司業主（綜合損益）' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    if not hasPrevSeasons:
                        income_statement.comprehensive_income_attributable_to_owners_of_parent = st_to_decimal(next_data.string)
                    elif symbolSeason1.comprehensive_income_attributable_to_owners_of_parent is not None and symbolSeason2.comprehensive_income_attributable_to_owners_of_parent is not None and symbolSeason3.comprehensive_income_attributable_to_owners_of_parent is not None:
                        income_statement.comprehensive_income_attributable_to_owners_of_parent = st_to_decimal(next_data.string) - symbolSeason1.comprehensive_income_attributable_to_owners_of_parent - symbolSeason2.comprehensive_income_attributable_to_owners_of_parent - symbolSeason3.comprehensive_income_attributable_to_owners_of_parent
                elif r'母公司業主' in data.string.encode('utf-8'):
                    if owners_of_parent == 0:
                        next_data = data.next_sibling.next_sibling
                        if not hasPrevSeasons:
                            income_statement.comprehensive_income_attributable_to_owners_of_parent = st_to_decimal(next_data.string)
                        elif symbolSeason1.comprehensive_income_attributable_to_owners_of_parent is not None and symbolSeason2.comprehensive_income_attributable_to_owners_of_parent is not None and symbolSeason3.comprehensive_income_attributable_to_owners_of_parent is not None:
                            income_statement.comprehensive_income_attributable_to_owners_of_parent = st_to_decimal(next_data.string) - symbolSeason1.comprehensive_income_attributable_to_owners_of_parent - symbolSeason2.comprehensive_income_attributable_to_owners_of_parent - symbolSeason3.comprehensive_income_attributable_to_owners_of_parent
                        owners_of_parent = 1
                    else:
                        next_data = data.next_sibling.next_sibling
                        if not hasPrevSeasons:
                            income_statement.comprehensive_income_attributable_to_owners_of_parent = st_to_decimal(next_data.string)
                        elif symbolSeason1.comprehensive_income_attributable_to_owners_of_parent is not None and symbolSeason2.comprehensive_income_attributable_to_owners_of_parent is not None and symbolSeason3.comprehensive_income_attributable_to_owners_of_parent is not None:
                            income_statement.comprehensive_income_attributable_to_owners_of_parent = st_to_decimal(next_data.string) - symbolSeason1.comprehensive_income_attributable_to_owners_of_parent - symbolSeason2.comprehensive_income_attributable_to_owners_of_parent - symbolSeason3.comprehensive_income_attributable_to_owners_of_parent
                elif r'非控制權益（綜合損益）' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    if not hasPrevSeasons:
                        income_statement.comprehensive_income_attributable_to_non_controlling_interests = st_to_decimal(next_data.string)
                    elif symbolSeason1.comprehensive_income_attributable_to_non_controlling_interests is not None and symbolSeason2.comprehensive_income_attributable_to_non_controlling_interests is not None and symbolSeason3.comprehensive_income_attributable_to_non_controlling_interests is not None:
                        income_statement.comprehensive_income_attributable_to_non_controlling_interests = st_to_decimal(next_data.string) - symbolSeason1.comprehensive_income_attributable_to_non_controlling_interests - symbolSeason2.comprehensive_income_attributable_to_non_controlling_interests - symbolSeason3.comprehensive_income_attributable_to_non_controlling_interests
                elif r'基本每股盈餘' in data.string.encode('utf-8'):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        if not hasPrevSeasons:
                            income_statement.total_basic_earnings_per_share = st_to_decimal(next_data.string)
                        elif symbolSeason1.total_basic_earnings_per_share is not None and symbolSeason2.total_basic_earnings_per_share is not None and symbolSeason3.total_basic_earnings_per_share is not None:
                            income_statement.total_basic_earnings_per_share = st_to_decimal(next_data.string) - symbolSeason1.total_basic_earnings_per_share - symbolSeason2.total_basic_earnings_per_share - symbolSeason3.total_basic_earnings_per_share
                elif r'稀釋每股盈餘' in data.string.encode('utf-8'):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        if not hasPrevSeasons:
                            income_statement.total_diluted_earnings_per_share = st_to_decimal(next_data.string)
                        elif symbolSeason1.total_diluted_earnings_per_share is not None and symbolSeason2.total_diluted_earnings_per_share is not None and symbolSeason3.total_diluted_earnings_per_share is not None:
                            income_statement.total_diluted_earnings_per_share = st_to_decimal(next_data.string) - symbolSeason1.total_diluted_earnings_per_share - symbolSeason2.total_diluted_earnings_per_share - symbolSeason3.total_diluted_earnings_per_share
                elif r'利息收入' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    if not hasPrevSeasons:
                        income_statement.interest_income = st_to_decimal(next_data.string)
                    elif symbolSeason1.interest_income is not None and symbolSeason2.interest_income is not None and symbolSeason3.interest_income is not None:
                        income_statement.interest_income = st_to_decimal(next_data.string) - symbolSeason1.interest_income - symbolSeason2.interest_income - symbolSeason3.interest_income
                elif r'減：利息費用' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    if not hasPrevSeasons:
                        income_statement.interest_expenses = st_to_decimal(next_data.string)
                    elif symbolSeason1.interest_expenses is not None and symbolSeason2.interest_expenses is not None and symbolSeason3.interest_expenses is not None:
                        income_statement.interest_expenses = st_to_decimal(next_data.string) - symbolSeason1.interest_expenses - symbolSeason2.interest_expenses - symbolSeason3.interest_expenses
                elif r'利息淨收益' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    if not hasPrevSeasons:
                        income_statement.net_interest_income_expense = st_to_decimal(next_data.string)
                    elif symbolSeason1.net_interest_income_expense is not None and symbolSeason2.net_interest_income_expense is not None and symbolSeason3.net_interest_income_expense is not None:
                        income_statement.net_interest_income_expense = st_to_decimal(next_data.string) - symbolSeason1.net_interest_income_expense - symbolSeason2.net_interest_income_expense - symbolSeason3.net_interest_income_expense
                elif r'手續費淨收益' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    if not hasPrevSeasons:
                        income_statement.net_service_fee_charge_and_commisions_income_loss = st_to_decimal(next_data.string)
                    elif symbolSeason1.net_service_fee_charge_and_commisions_income_loss is not None and symbolSeason2.net_service_fee_charge_and_commisions_income_loss is not None and symbolSeason3.net_service_fee_charge_and_commisions_income_loss is not None:
                        income_statement.net_service_fee_charge_and_commisions_income_loss = st_to_decimal(next_data.string) - symbolSeason1.net_service_fee_charge_and_commisions_income_loss - symbolSeason2.net_service_fee_charge_and_commisions_income_loss - symbolSeason3.net_service_fee_charge_and_commisions_income_loss
                elif r'透過損益按公允價值衡量之金融資產及負債損益' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    if not hasPrevSeasons:
                        income_statement.gain_loss_on_financial_assets_liabilities_at_fair_value = st_to_decimal(next_data.string)
                    elif symbolSeason1.gain_loss_on_financial_assets_liabilities_at_fair_value is not None and symbolSeason2.gain_loss_on_financial_assets_liabilities_at_fair_value is not None and symbolSeason3.gain_loss_on_financial_assets_liabilities_at_fair_value is not None:
                        income_statement.gain_loss_on_financial_assets_liabilities_at_fair_value = st_to_decimal(next_data.string) - symbolSeason1.gain_loss_on_financial_assets_liabilities_at_fair_value - symbolSeason2.gain_loss_on_financial_assets_liabilities_at_fair_value - symbolSeason3.gain_loss_on_financial_assets_liabilities_at_fair_value
                elif r'保險業務淨收益' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    if not hasPrevSeasons:
                        income_statement.net_income_loss_of_insurance_operations = st_to_decimal(next_data.string)
                    elif symbolSeason1.net_income_loss_of_insurance_operations is not None and symbolSeason2.net_income_loss_of_insurance_operations is not None and symbolSeason3.net_income_loss_of_insurance_operations is not None:
                        income_statement.net_income_loss_of_insurance_operations = st_to_decimal(next_data.string) - symbolSeason1.net_income_loss_of_insurance_operations - symbolSeason2.net_income_loss_of_insurance_operations - symbolSeason3.net_income_loss_of_insurance_operations
                elif r'投資性不動產損益' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    if not hasPrevSeasons:
                        income_statement.gain_loss_on_investment_property = st_to_decimal(next_data.string)
                    elif symbolSeason1.gain_loss_on_investment_property is not None and symbolSeason2.gain_loss_on_investment_property is not None and symbolSeason3.gain_loss_on_investment_property is not None:
                        income_statement.gain_loss_on_investment_property = st_to_decimal(next_data.string) - symbolSeason1.gain_loss_on_investment_property - symbolSeason2.gain_loss_on_investment_property - symbolSeason3.gain_loss_on_investment_property
                elif r'備供出售金融資產之已實現損益' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    if not hasPrevSeasons:
                        income_statement.realized_gains_on_available_for_sale_financial_assets = st_to_decimal(next_data.string)
                    elif symbolSeason1.realized_gains_on_available_for_sale_financial_assets is not None and symbolSeason2.realized_gains_on_available_for_sale_financial_assets is not None and symbolSeason3.realized_gains_on_available_for_sale_financial_assets is not None:
                        income_statement.realized_gains_on_available_for_sale_financial_assets = st_to_decimal(next_data.string) - symbolSeason1.realized_gains_on_available_for_sale_financial_assets - symbolSeason2.realized_gains_on_available_for_sale_financial_assets - symbolSeason3.realized_gains_on_available_for_sale_financial_assets
                elif r'持有至到期日金融資產之已實現損益' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    if not hasPrevSeasons:
                        income_statement.realized_gains_on_held_to_maturity_financial_assets = st_to_decimal(next_data.string)
                    elif symbolSeason1.realized_gains_on_held_to_maturity_financial_assets is not None and symbolSeason2.realized_gains_on_held_to_maturity_financial_assets is not None and symbolSeason3.realized_gains_on_held_to_maturity_financial_assets is not None:
                        income_statement.realized_gains_on_held_to_maturity_financial_assets = st_to_decimal(next_data.string) - symbolSeason1.realized_gains_on_held_to_maturity_financial_assets - symbolSeason2.realized_gains_on_held_to_maturity_financial_assets - symbolSeason3.realized_gains_on_held_to_maturity_financial_assets
                elif r'兌換損益' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    if not hasPrevSeasons:
                        income_statement.foreign_exchange_gains_losses = st_to_decimal(next_data.string)
                    elif symbolSeason1.foreign_exchange_gains_losses is not None and symbolSeason2.foreign_exchange_gains_losses is not None and symbolSeason3.foreign_exchange_gains_losses is not None:
                        income_statement.foreign_exchange_gains_losses = st_to_decimal(next_data.string) - symbolSeason1.foreign_exchange_gains_losses - symbolSeason2.foreign_exchange_gains_losses - symbolSeason3.foreign_exchange_gains_losses
                elif r'資產減損（損失）迴轉利益淨額' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    if not hasPrevSeasons:
                        income_statement.impairment_loss_or_reversal_of_impairment_loss_on_assets = st_to_decimal(next_data.string)
                    elif symbolSeason1.impairment_loss_or_reversal_of_impairment_loss_on_assets is not None and symbolSeason2.impairment_loss_or_reversal_of_impairment_loss_on_assets is not None and symbolSeason3.impairment_loss_or_reversal_of_impairment_loss_on_assets is not None:
                        income_statement.impairment_loss_or_reversal_of_impairment_loss_on_assets = st_to_decimal(next_data.string) - symbolSeason1.impairment_loss_or_reversal_of_impairment_loss_on_assets - symbolSeason2.impairment_loss_or_reversal_of_impairment_loss_on_assets - symbolSeason3.impairment_loss_or_reversal_of_impairment_loss_on_assets
                elif r'其他利息以外淨損益' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    if not hasPrevSeasons:
                        income_statement.net_other_non_interest_incomes_losses = st_to_decimal(next_data.string)
                    elif symbolSeason1.net_other_non_interest_incomes_losses is not None and symbolSeason2.net_other_non_interest_incomes_losses is not None and symbolSeason3.net_other_non_interest_incomes_losses is not None:
                        income_statement.net_other_non_interest_incomes_losses = st_to_decimal(next_data.string) - symbolSeason1.net_other_non_interest_incomes_losses - symbolSeason2.net_other_non_interest_incomes_losses - symbolSeason3.net_other_non_interest_incomes_losses
                elif r'利息以外淨損益' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    if not hasPrevSeasons:
                        income_statement.net_income_loss_except_interest = st_to_decimal(next_data.string)
                    elif symbolSeason1.net_income_loss_except_interest is not None and symbolSeason2.net_income_loss_except_interest is not None and symbolSeason3.net_income_loss_except_interest is not None:
                        income_statement.net_income_loss_except_interest = st_to_decimal(next_data.string) - symbolSeason1.net_income_loss_except_interest - symbolSeason2.net_income_loss_except_interest - symbolSeason3.net_income_loss_except_interest
                elif r'淨收益' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    if not hasPrevSeasons:
                        income_statement.net_income_loss = st_to_decimal(next_data.string)
                    elif symbolSeason1.net_income_loss and symbolSeason2.net_income_loss and symbolSeason3.net_income_loss:
                        income_statement.net_income_loss = st_to_decimal(next_data.string) - symbolSeason1.net_income_loss - symbolSeason2.net_income_loss - symbolSeason3.net_income_loss
                elif r'呆帳費用及保證責任準備提存（各項提存）' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    if not hasPrevSeasons:
                        income_statement.total_bad_debts_expense_and_guarantee_liability_provisions = st_to_decimal(next_data.string)
                    elif symbolSeason1.total_bad_debts_expense_and_guarantee_liability_provisions is not None and symbolSeason2.total_bad_debts_expense_and_guarantee_liability_provisions is not None and symbolSeason3.total_bad_debts_expense_and_guarantee_liability_provisions is not None:
                        income_statement.total_bad_debts_expense_and_guarantee_liability_provisions = st_to_decimal(next_data.string) - symbolSeason1.total_bad_debts_expense_and_guarantee_liability_provisions - symbolSeason2.total_bad_debts_expense_and_guarantee_liability_provisions - symbolSeason3.total_bad_debts_expense_and_guarantee_liability_provisions
                elif r'保險負債準備淨變動' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    if not hasPrevSeasons:
                        income_statement.total_net_change_in_provisions_for_insurance_liabilities = st_to_decimal(next_data.string)
                    elif symbolSeason1.total_net_change_in_provisions_for_insurance_liabilities is not None and symbolSeason2.total_net_change_in_provisions_for_insurance_liabilities is not None and symbolSeason3.total_net_change_in_provisions_for_insurance_liabilities is not None:
                        income_statement.total_net_change_in_provisions_for_insurance_liabilities = st_to_decimal(next_data.string) - symbolSeason1.total_net_change_in_provisions_for_insurance_liabilities - symbolSeason2.total_net_change_in_provisions_for_insurance_liabilities - symbolSeason3.total_net_change_in_provisions_for_insurance_liabilities
                elif r'員工福利費用' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    if not hasPrevSeasons:
                        income_statement.employee_benefits_expenses = st_to_decimal(next_data.string)
                    elif symbolSeason1.employee_benefits_expenses is not None and symbolSeason2.employee_benefits_expenses is not None and symbolSeason3.employee_benefits_expenses is not None:
                        income_statement.employee_benefits_expenses = st_to_decimal(next_data.string) - symbolSeason1.employee_benefits_expenses - symbolSeason2.employee_benefits_expenses - symbolSeason3.employee_benefits_expenses
                elif r'折舊及攤銷費用' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    if not hasPrevSeasons:
                        income_statement.employee_benefits_expenses = st_to_decimal(next_data.string)
                    elif symbolSeason1.employee_benefits_expenses is not None and symbolSeason2.employee_benefits_expenses is not None and symbolSeason3.employee_benefits_expenses is not None:
                        income_statement.employee_benefits_expenses = st_to_decimal(next_data.string) - symbolSeason1.employee_benefits_expenses - symbolSeason2.employee_benefits_expenses - symbolSeason3.employee_benefits_expenses
                elif r'其他業務及管理費用' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    if not hasPrevSeasons:
                        income_statement.other_general_and_administrative_expenses = st_to_decimal(next_data.string)
                    elif symbolSeason1.other_general_and_administrative_expenses is not None and symbolSeason2.other_general_and_administrative_expenses is not None and symbolSeason3.other_general_and_administrative_expenses is not None:
                        income_statement.other_general_and_administrative_expenses = st_to_decimal(next_data.string) - symbolSeason1.other_general_and_administrative_expenses - symbolSeason2.other_general_and_administrative_expenses - symbolSeason3.other_general_and_administrative_expenses
                elif r'現金流量避險中屬有效避險不分之避險工具利益（損失）' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    if not hasPrevSeasons:
                        income_statement.gain_loss_on_effective_portion_of_cash_flow_hedges = st_to_decimal(next_data.string)
                    elif symbolSeason1.gain_loss_on_effective_portion_of_cash_flow_hedges is not None and symbolSeason2.gain_loss_on_effective_portion_of_cash_flow_hedges is not None and symbolSeason3.gain_loss_on_effective_portion_of_cash_flow_hedges is not None:
                        income_statement.gain_loss_on_effective_portion_of_cash_flow_hedges = st_to_decimal(next_data.string) - symbolSeason1.gain_loss_on_effective_portion_of_cash_flow_hedges - symbolSeason2.gain_loss_on_effective_portion_of_cash_flow_hedges - symbolSeason3.gain_loss_on_effective_portion_of_cash_flow_hedges
                elif r'停業單位損益' in data.string.encode('utf-8') or r'停業單位損益合計' in data.string.encode('utf-8'):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        if not hasPrevSeasons:
                            income_statement.income_from_discontinued_operations = st_to_decimal(next_data.string)
                        elif symbolSeason1.income_from_discontinued_operations is not None and symbolSeason2.income_from_discontinued_operations is not None and symbolSeason3.income_from_discontinued_operations is not None:
                            income_statement.income_from_discontinued_operations = st_to_decimal(next_data.string) - symbolSeason1.income_from_discontinued_operations - symbolSeason2.income_from_discontinued_operations - symbolSeason3.income_from_discontinued_operations
            if income_statement.total_basic_earnings_per_share is not None:
                income_statement.save()
                print stock_symbol + ' data updated'
            else:
                print stock_symbol + 'has no data-----------'
    cnt = SeasonIncomeStatement.objects.filter(year=year, season=season).count()
    lastDate = SeasonIncomeStatement.objects.all().aggregate(Max('date'))['date__max']
    lastDateDataCnt = SeasonIncomeStatement.objects.filter(date=lastDate).count()
    updateManagement = UpdateManagement(name = "seasonIncomeStatement", last_update_date = datetime.date.today(), 
                                        last_data_date = lastDate, notes="There is " + str(lastDateDataCnt) + " season_revenues")
    updateManagement.save()
    json_obj = json.dumps({"name": updateManagement.name, "lastUpdateDate": updateManagement.last_update_date.strftime("%y-%m-%d"),
                           "lastDataDate": lastDate.strftime("%y-%m-%d"), "notes": "Update " + str(cnt) + " seasonrevenue on " + str(year) + "-" + str(season)})
    return HttpResponse(json_obj, content_type="application/json")

#資產負債表
def show_season_balance_sheet(request):
    stock_symbol = '8114'
    year = 2013
    season = 2
    url = 'http://mops.twse.com.tw/mops/web/t164sb04'
    values = {'encodeURIComponent' : '1', 'step' : '1', 'firstin' : '1', 'off' : '1',
            'keyword4' : '','code1' : '','TYPEK2' : '','checkbtn' : '',
            'queryName':'co_id', 'TYPEK':'all', 'isnew':'true', 'co_id' : stock_symbol, 'year' : year, 'season' : str(season).zfill(2) }
    # url_data = urllib.urlencode(values) 
    # req = urllib2.Request(url, url_data)
    # response = urllib2.urlopen(req)
    values = {'encodeURIComponent' : '1', 'id' : '', 'key' : '', 'TYPEK' : 'all', 'step' : '2',
                      'year' : str(year-1911), 'season' : str(season).zfill(2), 'co_id' : stock_symbol, 'firstin' : '1'}
    url_data = urllib.urlencode(values) 
    req = urllib2.Request(url, url_data)
    response = urllib2.urlopen(req)

    soup = BeautifulSoup(response,from_encoding="utf-8")
    # print soup 詳細資料
    detail_button = soup.find_all("input", {'type': 'button', 'value': r'詳細資訊'})
    print detail_button

    balance_sheet_datas = soup.find_all("td", {'style' : 'text-align:left;white-space:nowrap;'})
    for data in balance_sheet_datas:
        if r'現金及約當現金' in data.string.encode('utf-8'):
            next_data = data.next_sibling.next_sibling
            print st_to_decimal(next_data.string)
            next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
            print st_to_decimal(next_data.string)
    req = urllib2.Request(url, url_data)
    response = urllib2.urlopen(req)
    return HttpResponse(response.read())

#資產負債表
def update_season_balance_sheet(request):
    if 'year' in request.GET and  'season' in request.GET:
        year = int(request.GET['year'])
        season = int(request.GET['season'])
    else:
        today = datetime.datetime.now()
        year, season = last_season(today)
    stockIDs = get_updated_id(year, season)
    for stock_id in stockIDs:
        stock_symbol = stock_id
        if not SeasonBalanceSheet.objects.filter(symbol=stock_symbol, year=year, season=season):
            print stock_symbol + ' loaded'
            url = 'http://mops.twse.com.tw/mops/web/t164sb03'
            # if stock_symbol[:2] == '28' or stock_symbol == '5880' or stock_symbol == '5820' or stock_symbol == '3990' or stock_symbol == '5871':
            values = {'encodeURIComponent' : '1', 'id' : '', 'key' : '', 'TYPEK' : 'all', 'step' : '2',
                        'year' : str(year-1911), 'season' : str(season).zfill(1), 'co_id' : stock_symbol, 'firstin' : '1'}
            # else:
            # values = {'encodeURIComponent': '1', 'step': '1', 'firstin': '1', 'off': '1',
            #             'keyword4': '', 'code1': '', 'TYPEK2': '', 'checkbtn': '',
            #             'queryName': 'co_id', 'TYPEK': 'all', 'isnew': 'false',
            #             'co_id': stock_symbol, 'year': str(year-1911), 'season': str(season).zfill(2)}

            url_data = urllib.urlencode(values)
            headers = {'User-Agent': 'Mozilla/5.0'}
            req = urllib2.Request(url, url_data, headers)
            try:
                response = urllib2.urlopen(req)
                soup = BeautifulSoup(response,from_encoding="utf-8")
                balance_sheet_datas = soup.find_all("td", {'style' : 'text-align:left;white-space:nowrap;'})
                busy_msg = soup.find('table', attrs = {'width':'80%', 'border':'0','cellspacing':'8'})
            except URLError, e:
                print stock_symbol + ' time sleep'
                time.sleep(20)
                busy_msg = True
                if hasattr(e, "reason"):
                    print(stock_symbol + " Reason:"), e.reason
                elif hasattr(e, "code"):
                    print(stock_symbol + " Error code:"), e.code
            # 如果連線正常，還得再確認是否因查詢頻繁而給空表格；若有，則先sleep再重新連線
            while (busy_msg is not None):
                response.close()
                headers = {'User-Agent': 'Mozilla/4.0'}
                req = urllib2.Request(url, url_data, headers)
                try:
                    response = urllib2.urlopen(req)
                    soup = BeautifulSoup(response,from_encoding="utf-8")
                    balance_sheet_datas = soup.find_all("td", {'style' : 'text-align:left;white-space:nowrap;'})
                    busy_msg = soup.find('table', attrs = {'width':'80%', 'border':'0','cellspacing':'8'})
                except URLError, e:
                    busy_msg = True
                    if hasattr(e, "reason"):
                        print(stock_symbol + " Reason:"), e.reason
                    elif hasattr(e, "code"):
                        print(stock_symbol + " Error code:"), e.code
                if busy_msg:
                    print stock_symbol + ' time sleep' 
                    time.sleep(20)

            balance_sheet = SeasonBalanceSheet()
            balance_sheet.symbol = stock_symbol
            balance_sheet.year = str(year)
            balance_sheet.season = season
            balance_sheet.date = season_to_date(year, season)
            balance_sheet.surrogate_key = stock_symbol + '_' + str(year) + str(season).zfill(2)

            for data in balance_sheet_datas:
                if r'現金及約當現金' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.total_cash_and_cash_equivalents = st_to_decimal(next_data.string)
                elif r'無活絡市場之債券投資' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.current_bond_investment_without_active_market = st_to_decimal(next_data.string)
                elif r'透過損益按公允價值衡量之金融資產－流動' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.current_financial_assets_at_fair_value_through_profit_or_loss = st_to_decimal(next_data.string)
                elif r'備供出售金融資產－流動淨額' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.current_available_for_sale_financial_assets = st_to_decimal(next_data.string)
                elif r'持有至到期日金融資產－流動淨額' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.current_held_to_maturity_financial_assets = st_to_decimal(next_data.string)
                elif r'應收票據淨額' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.notes_receivable = st_to_decimal(next_data.string)
                elif r'應收帳款淨額' in data.string.encode('utf-8') or r'應收款項淨額' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.accounts_receivable = st_to_decimal(next_data.string)
                elif r'應收帳款－關係人淨額' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.accounts_receivable_due_from_related_parties = st_to_decimal(next_data.string)
                elif r'其他應收款淨額' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.net_other_receivables = st_to_decimal(next_data.string)
                elif r'其他應收款－關係人淨額' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.other_receivables_due_from_related_parties = st_to_decimal(next_data.string)
                elif r'當期所得稅資產' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.total_current_tax_assets = st_to_decimal(next_data.string)
                elif r'存貨' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.total_inventories = st_to_decimal(next_data.string)
                elif r'預付款項' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.total_prepayments = st_to_decimal(next_data.string)
                elif r'其他流動資產' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.total_other_current_assets = st_to_decimal(next_data.string)
                elif r'流動資產合計' in data.string.encode('utf-8') and r'非' not in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.total_current_assets = st_to_decimal(next_data.string)
                elif r'備供出售金融資產－非流動淨額' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.non_current_available_for_sale_financial_assets = st_to_decimal(next_data.string)
                elif r'以成本衡量之金融資產－非流動淨額' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.non_current_financial_assets_at_cost = st_to_decimal(next_data.string)
                elif r'採用權益法之投資淨額' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.investment_accounted_for_using_equity_method = st_to_decimal(next_data.string)
                elif r'不動產、廠房及設備' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.total_property_plant_and_equipment = st_to_decimal(next_data.string)
                elif r'投資性不動產淨額' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.net_investment_property = st_to_decimal(next_data.string)
                elif r'無形資產' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        balance_sheet.intangible_assets = st_to_decimal(next_data.string)
                elif r'遞延所得稅資產' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.deferred_tax_assets = st_to_decimal(next_data.string)
                elif r'其他非流動資產' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.total_other_non_current_assets = st_to_decimal(next_data.string)
                elif r'非流動資產合計' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.total_non_current_assets = st_to_decimal(next_data.string)
                elif r'資產總額' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.total_assets = st_to_decimal(next_data.string)
                elif r'短期借款' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.total_short_term_borrowings = st_to_decimal(next_data.string)
                elif r'透過損益按公允價值衡量之金融負債－流動' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.current_financial_liabilities_fair_value_through_profit_or_loss = st_to_decimal(next_data.string)
                elif r'避險之衍生金融負債－流動' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.current_derivative_financial_liabilities_for_hedging = st_to_decimal(next_data.string)
                elif r'應付票據' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.total_notes_payable = st_to_decimal(next_data.string)
                elif r'應付帳款－關係人' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.total_accounts_payable_to_related_parties = st_to_decimal(next_data.string)
                elif r'其他應付款項－關係人' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.other_payables_to_related_parties = st_to_decimal(next_data.string)
                elif r'其他應付款' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.total_other_payables = st_to_decimal(next_data.string)
                elif r'應付帳款' in data.string.encode('utf-8') or r'應付款項' in data.string.encode('utf-8'):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        balance_sheet.total_accounts_payable = st_to_decimal(next_data.string)
                elif r'應付建造合約款－關係人' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.construction_contracts_payable_to_related_parties = st_to_decimal(next_data.string)
                elif r'應付建造合約款' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.construction_contracts_payable = st_to_decimal(next_data.string)
                elif r'當期所得稅負債' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.current_tax_liabilities = st_to_decimal(next_data.string)
                elif r'負債準備－流動' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.current_provisions = st_to_decimal(next_data.string)
                elif r'其他流動負債' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.total_other_current_liabilities = st_to_decimal(next_data.string)
                elif r'流動負債合計' in data.string.encode('utf-8') and r'非' not in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.total_current_liabilities = st_to_decimal(next_data.string)
                elif r'避險之衍生金融負債－非流動' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.non_current_derivative_financial_liabilities_for_hedeging = st_to_decimal(next_data.string)
                elif r'長期借款' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.total_long_term_borrowings = st_to_decimal(next_data.string)
                elif r'負債準備－非流動' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.total_non_current_provisions = st_to_decimal(next_data.string)
                elif r'遞延所得稅負債' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.total_deferred_tax_liabilities = st_to_decimal(next_data.string)
                elif r'其他非流動負債' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.other_non_current_liabilities = st_to_decimal(next_data.string)
                elif r'非流動負債合計' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.total_non_current_liabilities = st_to_decimal(next_data.string)
                elif r'負債總額' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.total_liabilities = st_to_decimal(next_data.string)
                elif r'普通股股本' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.ordinary_share = st_to_decimal(next_data.string)
                elif r'股本合計' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.total_capital_stock = st_to_decimal(next_data.string)
                elif r'資本公積－發行溢價' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.additional_paid_in_capital = st_to_decimal(next_data.string)
                elif r'資本公積－庫藏股票交易' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.treasury_share_transactions = st_to_decimal(next_data.string)
                elif r'資本公積－合併溢額' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.net_assets_from_merger = st_to_decimal(next_data.string)
                elif r'資本公積合計' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.total_capital_surplus = st_to_decimal(next_data.string)
                elif r'法定盈餘公積' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.legal_reserve = st_to_decimal(next_data.string)
                elif r'特別盈餘公積' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.special_reserve = st_to_decimal(next_data.string)
                elif r'未分配盈餘（或待彌補虧損）' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.total_unappropriated_retained_earnings_or_accumulated_deficit = st_to_decimal(next_data.string)
                elif r'保留盈餘合計' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.total_retained_earnings = st_to_decimal(next_data.string)
                elif r'國外營運機構財務報表換算之兌換差額' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.exchange_differences_of_foreign_financial_statements = st_to_decimal(next_data.string)
                elif r'備供出售金融資產未實現損益' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.unrealised_gains_for_sale_financial_assets = st_to_decimal(next_data.string)
                elif r'其他權益合計' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.other_equity_interest = st_to_decimal(next_data.string)
                elif r'歸屬於母公司業主之權益合計' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.total_equity_attributable_to_owners_of_parent = st_to_decimal(next_data.string)
                elif r'共同控制下前手權益' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.equity_attributable_to_former_owner_of_business_combination = st_to_decimal(next_data.string)
                elif r'非控制權益' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.non_controlling_interests = st_to_decimal(next_data.string)
                elif r'權益總額' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.total_equity = st_to_decimal(next_data.string)
                elif r'待註銷股本股數（單位：股）' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.number_of_shares_capital_awaiting_retirement = st_to_decimal(next_data.string)
                elif r'預收股款（權益項下）之約當發行股數（單位：股）' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.equivalent_issue_shares_of_advance_receipts = st_to_decimal(next_data.string)
                elif r'母公司暨子公司所持有之母公司庫藏股股數（單位：股）' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.number_of_shares_in_entity_held_by_entity = st_to_decimal(next_data.string)
                elif r'存放央行及拆款同業' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.due_from_the_central_bank_and_call_loans_to_banks = st_to_decimal(next_data.string)
                elif r'避險之衍生金融資產' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.derivative_financial_assets_for_hedging = st_to_decimal(next_data.string)
                elif r'待出售資產－淨額' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.net_assets_classified_as_held_for_sale = st_to_decimal(next_data.string)
                elif r'貼現及放款－淨額' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.net_loans_discounted = st_to_decimal(next_data.string)
                elif r'再保險合約資產－淨額' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.net_reinsurance_contract_assets = st_to_decimal(next_data.string)
                elif r'其他金融資產－淨額' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.net_other_financial_assets = st_to_decimal(next_data.string)
                elif r'不動產及設備－淨額' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.net_property_and_equipment = st_to_decimal(next_data.string)
                elif r'其他資產－淨額' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.net_other_assets = st_to_decimal(next_data.string)
                elif r'央行及金融同業存款' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.deposits_from_the_central_bank_and_banks = st_to_decimal(next_data.string)
                elif r'央行及同業融資' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.due_to_the_central_bank_and_banks = st_to_decimal(next_data.string)
                elif r'附買回票券及債券負債' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.securities_sold_under_repurchase_agreements = st_to_decimal(next_data.string)
                elif r'應付商業本票－淨額' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.net_commercial_papers_issued = st_to_decimal(next_data.string)
                elif r'存款及匯款' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.deposits = st_to_decimal(next_data.string)
                elif r'負債準備' in data.string.encode('utf-8'):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        balance_sheet.total_provisions = st_to_decimal(next_data.string)
                elif r'其他金融負債' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.total_other_financial_liabilities = st_to_decimal(next_data.string)
                elif r'其他負債' in data.string.encode('utf-8'):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        balance_sheet.total_other_liabilities = st_to_decimal(next_data.string)
                elif r'庫藏股票' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.treasury_share = st_to_decimal(next_data.string)
            if balance_sheet.total_cash_and_cash_equivalents:
                balance_sheet.save()
            else:
                print stock_symbol + ' time sleep'
                time.sleep(5)

            print stock_symbol + ' data updated'
    
    return HttpResponse('balance sheet updated')

#現金流量表
def show_statements_of_cashflows(reqquest):
    url = 'http://mops.twse.com.tw/mops/web/t164sb05'
    year = 102
    season = 2
    values = {'encodeURIComponent' : '1', 'step' : '1', 'firstin' : '1', 'off' : '1',
            'keyword4' : '','code1' : '','TYPEK2' : '','checkbtn' : '',
            'queryName':'co_id', 'TYPEK':'all', 'isnew':'true', 'co_id' : 8109, 'year' : year, 'season' : str(season).zfill(2) }
    # values = {'encodeURIComponent' : '1', 'id' : '', 'key' : '', 'TYPEK' : 'all', 'step' : '2',
    #           'year' : '102', 'season' : '2', 'co_id' : stock_symbol, 'firstin' : '1'}
    url_data = urllib.urlencode(values) 
    req = urllib2.Request(url, url_data)
    response = urllib2.urlopen(req)

    soup = BeautifulSoup(response,from_encoding="utf-8")
    # print soup 詳細資料
    detail_button = soup.find_all("input", {'type': 'button', 'value': r'詳細資訊'})
    print detail_button

    balance_sheet_datas = soup.find_all("td", {'style' : 'text-align:left;white-space:nowrap;'})
    # for data in balance_sheet_datas:
    #     if r'現金及約當現金' in data.string.encode('utf-8'):
    #         next_data = data.next_sibling.next_sibling
    #         print st_to_decimal(next_data.string)
    #         next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
    #         print st_to_decimal(next_data.string)
    req = urllib2.Request(url, url_data)
    response = urllib2.urlopen(req)
    return HttpResponse(response.read())

def update_season_cashflow_statement(request):
    if 'year' in request.GET and  'season' in request.GET:
        year = int(request.GET['year'])
        season = int(request.GET['season'])
    else:
        today = datetime.datetime.now()
        year, season = last_season(today)
    stockIDs = get_updated_id(year, season)
    # stockIDs = ['2330', '8114']
    for stock_id in stockIDs:
        stock_symbol = stock_id
        if not SeasonCashFlowStatement.objects.filter(symbol=stock_symbol, year=year, season=season):
            print stock_symbol + ' loaded'
            url = 'http://mops.twse.com.tw/mops/web/t164sb05'
            values = {'encodeURIComponent' : '1', 'id' : '', 'key' : '', 'TYPEK' : 'all', 'step' : '2',
                    'year' : str(year-1911), 'season' : str(season).zfill(1), 'co_id' : stock_symbol, 'firstin' : '1'}
            url_data = urllib.urlencode(values)
            headers = {'User-Agent': 'Mozilla/5.0'}
            req = urllib2.Request(url, url_data, headers)
            try:
                response = urllib2.urlopen(req)
                soup = BeautifulSoup(response,from_encoding="utf-8")
                cashflos_datas = soup.find_all("td", {'style' : 'text-align:left;white-space:nowrap;'})
                busy_msg = soup.find('table', attrs = {'width':'80%', 'border':'0','cellspacing':'8'})
            except URLError, e:
                print stock_symbol + ' time sleep'
                time.sleep(20)
                busy_msg = True
                if hasattr(e, "reason"):
                    print(stock_symbol + " Reason:"), e.reason
                elif hasattr(e, "code"):
                    print(stock_symbol + " Error code:"), e.code
            # 如果連線正常，還得再確認是否因查詢頻繁而給空表格；若有，則先sleep再重新連線
            while (busy_msg is not None):
                response.close()
                headers = {'User-Agent': 'Mozilla/4.0'}
                req = urllib2.Request(url, url_data, headers)
                try:
                    response = urllib2.urlopen(req)
                    soup = BeautifulSoup(response,from_encoding="utf-8")
                    cashflos_datas = soup.find_all("td", {'style' : 'text-align:left;white-space:nowrap;'})
                    busy_msg = soup.find('table', attrs = {'width':'80%', 'border':'0','cellspacing':'8'})
                except URLError, e:
                    busy_msg = True
                    if hasattr(e, "reason"):
                        print(stock_symbol + " Reason:"), e.reason
                    elif hasattr(e, "code"):
                        print(stock_symbol + " Error code:"), e.code
                if busy_msg:
                    print stock_symbol + ' time sleep' 
                    time.sleep(20)
            cashflow = SeasonCashFlowStatement()
            cashflow.symbol = stock_symbol
            cashflow.year = str(year)
            cashflow.season = season
            cashflow.date = season_to_date(year, season)
            cashflow.surrogate_key = stock_symbol + '_' + str(year) + str(season).zfill(2)
            if season == 1:
                prevSeasonData = None
            elif season == 2:
                prevSeasonData = SeasonCashFlowStatement.objects.filter(symbol=stock_symbol, year=year, season__lte=1)
            elif season == 3:
                prevSeasonData = SeasonCashFlowStatement.objects.filter(symbol=stock_symbol, year=year, season__lte=2)
            elif season == 4:
                prevSeasonData = SeasonCashFlowStatement.objects.filter(symbol=stock_symbol, year=year, season__lte=3)
            for data in cashflos_datas:
                if data.string != None and (r'繼續營業單位稅前淨利（淨損）' in data.string.encode('utf-8') or r'繼續營業單位稅前（淨利）淨損' in data.string.encode('utf-8')):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        cashflow.profit_loss_from_continuing_operations_before_tax = st_to_decimal(next_data.string) if prevSeasonData is None else st_to_decimal(next_data.string) - prevSeasonData.aggregate(sum=Sum('profit_loss_from_continuing_operations_before_tax'))['sum']
                if data.string != None and r'本期稅前淨利' in data.string.encode('utf-8'):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        cashflow.profit_loss_before_tax = st_to_decimal(next_data.string) if prevSeasonData is None else st_to_decimal(next_data.string) - prevSeasonData.aggregate(sum=Sum('profit_loss_before_tax'))['sum']
                if data.string != None and r'折舊費用' in data.string.encode('utf-8'):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        cashflow.depreciation_expense = st_to_decimal(next_data.string) if prevSeasonData is None else st_to_decimal(next_data.string) - prevSeasonData.aggregate(sum=Sum('depreciation_expense'))['sum']
                if data.string != None and r'攤銷費用' in data.string.encode('utf-8'):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        cashflow.amortization_expense = st_to_decimal(next_data.string) if prevSeasonData is None else st_to_decimal(next_data.string) - prevSeasonData.aggregate(sum=Sum('amortization_expense'))['sum']
                if data.string != None and r'利息費用' in data.string.encode('utf-8'):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        cashflow.interest_expense = st_to_decimal(next_data.string) if prevSeasonData is None else st_to_decimal(next_data.string) - prevSeasonData.aggregate(sum=Sum('interest_expense'))['sum']
                if data.string != None and r'利息收入' in data.string.encode('utf-8'):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        cashflow.interest_income = st_to_decimal(next_data.string) if prevSeasonData is None else st_to_decimal(next_data.string) - prevSeasonData.aggregate(sum=Sum('interest_income'))['sum']
                if data.string != None and r'股份基礎給付酬勞成本' in data.string.encode('utf-8'):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        cashflow.share_based_payments = st_to_decimal(next_data.string) if prevSeasonData is None else st_to_decimal(next_data.string) - prevSeasonData.aggregate(sum=Sum('share_based_payments'))['sum']
                if data.string != None and (r'採用權益法認列之關聯企業及合資損失（利益）之份額' in data.string.encode('utf-8') or r'採用權益法認列之關聯企業及合資（損失）利益之份額' in data.string.encode('utf-8')):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        cashflow.share_of_profit_loss_of_associates_using_equity_method = st_to_decimal(next_data.string) if prevSeasonData is None else st_to_decimal(next_data.string) - prevSeasonData.aggregate(sum=Sum('share_of_profit_loss_of_associates_using_equity_method'))['sum']
                if data.string != None and (r'處分及報廢不動產、廠房及設備損失（利益）' in data.string.encode('utf-8') or r'處分及報廢不動產、廠房及設備（損失）利益' in data.string.encode('utf-8')):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        cashflow.loss_gain_on_disposal_of_property_plan_and_equipment = st_to_decimal(next_data.string) if prevSeasonData is None else st_to_decimal(next_data.string) - prevSeasonData.aggregate(sum=Sum('loss_gain_on_disposal_of_property_plan_and_equipment'))['sum']
                if data.string != None and (r'處分投資損失（利益）' in data.string.encode('utf-8') or r'處分投資（損失）利益' in data.string.encode('utf-8')):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        cashflow.loss_gain_on_disposal_of_investments = st_to_decimal(next_data.string) if prevSeasonData is None else st_to_decimal(next_data.string) - prevSeasonData.aggregate(sum=Sum('loss_gain_on_disposal_of_investments'))['sum']
                if data.string != None and (r'處分採用權益法之投資損失（利益）' in data.string.encode('utf-8') or r'處分採用權益法之投資（損失）利益' in data.string.encode('utf-8')):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        cashflow.loss_gain_on_disposal_of_investments_using_equity_method = st_to_decimal(next_data.string) if prevSeasonData is None else st_to_decimal(next_data.string) - prevSeasonData.aggregate(sum=Sum('loss_gain_on_disposal_of_investments_using_equity_method'))['sum']
                if data.string != None and r'金融資產減損損失' in data.string.encode('utf-8') and r'非' not in data.string.encode('utf-8'):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        cashflow.impairment_loss_on_financial_assets = st_to_decimal(next_data.string) if prevSeasonData is None else st_to_decimal(next_data.string) - prevSeasonData.aggregate(sum=Sum('impairment_loss_on_financial_assets'))['sum']
                if data.string != None and r'非金融資產減損損失' in data.string.encode('utf-8'):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        cashflow.impairment_loss_on_non_financial_assets = st_to_decimal(next_data.string) if prevSeasonData is None else st_to_decimal(next_data.string) - prevSeasonData.aggregate(sum=Sum('impairment_loss_on_non_financial_assets'))['sum']
                if data.string != None and (r'已實現銷貨損失（利益）' in data.string.encode('utf-8') or r'已實現銷貨（損失）利益' in data.string.encode('utf-8')):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        cashflow.realized_loss_profit_on_from_sales = st_to_decimal(next_data.string) if prevSeasonData is None else st_to_decimal(next_data.string) - prevSeasonData.aggregate(sum=Sum('realized_loss_profit_on_from_sales'))['sum']
                if data.string != None and (r'未實現外幣兌換損失（利益）' in data.string.encode('utf-8') or r'未實現外幣兌換（損失）利益' in data.string.encode('utf-8')):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        cashflow.unrealized_foreign_exchange_loss_gain = st_to_decimal(next_data.string) if prevSeasonData is None else st_to_decimal(next_data.string) - prevSeasonData.aggregate(sum=Sum('unrealized_foreign_exchange_loss_gain'))['sum']
                if data.string != None and r'其他項目' in data.string.encode('utf-8'):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        cashflow.other_adjustments_to_reconcile_profit_loss = st_to_decimal(next_data.string) if prevSeasonData is None else st_to_decimal(next_data.string) - prevSeasonData.aggregate(sum=Sum('other_adjustments_to_reconcile_profit_loss'))['sum']
                if data.string != None and r'不影響現金流量之收益費損項目合計' in data.string.encode('utf-8'):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        cashflow.total_adjustments_to_reconcile_profit_loss = st_to_decimal(next_data.string) if prevSeasonData is None else st_to_decimal(next_data.string) - prevSeasonData.aggregate(sum=Sum('total_adjustments_to_reconcile_profit_loss'))['sum']
                if data.string != None and (r'持有供交易之金融資產（增加）減少' in data.string.encode('utf-8') or r'持有供交易之金融資產增加（減少）' in data.string.encode('utf-8')):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        cashflow.decrease_increase_in_financial_assets_held_for_trading = st_to_decimal(next_data.string) if prevSeasonData is None else st_to_decimal(next_data.string) - prevSeasonData.aggregate(sum=Sum('decrease_increase_in_financial_assets_held_for_trading'))['sum']
                if data.string != None and (r'避險之衍生金融資產（增加）減少' in data.string.encode('utf-8') or r'避險之衍生金融資產增加（減少）' in data.string.encode('utf-8')):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        cashflow.decrease_increase_in_derivative_financial_assets_for_hedging = st_to_decimal(next_data.string) if prevSeasonData is None else st_to_decimal(next_data.string) - prevSeasonData.aggregate(sum=Sum('decrease_increase_in_derivative_financial_assets_for_hedging'))['sum']
                if data.string != None and (r'應收帳款（增加）減少' in data.string.encode('utf-8') or r'應收帳款增加（減少）' in data.string.encode('utf-8')):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        cashflow.decrease_increase_in_accounts_receivable = st_to_decimal(next_data.string) if prevSeasonData is None else st_to_decimal(next_data.string) - prevSeasonData.aggregate(sum=Sum('decrease_increase_in_accounts_receivable'))['sum']
                if data.string != None and (r'應收帳款－關係人（增加）減少' in data.string.encode('utf-8') or r'應收帳款－關係人增加（減少）' in data.string.encode('utf-8')):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        cashflow.decrease_increase_in_accounts_receivable_from_related_parties = st_to_decimal(next_data.string) if prevSeasonData is None else st_to_decimal(next_data.string) - prevSeasonData.aggregate(sum=Sum('decrease_increase_in_accounts_receivable_from_related_parties'))['sum']
                if data.string != None and (r'其他應收款－關係人（增加）減少' in data.string.encode('utf-8') or r'其他應收款－關係人增加（減少）' in data.string.encode('utf-8')):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        cashflow.decrease_increase_in_other_receivable_due_from_related_parties = st_to_decimal(next_data.string) if prevSeasonData is None else st_to_decimal(next_data.string) - prevSeasonData.aggregate(sum=Sum('decrease_increase_in_other_receivable_due_from_related_parties'))['sum']
                if data.string != None and (r'存貨（增加）減少' in data.string.encode('utf-8') or r'存貨增加（減少）' in data.string.encode('utf-8')):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        cashflow.decrease_increase_in_inventories = st_to_decimal(next_data.string) if prevSeasonData is None else st_to_decimal(next_data.string) - prevSeasonData.aggregate(sum=Sum('decrease_increase_in_inventories'))['sum']
                if data.string != None and (r'其他流動資產（增加）減少' in data.string.encode('utf-8') or r'其他流動資產增加（減少）' in data.string.encode('utf-8')):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        cashflow.decrease_increase_in_other_current_assets = st_to_decimal(next_data.string) if prevSeasonData is None else st_to_decimal(next_data.string) - prevSeasonData.aggregate(sum=Sum('decrease_increase_in_other_current_assets'))['sum']
                if data.string != None and (r'其他金融資產（增加）減少' in data.string.encode('utf-8') or r'其他金融資產增加（減少）' in data.string.encode('utf-8')):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        cashflow.decrease_increase_in_other_financial_assets = st_to_decimal(next_data.string) if prevSeasonData is None else st_to_decimal(next_data.string) - prevSeasonData.aggregate(sum=Sum('decrease_increase_in_other_financial_assets'))['sum']
                if data.string != None and r'與營業活動相關之資產之淨變動合計' in data.string.encode('utf-8'):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        cashflow.total_changes_in_operating_assets = st_to_decimal(next_data.string) if prevSeasonData is None else st_to_decimal(next_data.string) - prevSeasonData.aggregate(sum=Sum('total_changes_in_operating_assets'))['sum']
                if data.string != None and (r'應付帳款增加（減少）' in data.string.encode('utf-8') or r'應付帳款（增加）減少' in data.string.encode('utf-8')):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        cashflow.increase_decrease_in_accounts_payable = st_to_decimal(next_data.string) if prevSeasonData is None else st_to_decimal(next_data.string) - prevSeasonData.aggregate(sum=Sum('increase_decrease_in_accounts_payable'))['sum']
                if data.string != None and (r'應付帳款－關係人（增加）減少' in data.string.encode('utf-8') or r'應付帳款－關係人增加（減少）' in data.string.encode('utf-8')):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        cashflow.increase_decrease_in_accounts_payable_to_related_parties = st_to_decimal(next_data.string) if prevSeasonData is None else st_to_decimal(next_data.string) - prevSeasonData.aggregate(sum=Sum('increase_decrease_in_accounts_payable_to_related_parties'))['sum']
                if data.string != None and (r'負債準備增加（減少）' in data.string.encode('utf-8') or r'負債準備（增加）減少' in data.string.encode('utf-8')):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        cashflow.increase_decrease_in_provisions = st_to_decimal(next_data.string) if prevSeasonData is None else st_to_decimal(next_data.string) - prevSeasonData.aggregate(sum=Sum('increase_decrease_in_provisions'))['sum']
                if data.string != None and (r'其他流動負債增加（減少）' in data.string.encode('utf-8') or r'其他流動負債（增加）減少' in data.string.encode('utf-8')):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        cashflow.increase_decrease_in_other_current_liabilities = st_to_decimal(next_data.string) if prevSeasonData is None else st_to_decimal(next_data.string) - prevSeasonData.aggregate(sum=Sum('increase_decrease_in_other_current_liabilities'))['sum']
                if data.string != None and (r'應計退休金負債增加（減少）' in data.string.encode('utf-8') or r'應計退休金負債（增加）減少' in data.string.encode('utf-8')):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        cashflow.increase_decrease_in_accrued_pension_liabilities = st_to_decimal(next_data.string) if prevSeasonData is None else st_to_decimal(next_data.string) - prevSeasonData.aggregate(sum=Sum('increase_decrease_in_accrued_pension_liabilities'))['sum']
                if data.string != None and (r'其他營業負債增加（減少）' in data.string.encode('utf-8') or r'其他營業負債（增加）減少' in data.string.encode('utf-8')):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        cashflow.increase_decrease_in_other_operating_liabilities = st_to_decimal(next_data.string) if prevSeasonData is None else st_to_decimal(next_data.string) - prevSeasonData.aggregate(sum=Sum('increase_decrease_in_other_operating_liabilities'))['sum']
                if data.string != None and r'與營業活動相關之負債之淨變動合計' in data.string.encode('utf-8'):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        cashflow.total_changes_in_operating_liabilities = st_to_decimal(next_data.string) if prevSeasonData is None else st_to_decimal(next_data.string) - prevSeasonData.aggregate(sum=Sum('total_changes_in_operating_liabilities'))['sum']
                if data.string != None and r'與營業活動相關之資產及負債之淨變動合計' in data.string.encode('utf-8'):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        cashflow.total_changes_in_operating_assets_and_liabilities = st_to_decimal(next_data.string) if prevSeasonData is None else st_to_decimal(next_data.string) - prevSeasonData.aggregate(sum=Sum('total_changes_in_operating_assets_and_liabilities'))['sum']
                if data.string != None and r'調整項目合計' in data.string.encode('utf-8'):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        cashflow.total_adjustments = st_to_decimal(next_data.string) if prevSeasonData is None else st_to_decimal(next_data.string) - prevSeasonData.aggregate(sum=Sum('total_adjustments'))['sum']
                if data.string != None and (r'營運產生之現金流入（流出）' in data.string.encode('utf-8') or r'營運產生之現金（流入）流出' in data.string.encode('utf-8')):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        cashflow.cash_inflow_outflow_generated_from_operations = st_to_decimal(next_data.string) if prevSeasonData is None else st_to_decimal(next_data.string) - prevSeasonData.aggregate(sum=Sum('cash_inflow_outflow_generated_from_operations'))['sum']
                if data.string != None and (r'退還（支付）之所得稅' in data.string.encode('utf-8') or r'（退還）支付之所得稅' in data.string.encode('utf-8')):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        cashflow.income_taxes_refund_paid = st_to_decimal(next_data.string) if prevSeasonData is None else st_to_decimal(next_data.string) - prevSeasonData.aggregate(sum=Sum('income_taxes_refund_paid'))['sum']
                if data.string != None and (r'營業活動之淨現金流入（流出）' in data.string.encode('utf-8') or r'營業活動之淨現金（流入）流出' in data.string.encode('utf-8')):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        cashflow.net_cash_flows_from_used_in_operating_activities = st_to_decimal(next_data.string) if prevSeasonData is None else st_to_decimal(next_data.string) - prevSeasonData.aggregate(sum=Sum('net_cash_flows_from_used_in_operating_activities'))['sum']
                if data.string != None and r'取得備供出售金融資產' in data.string.encode('utf-8'):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        cashflow.acquisition_of_available_for_sale_financial_assets = st_to_decimal(next_data.string) if prevSeasonData is None else st_to_decimal(next_data.string) - prevSeasonData.aggregate(sum=Sum('acquisition_of_available_for_sale_financial_assets'))['sum']
                if data.string != None and r'處分備供出售金融資產' in data.string.encode('utf-8'):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        cashflow.proceeds_from_disposal_of_available_for_sale_financial_assets = st_to_decimal(next_data.string) if prevSeasonData is None else st_to_decimal(next_data.string) - prevSeasonData.aggregate(sum=Sum('proceeds_from_disposal_of_available_for_sale_financial_assets'))['sum']
                if data.string != None and r'取得持有至到期日金融資產' in data.string.encode('utf-8'):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        cashflow.acquisition_of_held_to_maturity_financial_assets = st_to_decimal(next_data.string) if prevSeasonData is None else st_to_decimal(next_data.string) - prevSeasonData.aggregate(sum=Sum('acquisition_of_held_to_maturity_financial_assets'))['sum']
                if data.string != None and r'持有至到期日金融資產到期還本' in data.string.encode('utf-8'):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        cashflow.proceeds_from_repayments_of_held_to_maturity_financial_assets = st_to_decimal(next_data.string) if prevSeasonData is None else st_to_decimal(next_data.string) - prevSeasonData.aggregate(sum=Sum('proceeds_from_repayments_of_held_to_maturity_financial_assets'))['sum']
                if data.string != None and r'取得以成本衡量之金融資產' in data.string.encode('utf-8'):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        cashflow.acquisition_of_financial_assets_at_cost = st_to_decimal(next_data.string) if prevSeasonData is None else st_to_decimal(next_data.string) - prevSeasonData.aggregate(sum=Sum('acquisition_of_financial_assets_at_cost'))['sum']
                if data.string != None and r'處分以成本衡量之金融資產' in data.string.encode('utf-8'):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        cashflow.proceeds_from_disposal_of_financial_assets_at_cost = st_to_decimal(next_data.string) if prevSeasonData is None else st_to_decimal(next_data.string) - prevSeasonData.aggregate(sum=Sum('proceeds_from_disposal_of_financial_assets_at_cost'))['sum']
                if data.string != None and r'處分採用權益法之投資' in data.string.encode('utf-8'):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        cashflow.proceeds_from_disposal_of_investments_using_equity_method = st_to_decimal(next_data.string) if prevSeasonData is None else st_to_decimal(next_data.string) - prevSeasonData.aggregate(sum=Sum('proceeds_from_disposal_of_investments_using_equity_method'))['sum']
                if data.string != None and r'處分子公司' in data.string.encode('utf-8'):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        cashflow.proceeds_from_disposal_of_subsidiaries = st_to_decimal(next_data.string) if prevSeasonData is None else st_to_decimal(next_data.string) - prevSeasonData.aggregate(sum=Sum('proceeds_from_disposal_of_subsidiaries'))['sum']
                if data.string != None and r'取得不動產、廠房及設備' in data.string.encode('utf-8'):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        cashflow.acquisition_of_property_plant_and_equipment = st_to_decimal(next_data.string) if prevSeasonData is None else st_to_decimal(next_data.string) - prevSeasonData.aggregate(sum=Sum('acquisition_of_property_plant_and_equipment'))['sum']
                if data.string != None and r'處分不動產、廠房及設備' in data.string.encode('utf-8'):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        cashflow.proceeds_from_disposal_of_property_plant_and_equipment = st_to_decimal(next_data.string) if prevSeasonData is None else st_to_decimal(next_data.string) - prevSeasonData.aggregate(sum=Sum('proceeds_from_disposal_of_property_plant_and_equipment'))['sum']
                if data.string != None and r'存出保證金增加' in data.string.encode('utf-8'):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        cashflow.increase_in_refundable_deposits = st_to_decimal(next_data.string) if prevSeasonData is None else st_to_decimal(next_data.string) - prevSeasonData.aggregate(sum=Sum('increase_in_refundable_deposits'))['sum']
                if data.string != None and r'存出保證金減少' in data.string.encode('utf-8'):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        cashflow.decrease_in_refundable_deposits = st_to_decimal(next_data.string) if prevSeasonData is None else st_to_decimal(next_data.string) - prevSeasonData.aggregate(sum=Sum('decrease_in_refundable_deposits'))['sum']
                if data.string != None and r'取得無形資產' in data.string.encode('utf-8'):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        cashflow.acquisition_of_intangible_assets = st_to_decimal(next_data.string) if prevSeasonData is None else st_to_decimal(next_data.string) - prevSeasonData.aggregate(sum=Sum('acquisition_of_intangible_assets'))['sum']
                if data.string != None and (r'長期應收租賃款減少' in data.string.encode('utf-8') or r'應收租賃款減少' in data.string.encode('utf-8')):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        cashflow.decrease_in_long_term_lease_and_installment_receivables = st_to_decimal(next_data.string) if prevSeasonData is None else st_to_decimal(next_data.string) - prevSeasonData.aggregate(sum=Sum('decrease_in_long_term_lease_and_installment_receivables'))['sum']
                if data.string != None and (r'其他金融資產增加' in data.string.encode('utf-8') or r'其他金融資產（增加）減少' in data.string.encode('utf-8') or r'其他金融資產增加（減少）' in data.string.encode('utf-8')):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        cashflow.increase_in_other_financial_assets = st_to_decimal(next_data.string) if prevSeasonData is None else st_to_decimal(next_data.string) - prevSeasonData.aggregate(sum=Sum('increase_in_other_financial_assets'))['sum']
                if data.string != None and r'其他非流動資產增加' in data.string.encode('utf-8'):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        cashflow.increase_in_other_non_current_assets = st_to_decimal(next_data.string) if prevSeasonData is None else st_to_decimal(next_data.string) - prevSeasonData.aggregate(sum=Sum('increase_in_other_non_current_assets'))['sum']
                if data.string != None and r'收取之利息' in data.string.encode('utf-8'):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        cashflow.interest_received = st_to_decimal(next_data.string) if prevSeasonData is None else st_to_decimal(next_data.string) - prevSeasonData.aggregate(sum=Sum('interest_received'))['sum']
                if data.string != None and r'收取之股利' in data.string.encode('utf-8'):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        cashflow.dividends_received = st_to_decimal(next_data.string) if prevSeasonData is None else st_to_decimal(next_data.string) - prevSeasonData.aggregate(sum=Sum('dividends_received'))['sum']
                if data.string != None and r'其他投資活動' in data.string.encode('utf-8'):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        cashflow.other_investing_activities = st_to_decimal(next_data.string) if prevSeasonData is None else st_to_decimal(next_data.string) - prevSeasonData.aggregate(sum=Sum('other_investing_activities'))['sum']
                if data.string != None and (r'投資活動之淨現金流入（流出）' in data.string.encode('utf-8') or r'投資活動之淨現金（流入）流出' in data.string.encode('utf-8')):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        cashflow.net_cash_flows_from_used_in_investing_activities = st_to_decimal(next_data.string) if prevSeasonData is None else st_to_decimal(next_data.string) - prevSeasonData.aggregate(sum=Sum('net_cash_flows_from_used_in_investing_activities'))['sum']
                if data.string != None and r'短期借款增加' in data.string.encode('utf-8'):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        cashflow.increase_in_short_term_loans = st_to_decimal(next_data.string) if prevSeasonData is None else st_to_decimal(next_data.string) - prevSeasonData.aggregate(sum=Sum('increase_in_short_term_loans'))['sum']
                if data.string != None and r'發行公司債' in data.string.encode('utf-8'):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        cashflow.proceeds_from_issuing_bonds = st_to_decimal(next_data.string) if prevSeasonData is None else st_to_decimal(next_data.string) - prevSeasonData.aggregate(sum=Sum('proceeds_from_issuing_bonds'))['sum']
                if data.string != None and r'償還公司債' in data.string.encode('utf-8'):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        cashflow.repayments_of_bonds = st_to_decimal(next_data.string) if prevSeasonData is None else st_to_decimal(next_data.string) - prevSeasonData.aggregate(sum=Sum('repayments_of_bonds'))['sum']
                if data.string != None and r'舉借長期借款' in data.string.encode('utf-8'):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        cashflow.proceeds_from_long_term_debt = st_to_decimal(next_data.string) if prevSeasonData is None else st_to_decimal(next_data.string) - prevSeasonData.aggregate(sum=Sum('proceeds_from_long_term_debt'))['sum']
                if data.string != None and r'償還長期借款' in data.string.encode('utf-8'):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        cashflow.repayments_of_long_term_debt = st_to_decimal(next_data.string) if prevSeasonData is None else st_to_decimal(next_data.string) - prevSeasonData.aggregate(sum=Sum('repayments_of_long_term_debt'))['sum']
                if data.string != None and r'存入保證金增加' in data.string.encode('utf-8'):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        cashflow.increase_in_guarantee_deposits_received = st_to_decimal(next_data.string) if prevSeasonData is None else st_to_decimal(next_data.string) - prevSeasonData.aggregate(sum=Sum('increase_in_guarantee_deposits_received'))['sum']
                if data.string != None and r'存入保證金減少' in data.string.encode('utf-8'):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        cashflow.decrease_in_guarantee_deposits_received = st_to_decimal(next_data.string) if prevSeasonData is None else st_to_decimal(next_data.string) - prevSeasonData.aggregate(sum=Sum('decrease_in_guarantee_deposits_received'))['sum']
                if data.string != None and r'應付租賃款減少' in data.string.encode('utf-8'):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        cashflow.decrease_in_lease_payable = st_to_decimal(next_data.string) if prevSeasonData is None else st_to_decimal(next_data.string) - prevSeasonData.aggregate(sum=Sum('decrease_in_lease_payable'))['sum']
                if data.string != None and r'員工執行認股權' in data.string.encode('utf-8'):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        cashflow.exercise_of_employee_share_options = st_to_decimal(next_data.string) if prevSeasonData is None else st_to_decimal(next_data.string) - prevSeasonData.aggregate(sum=Sum('exercise_of_employee_share_options'))['sum']
                if data.string != None and r'支付之利息' in data.string.encode('utf-8'):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        cashflow.interest_paid = st_to_decimal(next_data.string) if prevSeasonData is None else st_to_decimal(next_data.string) - prevSeasonData.aggregate(sum=Sum('interest_paid'))['sum']
                if data.string != None and r'非控制權益變動' in data.string.encode('utf-8'):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        cashflow.change_in_non_controlling_interests = st_to_decimal(next_data.string) if prevSeasonData is None else st_to_decimal(next_data.string) - prevSeasonData.aggregate(sum=Sum('interest_income'))['sum']
                if data.string != None and r'其他籌資活動' in data.string.encode('utf-8'):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        cashflow.other_financing_activities = st_to_decimal(next_data.string) if prevSeasonData is None else st_to_decimal(next_data.string) - prevSeasonData.aggregate(sum=Sum('other_financing_activities'))['sum']
                if data.string != None and (r'籌資活動之淨現金流入（流出）' in data.string.encode('utf-8') or r'籌資活動之淨現金（流入）流出' in data.string.encode('utf-8')):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        cashflow.net_cash_flows_from_used_in_financing_activities = st_to_decimal(next_data.string) if prevSeasonData is None else st_to_decimal(next_data.string) - prevSeasonData.aggregate(sum=Sum('net_cash_flows_from_used_in_financing_activities'))['sum']
                if data.string != None and r'匯率變動對現金及約當現金之影響' in data.string.encode('utf-8'):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        cashflow.effect_of_exchange_rate_changes_on_cash_and_cash_equivalents = st_to_decimal(next_data.string) if prevSeasonData is None else st_to_decimal(next_data.string) - prevSeasonData.aggregate(sum=Sum('effect_of_exchange_rate_changes_on_cash_and_cash_equivalents'))['sum']
                if data.string != None and (r'本期現金及約當現金增加（減少）數' in data.string.encode('utf-8') or r'本期現金及約當現金（增加）減少數' in data.string.encode('utf-8')):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        cashflow.net_increase_decrease_in_cash_and_cash_equivalents = st_to_decimal(next_data.string) if prevSeasonData is None else st_to_decimal(next_data.string) - prevSeasonData.aggregate(sum=Sum('interest_income'))['sum']
                if data.string != None and r'期初現金及約當現金餘額' in data.string.encode('utf-8'):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        cashflow.cash_and_cash_equivalents_at_beginning_of_period = st_to_decimal(next_data.string) if prevSeasonData is None else st_to_decimal(next_data.string) - prevSeasonData.aggregate(sum=Sum('cash_and_cash_equivalents_at_beginning_of_period'))['sum']
                if data.string != None and r'期末現金及約當現金餘額' in data.string.encode('utf-8'):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        cashflow.cash_and_cash_equivalents_at_end_of_period = st_to_decimal(next_data.string) if prevSeasonData is None else st_to_decimal(next_data.string) - prevSeasonData.aggregate(sum=Sum('cash_and_cash_equivalents_at_end_of_period'))['sum']
                if data.string != None and r'資產負債表帳列之現金及約當現金' in data.string.encode('utf-8'):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        cashflow.cash_and_cash_equivalents_in_the_statement_of_financial_position = st_to_decimal(next_data.string) if prevSeasonData is None else st_to_decimal(next_data.string) - prevSeasonData.aggregate(sum=Sum('cash_and_cash_equivalents_in_the_statement_of_financial_position'))['sum']
                cashflow.free_cash_flow = cashflow.net_cash_flows_from_used_in_operating_activities + cashflow.net_cash_flows_from_used_in_investing_activities
                if data.string != None and r'利息收入' in data.string.encode('utf-8'):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        cashflow.interest_income = st_to_decimal(next_data.string) if prevSeasonData is None else st_to_decimal(next_data.string) - prevSeasonData.aggregate(sum=Sum('interest_income'))['sum']
            response.close()
            if cashflow.profit_loss_from_continuing_operations_before_tax:
                cashflow.save()

    return HttpResponse('cashflow statement updated')

def update_year_financial_ratio(request):
    stock_ids = StockId.objects.all()
    today = datetime.date.today()
    for stock_id in stock_ids:
        stock_symbol = stock_id.symbol
        ratioInDb = YearFinancialRatio.objects.filter(symbol=stock_symbol, year=today.year-1)
        if ratioInDb:
            continue
        url = 'http://jsjustweb.jihsun.com.tw/z/zc/zcr/zcra/zcra_' + stock_symbol + '.djhtm'
        webcode = urllib.urlopen(url)
        soup = BeautifulSoup(webcode)
        stage_datas = soup.find_all('td', {'class':'t2'})

        isDataStart = False
        arrRatioDatas = []
        for stage_data in stage_datas:
            if isDataStart:
                if stage_data.string.encode('utf-8') == r'期別':
                    break
                year = int(stage_data.string.split('.')[0]) + 1911
                year_ratio = YearFinancialRatio()
                year_ratio.surrogate_key = stock_symbol + '_' + str(year)
                year_ratio.year = year
                year_ratio.date = datetime.date(year, 1, 1)
                year_ratio.symbol = stock_symbol
                year_ratio.date = datetime.date(year, 1, 1)
                arrRatioDatas.append(year_ratio)
            if stage_data.string.encode('utf-8') == r'期別':
                isDataStart = True
        ratio_datas = soup.find_all('td', {'class':'t4t1'})
        for ratio_data in ratio_datas:
            next = ratio_data.next_sibling.next_sibling
            if ratio_data.string.encode('utf-8') == r'營業毛利率':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.gross_profit_margin = st_to_decimal(next.string)
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'營業利益率':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.operating_profit_margin = st_to_decimal(next.string)
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'稅前淨利率':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.net_before_tax_profit_margin = st_to_decimal(next.string)
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'稅後淨利率':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.net_after_tax_profit_margin = st_to_decimal(next.string)
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'每股淨值(元)':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.net_value_per_share = st_to_decimal(next.string)
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'每股營業額(元)':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.revenue_per_share = st_to_decimal(next.string)
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'每股營業利益(元)':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.operating_profit_per_share = st_to_decimal(next.string)
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'每股稅前淨利(元)':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.net_before_tax_profit_per_share = st_to_decimal(next.string)
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'股東權益報酬率':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.return_on_equity = st_to_decimal(next.string)
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'資產報酬率':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.return_on_assets = st_to_decimal(next.string)
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'每股稅後淨利(元)':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.net_after_tax_profit_per_share = st_to_decimal(next.string)
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'營收成長率':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.revenue_growth_rate = st_to_decimal(next.string)
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'營業利益成長率':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.operating_profit_growth_rate = st_to_decimal(next.string)
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'稅前淨利成長率':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.net_before_tax_profit_growth_rate = st_to_decimal(next.string)
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'稅後淨利成長率':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.net_after_tax_profit_growth_rate = st_to_decimal(next.string)
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'總資產成長率':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.assets_growth_rate = st_to_decimal(next.string)
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'淨值成長率':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.net_value_growth_rate = st_to_decimal(next.string)
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'固定資產成長率':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.fixed_assets_growth_rate = st_to_decimal(next.string)
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'流動比率':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.current_ratio = st_to_decimal(next.string)
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'速動比率':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.quick_ratio = st_to_decimal(next.string)
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'負債比率':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.debt_ratio = st_to_decimal(next.string)
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'利息保障倍數':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.interest_cover = st_to_decimal(next.string)
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'應收帳款週轉率(次)':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.account_receivable_turnover_ratio = st_to_decimal(next.string)
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'存貨週轉率(次)':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.inventory_turnover_ratio = st_to_decimal(next.string)
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'固定資產週轉率(次)':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.fixed_assets_turnover_ratio = st_to_decimal(next.string)
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'總資產週轉率(次)':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.assets_turnover_ratio = st_to_decimal(next.string)
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'員工平均營業額(千元)':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.revenue_per_employee = st_to_decimal(next.string)
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'淨值週轉率':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.equity_turnover_ratio = st_to_decimal(next.string)
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'負債對淨值比率':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.debt_equity_ratio = st_to_decimal(next.string)
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'長期資金適合率':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.long_term_funds_to_fixed_assets = st_to_decimal(next.string)
                    next = next.next_sibling.next_sibling
        for ratio in arrRatioDatas:
            ratio.save()
        print ('update ' + stock_symbol + ' year financial ratio')

    return HttpResponse('update year financial ratio')

def update_season_financial_ratio(request):
    stock_ids = StockId.objects.all()
    if 'year' in request.GET and  'season' in request.GET:
        input_year = int(request.GET['year'])
        input_season = int(request.GET['season'])
    else:
        return HttpResponse('please input year or season')
    for stock_id in stock_ids:
        stock_symbol = stock_id.symbol
        ratioInDb = SeasonFinancialRatio.objects.filter(symbol=stock_symbol, year=input_year, season=input_season)
        if ratioInDb:
            ratioInDb = None
            continue
        url = 'http://jsjustweb.jihsun.com.tw/z/zc/zcr/zcr_' + stock_symbol + '.djhtm'
        webcode = urllib.urlopen(url)
        soup = BeautifulSoup(webcode)
        stage_datas = soup.find_all('td', {'class':'t2'})

        isDataStart = False
        arrRatioDatas = []
        for stage_data in stage_datas:
            if isDataStart:
                try:
                    year = int(stage_data.string.split('Q')[0].split('.')[0]) + int(1911)
                    season = int(stage_data.string.split('Q')[0].split('.')[1])
                    season_ratio = SeasonFinancialRatio()
                    season_ratio.surrogate_key = stock_symbol + '_' + str(year) + str(season).zfill(2)
                    season_ratio.year = year
                    season_ratio.season = season
                    season_ratio.symbol = stock_symbol
                    if season == 1:
                        season_ratio.date = datetime.date(year, 1, 1)
                    elif season == 2:
                        season_ratio.date = datetime.date(year, 4, 1)
                    elif season == 3:
                        season_ratio.date = datetime.date(year, 7, 1)
                    elif season == 4:
                        season_ratio.date = datetime.date(year, 10, 1)
                    arrRatioDatas.append(season_ratio)
                except:
                    break
            if stage_data.string.encode('utf-8') == r'期別':
                isDataStart = True
        ratio_datas = soup.find_all('td', {'class':'t4t1'})
        for ratio_data in ratio_datas:
            next = ratio_data.next_sibling
            if ratio_data.string.encode('utf-8') == r'營業毛利率':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.gross_profit_margin = st_to_decimal(next.string)
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'營業利益率':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.operating_profit_margin = st_to_decimal(next.string)
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'稅前淨利率':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.net_before_tax_profit_margin = st_to_decimal(next.string)
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'稅後淨利率':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.net_after_tax_profit_margin = st_to_decimal(next.string)
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'每股淨值(元)':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.net_value_per_share = st_to_decimal(next.string)
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'每股營業額(元)':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.revenue_per_share = st_to_decimal(next.string)
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'每股營業利益(元)':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.operating_profit_per_share = st_to_decimal(next.string)
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'每股稅前淨利(元)':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.net_before_tax_profit_per_share = st_to_decimal(next.string)
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'股東權益報酬率':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.return_on_equity = st_to_decimal(next.string)
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'資產報酬率':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.return_on_assets = st_to_decimal(next.string)
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'每股稅後淨利(元)':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.net_after_tax_profit_per_share = st_to_decimal(next.string)
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'營收成長率':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.revenue_growth_rate = st_to_decimal(next.string)
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'營業利益成長率':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.operating_profit_growth_rate = st_to_decimal(next.string)
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'稅前淨利成長率':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.net_before_tax_profit_growth_rate = st_to_decimal(next.string)
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'稅後淨利成長率':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.net_after_tax_profit_growth_rate = st_to_decimal(next.string)
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'總資產成長率':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.assets_growth_rate = st_to_decimal(next.string)
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'淨值成長率':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.net_value_growth_rate = st_to_decimal(next.string)
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'固定資產成長率':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.fixed_assets_growth_rate = st_to_decimal(next.string)
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'流動比率':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.current_ratio = st_to_decimal(next.string)
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'速動比率':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.quick_ratio = st_to_decimal(next.string)
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'負債比率':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.debt_ratio = st_to_decimal(next.string)
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'利息保障倍數':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.interest_cover = st_to_decimal(next.string)
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'應收帳款週轉率(次)':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.account_receivable_turnover_ratio = st_to_decimal(next.string)
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'存貨週轉率(次)':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.inventory_turnover_ratio = st_to_decimal(next.string)
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'固定資產週轉率(次)':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.fixed_assets_turnover_ratio = st_to_decimal(next.string)
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'總資產週轉率(次)':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.assets_turnover_ratio = st_to_decimal(next.string)
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'員工平均營業額(千元)':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.revenue_per_employee = st_to_decimal(next.string)
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'淨值週轉率':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.equity_turnover_ratio = st_to_decimal(next.string)
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'負債對淨值比率':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.debt_equity_ratio = st_to_decimal(next.string)
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'長期資金適合率':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.long_term_funds_to_fixed_assets = st_to_decimal(next.string)
                    next = next.next_sibling.next_sibling
        for ratio in arrRatioDatas:
            ratio.save()
        print ('update ' + stock_symbol + ' season financial ratio')

    return HttpResponse('update season financial ratio')
