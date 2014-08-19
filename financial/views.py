#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib2
import urllib
from django.http import HttpResponse
from HTMLParser import HTMLParser
import time
from decimal import Decimal
from stocks.models import StockId
from financial.models import SeasonFinancialRatio, SeasonBalanceSheet, SeasonIncomeStatement, YearFinancialRatio
from stocks.models import SeasonRevenue
from bs4 import BeautifulSoup
import html5lib
import datetime
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

def get_financial_company(request):
    stock_type = ['sii', 'otc']
    company_list = []
    year = 2013
    season = 2
    url = 'http://mops.twse.com.tw/mops/web/t163sb14'
    values = {'encodeURIComponent': '1', 'step': '1', 'firstin': '1', 'off': '1', 
              'TYPEK': 'sii', 'year': str(year-1911), 'season': str(season).zfill(2)} 
    url_data = urllib.urlencode(values)
    req = urllib2.Request(url, url_data)
    response = urllib2.urlopen(req)
    soup = BeautifulSoup(response,from_encoding="utf-8")
    table_datas = soup.find_all("table", {'class' : 'hasBorder'})
    company = table_datas[0].td
    while(company):
        pdb.set_trace()
        company_list.append(company)
        compnay = company.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling

    for data in table_datas:
        pdb.set_trace()
        print data
    return HttpResponse(table_datas)

#income statement from TWSE 綜合損益表
def old_show_season_income_statement(request):
    stock_symbol = '2454'
    year = 102
    season = 1
    url = 'http://mops.twse.com.tw/mops/web/ajax_t164sb04'
    values = {'encodeURIComponent' : '1', 'step' : '1', 'firstin' : '1', 'off' : '1',
              'keyword4' : '','code1' : '','TYPEK2' : '','checkbtn' : '',
              'queryName':'co_id', 'TYPEK':'all', 'isnew':'false', 'co_id' : stock_symbol, 'year' : year, 'season' : str(season).zfill(2) }
    values = {'encodeURIComponent' : '1', 'id' : '', 'key' : '', 'TYPEK' : 'sii', 'step' : '2',
              'year' : year, 'season' : season, 'co_id' : stock_symbol, 'firstin' : '1'}
    url_data = urllib.urlencode(values)
    req = urllib2.Request(url, url_data)
    response = urllib2.urlopen(req)
    income_statement = SeasonIncomeStatement()
    soup = BeautifulSoup(response, from_encoding="utf-8")
    # print soup 詳細資料

    balance_sheet_datas = soup.find_all("td", {'style' : 'text-align:left;white-space:nowrap;'})
    for data in balance_sheet_datas:
        if r'基本每股盈餘' in data.string.encode('utf-8'):
            if income_statement.basic_earnings_per_share is None:
                print 'init is none'
            if data.next_sibling.next_sibling.string is not None:
                income_statement.basic_earnings_per_share = Decimal(data.next_sibling.next_sibling.string.strip().replace(',',''))
                print data.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.string
                if income_statement.basic_earnings_per_share is not None:
                    print Decimal(data.next_sibling.next_sibling.string.strip().replace(',',''))
    req = urllib2.Request(url, url_data)
    response = urllib2.urlopen(req)
    return HttpResponse(response.read())

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
    if 'year' in request.GET and  'season' in request.GET:
        year = int(request.GET['year'])
        season = int(request.GET['season'])
    else:
        return HttpResponse('please input year or season')
    seasonRevenues = SeasonRevenue.objects.filter(year=year, season=season)
    #stock_ids = StockId.objects.all()
    if season == 4:
        incomeStatementsSeason1 = SeasonIncomeStatement.objects.filter(year=year, season=1)
        incomeStatementsSeason2 = SeasonIncomeStatement.objects.filter(year=year, season=2)
        incomeStatementsSeason3 = SeasonIncomeStatement.objects.filter(year=year, season=3)
        lastYearIncomeStatementsSeason1 = SeasonIncomeStatement.objects.filter(year=year-1, season=1)
        lastYearIncomeStatementsSeason2 = SeasonIncomeStatement.objects.filter(year=year-1, season=2)
        lastYearIncomeStatementsSeason3 = SeasonIncomeStatement.objects.filter(year=year-1, season=3)
    for seasonRevenue in seasonRevenues:
        stock_symbol = seasonRevenue.symbol
        if not (SeasonIncomeStatement.objects.filter(symbol=stock_symbol, year=year, season=season) and SeasonIncomeStatement.objects.filter(symbol=stock_symbol, year=year-1, season=season)):
            url = 'http://mops.twse.com.tw/mops/web/ajax_t164sb04'
            values = {'encodeURIComponent' : '1', 'step' : '1', 'firstin' : '1', 'off' : '1',
            'keyword4' : '','code1' : '','TYPEK2' : '','checkbtn' : '',
            'queryName':'co_id', 'TYPEK':'all', 'isnew':'false', 'co_id' : stock_symbol, 'year' : year, 'season' : str(season).zfill(2) }
            values = {'encodeURIComponent' : '1', 'id' : '', 'key' : '', 'TYPEK' : 'sii', 'step' : '2',
                      'year' : str(year-1911), 'season' : str(season).zfill(2), 'co_id' : stock_symbol, 'firstin' : '1'}
            url_data = urllib.urlencode(values)
            req = urllib2.Request(url, url_data)
            response = urllib2.urlopen(req)
            soup = BeautifulSoup(response,from_encoding="utf-8")
            
            season_income_datas = soup.find_all("td", {'style' : 'text-align:left;white-space:nowrap;'})
            income_statement = SeasonIncomeStatement()
            income_statement.symbol = stock_symbol
            income_statement.year = year
            income_statement.season = season
            income_statement.surrogate_key = stock_symbol + '_' + str(year) + str(season).zfill(2)

            income_statement.date = season_to_date(year, season)

            last_year_income_statement = SeasonIncomeStatement()
            last_year_income_statement.symbol = stock_symbol
            last_year_income_statement.year = str(year-1)
            last_year_income_statement.season = season

            last_year_income_statement.date = season_to_date(year-1, season)
            
            last_year_income_statement.surrogate_key = stock_symbol + '_' + str(year-1) + str(season).zfill(2)

            owners_of_parent = 0
            print stock_symbol + ' loaded'
            symbolSeason1 = None
            symbolSeason2 = None
            symbolSeason3 = None
            lastYearSymbolSeason1 = None
            lastYearSymbolSeason2 = None
            lastYearSymbolSeason3 = None
            hasPrevSeasons = False
            hasLastYearPrevSeasons = False
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
                if lastYearIncomeStatementsSeason1:
                    if lastYearIncomeStatementsSeason1.filter(symbol=stock_symbol):
                        lastYearSymbolSeason1 = lastYearIncomeStatementsSeason1.get(symbol=stock_symbol)
                if lastYearIncomeStatementsSeason2:
                    if lastYearIncomeStatementsSeason2.filter(symbol=stock_symbol):
                        lastYearSymbolSeason2 = lastYearIncomeStatementsSeason2.get(symbol=stock_symbol)
                if lastYearIncomeStatementsSeason3:
                    if lastYearIncomeStatementsSeason3.filter(symbol=stock_symbol):
                        lastYearSymbolSeason3 = lastYearIncomeStatementsSeason3.get(symbol=stock_symbol)
                if symbolSeason1 and symbolSeason2 and symbolSeason3:
                    hasPrevSeasons = True
                if lastYearSymbolSeason1 and lastYearSymbolSeason2 and lastYearSymbolSeason3:
                    hasLastYearPrevSeasons = True
            else:
                hasPrevSeasons = False
                hasLastYearPrevSeasons = False

            for data in season_income_datas:
                if r'營業收入合計' in data.string.encode('utf-8') or r'收入合計' == data.string.encode('utf-8') or r'淨收益' == data.string.encode('utf-8') or r'收益合計' == data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    if not hasPrevSeasons:
                        income_statement.operating_revenue = st_to_decimal(next_data.string)
                    elif symbolSeason1.operating_revenue and symbolSeason2.operating_revenue and symbolSeason3.operating_revenue:
                        income_statement.operating_revenue = st_to_decimal(next_data.string) - symbolSeason1.operating_revenue - symbolSeason2.operating_revenue - symbolSeason3.operating_revenue
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    if not hasLastYearPrevSeasons:
                        last_year_income_statement.operating_revenue = st_to_decimal(next_data.string)
                    elif lastYearSymbolSeason1.operating_revenue and lastYearSymbolSeason2.operating_revenue and lastYearSymbolSeason3.operating_revenue:
                        last_year_income_statement.operating_revenue = st_to_decimal(next_data.string) - lastYearSymbolSeason1.operating_revenue - lastYearSymbolSeason2.operating_revenue - lastYearSymbolSeason3.operating_revenue
                elif r'營業成本合計' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    if not hasPrevSeasons:
                        income_statement.operating_cost = st_to_decimal(next_data.string)
                    elif symbolSeason1.operating_cost and symbolSeason2.operating_cost and symbolSeason3.operating_cost:
                        income_statement.operating_cost = st_to_decimal(next_data.string) - symbolSeason1.operating_cost - symbolSeason2.operating_cost - symbolSeason3.operating_cost
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    if not hasLastYearPrevSeasons:
                        last_year_income_statement.operating_cost = st_to_decimal(next_data.string)
                    elif lastYearSymbolSeason1.operating_cost and lastYearSymbolSeason2.operating_cost and lastYearSymbolSeason3.operating_cost:
                        last_year_income_statement.operating_cost = st_to_decimal(next_data.string) - lastYearSymbolSeason1.operating_cost - lastYearSymbolSeason2.operating_cost - lastYearSymbolSeason3.operating_cost
                elif r'營業毛利（毛損）' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    if not hasPrevSeasons:
                        income_statement.gross_profit_from_operations = st_to_decimal(next_data.string)
                    elif symbolSeason1.gross_profit_from_operations and symbolSeason2.gross_profit_from_operations and symbolSeason3.gross_profit_from_operations:
                        income_statement.gross_profit_from_operations = st_to_decimal(next_data.string) - symbolSeason1.gross_profit_from_operations - symbolSeason2.gross_profit_from_operations - symbolSeason3.gross_profit_from_operations
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    if not hasLastYearPrevSeasons:
                        last_year_income_statement.gross_profit_from_operations = st_to_decimal(next_data.string)
                    elif lastYearSymbolSeason1.gross_profit_from_operations and lastYearSymbolSeason2.gross_profit_from_operations and lastYearSymbolSeason3.gross_profit_from_operations:
                        last_year_income_statement.gross_profit_from_operations = st_to_decimal(next_data.string) - lastYearSymbolSeason1.gross_profit_from_operations - lastYearSymbolSeason2.gross_profit_from_operations - lastYearSymbolSeason3.gross_profit_from_operations
                elif r'推銷費用' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    if not hasPrevSeasons:
                        income_statement.selling_expenses = st_to_decimal(next_data.string)
                    elif symbolSeason1.selling_expenses and symbolSeason2.selling_expenses and symbolSeason3.selling_expenses:
                        income_statement.selling_expenses = st_to_decimal(next_data.string) - symbolSeason1.selling_expenses - symbolSeason2.selling_expenses - symbolSeason3.selling_expenses
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    if not hasLastYearPrevSeasons:
                        last_year_income_statement.selling_expenses = st_to_decimal(next_data.string)
                    elif lastYearSymbolSeason1.selling_expenses and lastYearSymbolSeason2.selling_expenses and lastYearSymbolSeason3.selling_expenses:
                        last_year_income_statement.selling_expenses = st_to_decimal(next_data.string) - lastYearSymbolSeason1.selling_expenses - lastYearSymbolSeason2.selling_expenses - lastYearSymbolSeason3.selling_expenses
                elif r'管理費用' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    if not hasPrevSeasons:
                        income_statement.administrative_expenses = st_to_decimal(next_data.string)
                    elif symbolSeason1.administrative_expenses and symbolSeason2.administrative_expenses and symbolSeason3.administrative_expenses:
                        income_statement.administrative_expenses = st_to_decimal(next_data.string) - symbolSeason1.administrative_expenses - symbolSeason2.administrative_expenses - symbolSeason3.administrative_expenses
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    if not hasLastYearPrevSeasons:
                        last_year_income_statement.administrative_expenses = st_to_decimal(next_data.string)
                    elif lastYearSymbolSeason1.administrative_expenses and lastYearSymbolSeason2.administrative_expenses and lastYearSymbolSeason3.administrative_expenses:
                        last_year_income_statement.administrative_expenses = st_to_decimal(next_data.string) - lastYearSymbolSeason1.administrative_expenses - lastYearSymbolSeason2.administrative_expenses - lastYearSymbolSeason3.administrative_expenses
                elif r'研究發展費用' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    if not hasPrevSeasons:
                        income_statement.research_and_development_expenses = st_to_decimal(next_data.string)
                    elif symbolSeason1.research_and_development_expenses and symbolSeason2.research_and_development_expenses and symbolSeason3.research_and_development_expenses:
                        income_statement.research_and_development_expenses = st_to_decimal(next_data.string) - symbolSeason1.research_and_development_expenses - symbolSeason2.research_and_development_expenses - symbolSeason3.research_and_development_expenses
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    if not hasLastYearPrevSeasons:
                        last_year_income_statement.research_and_development_expenses = st_to_decimal(next_data.string)
                    elif lastYearSymbolSeason1.research_and_development_expenses and lastYearSymbolSeason2.research_and_development_expenses and lastYearSymbolSeason3.research_and_development_expenses:
                        last_year_income_statement.research_and_development_expenses = st_to_decimal(next_data.string) - lastYearSymbolSeason1.research_and_development_expenses - lastYearSymbolSeason2.research_and_development_expenses - lastYearSymbolSeason3.research_and_development_expenses
                elif r'營業費用合計' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    if not hasPrevSeasons:
                        income_statement.operating_expenses = st_to_decimal(next_data.string)
                    elif symbolSeason1.operating_expenses and symbolSeason2.operating_expenses and symbolSeason3.operating_expenses:
                        income_statement.operating_expenses = st_to_decimal(next_data.string) - symbolSeason1.operating_expenses - symbolSeason2.operating_expenses - symbolSeason3.operating_expenses
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    if not hasLastYearPrevSeasons:
                        last_year_income_statement.operating_expenses = st_to_decimal(next_data.string)
                    elif lastYearSymbolSeason1.operating_expenses and lastYearSymbolSeason2.operating_expenses and lastYearSymbolSeason3.operating_expenses:
                        last_year_income_statement.operating_expenses = st_to_decimal(next_data.string) - lastYearSymbolSeason1.operating_expenses - lastYearSymbolSeason2.operating_expenses - lastYearSymbolSeason3.operating_expenses
                elif r'營業利益（損失）' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    if not hasPrevSeasons:
                        income_statement.net_operating_income = st_to_decimal(next_data.string)
                    elif symbolSeason1.net_operating_income and symbolSeason2.net_operating_income and symbolSeason3.net_operating_income:
                        income_statement.net_operating_income = st_to_decimal(next_data.string) - symbolSeason1.net_operating_income - symbolSeason2.net_operating_income - symbolSeason3.net_operating_income
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    if not hasLastYearPrevSeasons:
                        last_year_income_statement.net_operating_income = st_to_decimal(next_data.string)
                    elif lastYearSymbolSeason1.net_operating_income and lastYearSymbolSeason2.net_operating_income and lastYearSymbolSeason3.net_operating_income:
                        last_year_income_statement.net_operating_income = st_to_decimal(next_data.string) - lastYearSymbolSeason1.net_operating_income - lastYearSymbolSeason2.net_operating_income - lastYearSymbolSeason3.net_operating_income
                elif r'其他收入' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    if not hasPrevSeasons:
                        income_statement.net_operating_income = st_to_decimal(next_data.string)
                    elif symbolSeason1.net_operating_income and symbolSeason2.net_operating_income and symbolSeason3.net_operating_income:
                        income_statement.net_operating_income = st_to_decimal(next_data.string) - symbolSeason1.net_operating_income - symbolSeason2.net_operating_income - symbolSeason3.net_operating_income
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    if not hasLastYearPrevSeasons:
                        last_year_income_statement.net_operating_income = st_to_decimal(next_data.string)
                    elif lastYearSymbolSeason1.net_operating_income and lastYearSymbolSeason2.net_operating_income and lastYearSymbolSeason3.net_operating_income:
                        last_year_income_statement.net_operating_income = st_to_decimal(next_data.string) - lastYearSymbolSeason1.net_operating_income - lastYearSymbolSeason2.net_operating_income - lastYearSymbolSeason3.net_operating_income
                elif r'其他利益及損失淨額' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    if not hasPrevSeasons:
                        income_statement.other_gains_and_losses = st_to_decimal(next_data.string)
                    elif symbolSeason1.other_gains_and_losses and symbolSeason2.other_gains_and_losses and symbolSeason3.other_gains_and_losses:
                        income_statement.other_gains_and_losses = st_to_decimal(next_data.string) - symbolSeason1.other_gains_and_losses - symbolSeason2.other_gains_and_losses - symbolSeason3.other_gains_and_losses
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    if not hasLastYearPrevSeasons:
                        last_year_income_statement.other_gains_and_losses = st_to_decimal(next_data.string)
                    elif lastYearSymbolSeason1.other_gains_and_losses and lastYearSymbolSeason2.other_gains_and_losses and lastYearSymbolSeason3.other_gains_and_losses:
                        last_year_income_statement.other_gains_and_losses = st_to_decimal(next_data.string) - lastYearSymbolSeason1.other_gains_and_losses - lastYearSymbolSeason2.other_gains_and_losses - lastYearSymbolSeason3.other_gains_and_losses
                elif r'財務成本淨額' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    if not hasPrevSeasons:
                        income_statement.finance_costs = st_to_decimal(next_data.string)
                    elif symbolSeason1.finance_costs and symbolSeason2.finance_costs and symbolSeason3.finance_costs:
                        income_statement.finance_costs = st_to_decimal(next_data.string) - symbolSeason1.finance_costs - symbolSeason2.finance_costs - symbolSeason3.finance_costs
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    if not hasLastYearPrevSeasons:
                        last_year_income_statement.finance_costs = st_to_decimal(next_data.string)
                    elif lastYearSymbolSeason1.finance_costs and lastYearSymbolSeason2.finance_costs and lastYearSymbolSeason3.finance_costs:
                        last_year_income_statement.finance_costs = st_to_decimal(next_data.string) - lastYearSymbolSeason1.finance_costs - lastYearSymbolSeason2.finance_costs - lastYearSymbolSeason3.finance_costs
                elif r'營業外收入及支出合計' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    if not hasPrevSeasons:
                        income_statement.non_operating_income_and_expenses = st_to_decimal(next_data.string)
                    elif symbolSeason1.non_operating_income_and_expenses and symbolSeason2.non_operating_income_and_expenses and symbolSeason3.non_operating_income_and_expenses:
                        income_statement.non_operating_income_and_expenses = st_to_decimal(next_data.string) - symbolSeason1.non_operating_income_and_expenses - symbolSeason2.non_operating_income_and_expenses - symbolSeason3.non_operating_income_and_expenses
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    if not hasLastYearPrevSeasons:
                        last_year_income_statement.non_operating_income_and_expenses = st_to_decimal(next_data.string)
                    elif lastYearSymbolSeason1.non_operating_income_and_expenses and lastYearSymbolSeason2.non_operating_income_and_expenses and lastYearSymbolSeason3.non_operating_income_and_expenses:
                        last_year_income_statement.non_operating_income_and_expenses = st_to_decimal(next_data.string) - lastYearSymbolSeason1.non_operating_income_and_expenses - lastYearSymbolSeason2.non_operating_income_and_expenses - lastYearSymbolSeason3.non_operating_income_and_expenses
                elif r'稅前淨利（淨損）' in data.string.encode('utf-8') or r'繼續營業單位稅前淨利（淨損）' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    if not hasPrevSeasons:
                        income_statement.profit_from_continuing_operations_before_tax = st_to_decimal(next_data.string)
                    elif symbolSeason1.profit_from_continuing_operations_before_tax and symbolSeason2.profit_from_continuing_operations_before_tax and symbolSeason3.profit_from_continuing_operations_before_tax:
                        income_statement.profit_from_continuing_operations_before_tax = st_to_decimal(next_data.string) - symbolSeason1.profit_from_continuing_operations_before_tax - symbolSeason2.profit_from_continuing_operations_before_tax - symbolSeason3.profit_from_continuing_operations_before_tax
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    if not hasLastYearPrevSeasons:
                        last_year_income_statement.profit_from_continuing_operations_before_tax = st_to_decimal(next_data.string)
                    elif lastYearSymbolSeason1.profit_from_continuing_operations_before_tax and lastYearSymbolSeason2.profit_from_continuing_operations_before_tax and lastYearSymbolSeason3.profit_from_continuing_operations_before_tax:
                        last_year_income_statement.profit_from_continuing_operations_before_tax = st_to_decimal(next_data.string) - lastYearSymbolSeason1.profit_from_continuing_operations_before_tax - lastYearSymbolSeason2.profit_from_continuing_operations_before_tax - lastYearSymbolSeason3.profit_from_continuing_operations_before_tax
                elif r'所得稅費用（利益）合計' in data.string.encode('utf-8') or r'所得稅（費用）利益' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    if not hasPrevSeasons:
                        income_statement.tax_expense = st_to_decimal(next_data.string)
                    elif symbolSeason1.tax_expense and symbolSeason2.tax_expense and symbolSeason3.tax_expense:
                        income_statement.tax_expense = st_to_decimal(next_data.string) - symbolSeason1.tax_expense - symbolSeason2.tax_expense - symbolSeason3.tax_expense
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    if not hasLastYearPrevSeasons:
                        last_year_income_statement.tax_expense = st_to_decimal(next_data.string)
                    elif lastYearSymbolSeason1.tax_expense and lastYearSymbolSeason2.tax_expense and lastYearSymbolSeason3.tax_expense:
                        last_year_income_statement.tax_expense = st_to_decimal(next_data.string) - lastYearSymbolSeason1.tax_expense - lastYearSymbolSeason2.tax_expense - lastYearSymbolSeason3.tax_expense
                elif r'繼續營業單位本期淨利（淨損）' in data.string.encode('utf-8') or r'繼續營業單位本期稅後淨利（淨損）' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    if not hasPrevSeasons:
                        income_statement.profit_from_continuing_operations = st_to_decimal(next_data.string)
                    elif symbolSeason1.profit_from_continuing_operations and symbolSeason2.profit_from_continuing_operations and symbolSeason3.profit_from_continuing_operations:
                        income_statement.profit_from_continuing_operations = st_to_decimal(next_data.string) - symbolSeason1.profit_from_continuing_operations - symbolSeason2.profit_from_continuing_operations - symbolSeason3.profit_from_continuing_operations
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    if not hasLastYearPrevSeasons:
                        last_year_income_statement.profit_from_continuing_operations = st_to_decimal(next_data.string)
                    elif lastYearSymbolSeason1.profit_from_continuing_operations and lastYearSymbolSeason2.profit_from_continuing_operations and lastYearSymbolSeason3.profit_from_continuing_operations:
                        last_year_income_statement.profit_from_continuing_operations = st_to_decimal(next_data.string) - lastYearSymbolSeason1.profit_from_continuing_operations - lastYearSymbolSeason2.profit_from_continuing_operations - lastYearSymbolSeason3.profit_from_continuing_operations
                elif r'本期淨利（淨損）' in data.string.encode('utf-8') or r'本期稅後淨利（淨損）' in data.string.encode('utf-8'):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        if not hasPrevSeasons:
                            income_statement.profit = st_to_decimal(next_data.string)
                        elif symbolSeason1.profit and symbolSeason2.profit and symbolSeason3.profit:
                            income_statement.profit = st_to_decimal(next_data.string) - symbolSeason1.profit - symbolSeason2.profit - symbolSeason3.profit
                        next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                        if not hasLastYearPrevSeasons:
                            last_year_income_statement.profit = st_to_decimal(next_data.string)
                        elif lastYearSymbolSeason1.profit and lastYearSymbolSeason2.profit and lastYearSymbolSeason3.profit:
                            last_year_income_statement.profit = st_to_decimal(next_data.string) - lastYearSymbolSeason1.profit - lastYearSymbolSeason2.profit - lastYearSymbolSeason3.profit
                elif r'國外營運機構財務報表換算之兌換差額' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    if not hasPrevSeasons:
                        income_statement.exchange_differences_on_translation = st_to_decimal(next_data.string)
                    elif symbolSeason1.exchange_differences_on_translation and symbolSeason2.exchange_differences_on_translation and symbolSeason3.exchange_differences_on_translation:
                        income_statement.exchange_differences_on_translation = st_to_decimal(next_data.string) - symbolSeason1.exchange_differences_on_translation - symbolSeason2.exchange_differences_on_translation - symbolSeason3.exchange_differences_on_translation
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    if not hasLastYearPrevSeasons:
                        last_year_income_statement.exchange_differences_on_translation = st_to_decimal(next_data.string)
                    elif lastYearSymbolSeason1.exchange_differences_on_translation and lastYearSymbolSeason2.exchange_differences_on_translation and lastYearSymbolSeason3.exchange_differences_on_translation:
                        last_year_income_statement.exchange_differences_on_translation = st_to_decimal(next_data.string) - lastYearSymbolSeason1.exchange_differences_on_translation - lastYearSymbolSeason2.exchange_differences_on_translation - lastYearSymbolSeason3.exchange_differences_on_translation
                elif r'備供出售金融資產未實現評價損益' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    if not hasPrevSeasons:
                        income_statement.unrealised_gains_for_sale_financial_assets = st_to_decimal(next_data.string)
                    elif symbolSeason1.unrealised_gains_for_sale_financial_assets and symbolSeason2.unrealised_gains_for_sale_financial_assets and symbolSeason3.unrealised_gains_for_sale_financial_assets:
                        income_statement.unrealised_gains_for_sale_financial_assets = st_to_decimal(next_data.string) - symbolSeason1.unrealised_gains_for_sale_financial_assets - symbolSeason2.unrealised_gains_for_sale_financial_assets - symbolSeason3.unrealised_gains_for_sale_financial_assets
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    if not hasLastYearPrevSeasons:
                        last_year_income_statement.unrealised_gains_for_sale_financial_assets = st_to_decimal(next_data.string)
                    elif lastYearSymbolSeason1.unrealised_gains_for_sale_financial_assets and lastYearSymbolSeason2.unrealised_gains_for_sale_financial_assets and lastYearSymbolSeason3.unrealised_gains_for_sale_financial_assets:
                        last_year_income_statement.unrealised_gains_for_sale_financial_assets = st_to_decimal(next_data.string) - lastYearSymbolSeason1.unrealised_gains_for_sale_financial_assets - lastYearSymbolSeason2.unrealised_gains_for_sale_financial_assets - lastYearSymbolSeason3.unrealised_gains_for_sale_financial_assets
                elif r'與其他綜合損益組成部分相關之所得稅' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    if not hasPrevSeasons:
                        income_statement.income_tax_of_other_comprehensive_income = st_to_decimal(next_data.string)
                    elif symbolSeason1.income_tax_of_other_comprehensive_income and symbolSeason2.income_tax_of_other_comprehensive_income and symbolSeason3.income_tax_of_other_comprehensive_income:
                        income_statement.income_tax_of_other_comprehensive_income = st_to_decimal(next_data.string) - symbolSeason1.income_tax_of_other_comprehensive_income - symbolSeason2.income_tax_of_other_comprehensive_income - symbolSeason3.income_tax_of_other_comprehensive_income
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    if not hasLastYearPrevSeasons:
                        last_year_income_statement.income_tax_of_other_comprehensive_income = st_to_decimal(next_data.string)
                    elif lastYearSymbolSeason1.income_tax_of_other_comprehensive_income and lastYearSymbolSeason2.income_tax_of_other_comprehensive_income and lastYearSymbolSeason3.income_tax_of_other_comprehensive_income:
                        last_year_income_statement.income_tax_of_other_comprehensive_income = st_to_decimal(next_data.string) - lastYearSymbolSeason1.income_tax_of_other_comprehensive_income - lastYearSymbolSeason2.income_tax_of_other_comprehensive_income - lastYearSymbolSeason3.income_tax_of_other_comprehensive_income
                elif r'其他綜合損益（淨額）' in data.string.encode('utf-8') or r'其他綜合損益（稅後）淨額' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    if not hasPrevSeasons:
                        income_statement.other_comprehensive_income = st_to_decimal(next_data.string)
                    elif symbolSeason1.other_comprehensive_income and symbolSeason2.other_comprehensive_income and symbolSeason3.other_comprehensive_income:
                        income_statement.other_comprehensive_income = st_to_decimal(next_data.string) - symbolSeason1.other_comprehensive_income - symbolSeason2.other_comprehensive_income - symbolSeason3.other_comprehensive_income
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    if not hasLastYearPrevSeasons:
                        last_year_income_statement.other_comprehensive_income = st_to_decimal(next_data.string)
                    elif lastYearSymbolSeason1.other_comprehensive_income and lastYearSymbolSeason2.other_comprehensive_income and lastYearSymbolSeason3.other_comprehensive_income:
                        last_year_income_statement.other_comprehensive_income = st_to_decimal(next_data.string) - lastYearSymbolSeason1.other_comprehensive_income - lastYearSymbolSeason2.other_comprehensive_income - lastYearSymbolSeason3.other_comprehensive_income
                elif r'本期綜合損益總額' in data.string.encode('utf-8') or r'本期綜合損益總額（稅後）' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    if not hasPrevSeasons:
                        income_statement.total_comprehensive_income = st_to_decimal(next_data.string)
                    elif symbolSeason1.total_comprehensive_income and symbolSeason2.total_comprehensive_income and symbolSeason3.total_comprehensive_income:
                        income_statement.total_comprehensive_income = st_to_decimal(next_data.string) - symbolSeason1.total_comprehensive_income - symbolSeason2.total_comprehensive_income - symbolSeason3.total_comprehensive_income
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    if not hasLastYearPrevSeasons:
                        last_year_income_statement.total_comprehensive_income = st_to_decimal(next_data.string)
                    elif lastYearSymbolSeason1.total_comprehensive_income and lastYearSymbolSeason2.total_comprehensive_income and lastYearSymbolSeason3.total_comprehensive_income:
                        last_year_income_statement.total_comprehensive_income = st_to_decimal(next_data.string) - lastYearSymbolSeason1.total_comprehensive_income - lastYearSymbolSeason2.total_comprehensive_income - lastYearSymbolSeason3.total_comprehensive_income
                elif r'母公司業主（淨利／損）' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    if not hasPrevSeasons:
                        income_statement.profit_to_owners_of_parent = st_to_decimal(next_data.string)
                    elif symbolSeason1.profit_to_owners_of_parent and symbolSeason2.profit_to_owners_of_parent and symbolSeason3.profit_to_owners_of_parent:
                        income_statement.profit_to_owners_of_parent = st_to_decimal(next_data.string) - symbolSeason1.profit_to_owners_of_parent - symbolSeason2.profit_to_owners_of_parent - symbolSeason3.profit_to_owners_of_parent
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    if not hasLastYearPrevSeasons:
                        last_year_income_statement.profit_to_owners_of_parent = st_to_decimal(next_data.string)
                    elif lastYearSymbolSeason1.profit_to_owners_of_parent and lastYearSymbolSeason2.profit_to_owners_of_parent and lastYearSymbolSeason3.profit_to_owners_of_parent:
                        last_year_income_statement.profit_to_owners_of_parent = st_to_decimal(next_data.string) - lastYearSymbolSeason1.profit_to_owners_of_parent - lastYearSymbolSeason2.profit_to_owners_of_parent - lastYearSymbolSeason3.profit_to_owners_of_parent
                elif r'非控制權益（淨利／損）' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    if not hasPrevSeasons:
                        income_statement.profit_to_non_controlling_interests = st_to_decimal(next_data.string)
                    elif symbolSeason1.profit_to_non_controlling_interests and symbolSeason2.profit_to_non_controlling_interests and symbolSeason3.profit_to_non_controlling_interests:
                        income_statement.profit_to_non_controlling_interests = st_to_decimal(next_data.string) - symbolSeason1.profit_to_non_controlling_interests - symbolSeason2.profit_to_non_controlling_interests - symbolSeason3.profit_to_non_controlling_interests
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    if not hasLastYearPrevSeasons:
                        last_year_income_statement.profit_to_non_controlling_interests = st_to_decimal(next_data.string)
                    elif lastYearSymbolSeason1.profit_to_non_controlling_interests and lastYearSymbolSeason2.profit_to_non_controlling_interests and lastYearSymbolSeason3.profit_to_non_controlling_interests:
                        last_year_income_statement.profit_to_non_controlling_interests = st_to_decimal(next_data.string) - lastYearSymbolSeason1.profit_to_non_controlling_interests - lastYearSymbolSeason2.profit_to_non_controlling_interests - lastYearSymbolSeason3.profit_to_non_controlling_interests
                elif r'母公司業主（綜合損益）' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    if not hasPrevSeasons:
                        income_statement.comprehensive_income_to_owners_of_parent = st_to_decimal(next_data.string)
                    elif symbolSeason1.comprehensive_income_to_owners_of_parent and symbolSeason2.comprehensive_income_to_owners_of_parent and symbolSeason3.comprehensive_income_to_owners_of_parent:
                        income_statement.comprehensive_income_to_owners_of_parent = st_to_decimal(next_data.string) - symbolSeason1.comprehensive_income_to_owners_of_parent - symbolSeason2.comprehensive_income_to_owners_of_parent - symbolSeason3.comprehensive_income_to_owners_of_parent
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    if not hasLastYearPrevSeasons:
                        last_year_income_statement.comprehensive_income_to_owners_of_parent = st_to_decimal(next_data.string)
                    elif lastYearSymbolSeason1.comprehensive_income_to_owners_of_parent and lastYearSymbolSeason2.comprehensive_income_to_owners_of_parent and lastYearSymbolSeason3.comprehensive_income_to_owners_of_parent:
                        last_year_income_statement.comprehensive_income_to_owners_of_parent = st_to_decimal(next_data.string) - lastYearSymbolSeason1.comprehensive_income_to_owners_of_parent - lastYearSymbolSeason2.comprehensive_income_to_owners_of_parent - lastYearSymbolSeason3.comprehensive_income_to_owners_of_parent
                elif r'母公司業主' in data.string.encode('utf-8'):
                    if owners_of_parent == 0:
                        next_data = data.next_sibling.next_sibling
                        if not hasPrevSeasons:
                            income_statement.profit_to_owners_of_parent = st_to_decimal(next_data.string)
                        elif symbolSeason1.profit_to_owners_of_parent and symbolSeason2.profit_to_owners_of_parent and symbolSeason3.profit_to_owners_of_parent:
                            income_statement.profit_to_owners_of_parent = st_to_decimal(next_data.string) - symbolSeason1.profit_to_owners_of_parent - symbolSeason2.profit_to_owners_of_parent - symbolSeason3.profit_to_owners_of_parent
                        next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                        if not hasLastYearPrevSeasons:
                            last_year_income_statement.profit_to_owners_of_parent = st_to_decimal(next_data.string)
                        elif lastYearSymbolSeason1.profit_to_owners_of_parent and lastYearSymbolSeason2.profit_to_owners_of_parent and lastYearSymbolSeason3.profit_to_owners_of_parent:
                            last_year_income_statement.profit_to_owners_of_parent = st_to_decimal(next_data.string) - lastYearSymbolSeason1.profit_to_owners_of_parent - lastYearSymbolSeason2.profit_to_owners_of_parent - lastYearSymbolSeason3.profit_to_owners_of_parent
                        owners_of_parent = 1
                    else:
                        next_data = data.next_sibling.next_sibling
                        if not hasPrevSeasons:
                            income_statement.comprehensive_income_to_owners_of_parent = st_to_decimal(next_data.string)
                        elif symbolSeason1.comprehensive_income_to_owners_of_parent and symbolSeason2.comprehensive_income_to_owners_of_parent and symbolSeason3.comprehensive_income_to_owners_of_parent:
                            income_statement.comprehensive_income_to_owners_of_parent = st_to_decimal(next_data.string) - symbolSeason1.comprehensive_income_to_owners_of_parent - symbolSeason2.comprehensive_income_to_owners_of_parent - symbolSeason3.comprehensive_income_to_owners_of_parent
                        next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                        if not hasLastYearPrevSeasons:
                            last_year_income_statement.comprehensive_income_to_owners_of_parent = st_to_decimal(next_data.string)
                        elif lastYearSymbolSeason1.comprehensive_income_to_owners_of_parent and lastYearSymbolSeason2.comprehensive_income_to_owners_of_parent and lastYearSymbolSeason3.comprehensive_income_to_owners_of_parent:
                            last_year_income_statement.comprehensive_income_to_owners_of_parent = st_to_decimal(next_data.string) - lastYearSymbolSeason1.comprehensive_income_to_owners_of_parent - lastYearSymbolSeason2.comprehensive_income_to_owners_of_parent - lastYearSymbolSeason3.comprehensive_income_to_owners_of_parent
                elif r'非控制權益（綜合損益）' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    if not hasPrevSeasons:
                        income_statement.comprehensive_income_to_non_controlling_interests = st_to_decimal(next_data.string)
                    elif symbolSeason1.comprehensive_income_to_non_controlling_interests and symbolSeason2.comprehensive_income_to_non_controlling_interests and symbolSeason3.comprehensive_income_to_non_controlling_interests:
                        income_statement.comprehensive_income_to_non_controlling_interests = st_to_decimal(next_data.string) - symbolSeason1.comprehensive_income_to_non_controlling_interests - symbolSeason2.comprehensive_income_to_non_controlling_interests - symbolSeason3.comprehensive_income_to_non_controlling_interests
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    if not hasLastYearPrevSeasons:
                        last_year_income_statement.comprehensive_income_to_non_controlling_interests = st_to_decimal(next_data.string)
                    elif lastYearSymbolSeason1.comprehensive_income_to_non_controlling_interests and lastYearSymbolSeason2.comprehensive_income_to_non_controlling_interests and lastYearSymbolSeason3.comprehensive_income_to_non_controlling_interests:
                        last_year_income_statement.comprehensive_income_to_non_controlling_interests = st_to_decimal(next_data.string) - lastYearSymbolSeason1.comprehensive_income_to_non_controlling_interests - lastYearSymbolSeason2.comprehensive_income_to_non_controlling_interests - lastYearSymbolSeason3.comprehensive_income_to_non_controlling_interests
                elif r'基本每股盈餘' in data.string.encode('utf-8'):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        if not hasPrevSeasons:
                            income_statement.basic_earnings_per_share = st_to_decimal(next_data.string)
                        elif symbolSeason1.basic_earnings_per_share and symbolSeason2.basic_earnings_per_share and symbolSeason3.basic_earnings_per_share:
                            income_statement.basic_earnings_per_share = st_to_decimal(next_data.string) - symbolSeason1.basic_earnings_per_share - symbolSeason2.basic_earnings_per_share - symbolSeason3.basic_earnings_per_share
                        next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                        if not hasLastYearPrevSeasons:
                            last_year_income_statement.basic_earnings_per_share = st_to_decimal(next_data.string)
                        elif lastYearSymbolSeason1.basic_earnings_per_share and lastYearSymbolSeason2.basic_earnings_per_share and lastYearSymbolSeason3.basic_earnings_per_share:
                            last_year_income_statement.basic_earnings_per_share = st_to_decimal(next_data.string) - lastYearSymbolSeason1.basic_earnings_per_share - lastYearSymbolSeason2.basic_earnings_per_share - lastYearSymbolSeason3.basic_earnings_per_share
                elif r'稀釋每股盈餘' in data.string.encode('utf-8'):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        if not hasPrevSeasons:
                            income_statement.diluted_earnings_per_share = st_to_decimal(next_data.string)
                        elif symbolSeason1.diluted_earnings_per_share and symbolSeason2.diluted_earnings_per_share and symbolSeason3.diluted_earnings_per_share:
                            income_statement.diluted_earnings_per_share = st_to_decimal(next_data.string) - symbolSeason1.diluted_earnings_per_share - symbolSeason2.diluted_earnings_per_share - symbolSeason3.diluted_earnings_per_share
                        next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                        if not hasLastYearPrevSeasons:
                            last_year_income_statement.diluted_earnings_per_share = st_to_decimal(next_data.string)
                        elif lastYearSymbolSeason1.diluted_earnings_per_share and lastYearSymbolSeason2.diluted_earnings_per_share and lastYearSymbolSeason3.diluted_earnings_per_share:
                            last_year_income_statement.diluted_earnings_per_share = st_to_decimal(next_data.string) - lastYearSymbolSeason1.diluted_earnings_per_share - lastYearSymbolSeason2.diluted_earnings_per_share - lastYearSymbolSeason3.diluted_earnings_per_share
                elif r'利息收入' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    if not hasPrevSeasons:
                        income_statement.interest_income = st_to_decimal(next_data.string)
                    elif symbolSeason1.interest_income and symbolSeason2.interest_income and symbolSeason3.interest_income:
                        income_statement.interest_income = st_to_decimal(next_data.string) - symbolSeason1.interest_income - symbolSeason2.interest_income - symbolSeason3.interest_income
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    if not hasLastYearPrevSeasons:
                        last_year_income_statement.interest_income = st_to_decimal(next_data.string)
                    elif lastYearSymbolSeason1.interest_income and lastYearSymbolSeason2.interest_income and lastYearSymbolSeason3.interest_income:
                        last_year_income_statement.interest_income = st_to_decimal(next_data.string) - lastYearSymbolSeason1.interest_income - lastYearSymbolSeason2.interest_income - lastYearSymbolSeason3.interest_income
                elif r'減：利息費用' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    if not hasPrevSeasons:
                        income_statement.interest_expenses = st_to_decimal(next_data.string)
                    elif symbolSeason1.interest_expenses and symbolSeason2.interest_expenses and symbolSeason3.interest_expenses:
                        income_statement.interest_expenses = st_to_decimal(next_data.string) - symbolSeason1.interest_expenses - symbolSeason2.interest_expenses - symbolSeason3.interest_expenses
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    if not hasLastYearPrevSeasons:
                        last_year_income_statement.interest_expenses = st_to_decimal(next_data.string)
                    elif lastYearSymbolSeason1.interest_expenses and lastYearSymbolSeason2.interest_expenses and lastYearSymbolSeason3.interest_expenses:
                        last_year_income_statement.interest_expenses = st_to_decimal(next_data.string) - lastYearSymbolSeason1.interest_expenses - lastYearSymbolSeason2.interest_expenses - lastYearSymbolSeason3.interest_expenses
                elif r'利息淨收益' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    if not hasPrevSeasons:
                        income_statement.net_income_of_interest = st_to_decimal(next_data.string)
                    elif symbolSeason1.net_income_of_interest and symbolSeason2.net_income_of_interest and symbolSeason3.net_income_of_interest:
                        income_statement.net_income_of_interest = st_to_decimal(next_data.string) - symbolSeason1.net_income_of_interest - symbolSeason2.net_income_of_interest - symbolSeason3.net_income_of_interest
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    if not hasLastYearPrevSeasons:
                        last_year_income_statement.net_income_of_interest = st_to_decimal(next_data.string)
                    elif lastYearSymbolSeason1.net_income_of_interest and lastYearSymbolSeason2.net_income_of_interest and lastYearSymbolSeason3.net_income_of_interest:
                        last_year_income_statement.net_income_of_interest = st_to_decimal(next_data.string) - lastYearSymbolSeason1.net_income_of_interest - lastYearSymbolSeason2.net_income_of_interest - lastYearSymbolSeason3.net_income_of_interest
                elif r'手續費淨收益' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    if not hasPrevSeasons:
                        income_statement.net_service_fee_income = st_to_decimal(next_data.string)
                    elif symbolSeason1.net_service_fee_income and symbolSeason2.net_service_fee_income and symbolSeason3.net_service_fee_income:
                        income_statement.net_service_fee_income = st_to_decimal(next_data.string) - symbolSeason1.net_service_fee_income - symbolSeason2.net_service_fee_income - symbolSeason3.net_service_fee_income
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    if not hasLastYearPrevSeasons:
                        last_year_income_statement.net_service_fee_income = st_to_decimal(next_data.string)
                    elif lastYearSymbolSeason1.net_service_fee_income and lastYearSymbolSeason2.net_service_fee_income and lastYearSymbolSeason3.net_service_fee_income:
                        last_year_income_statement.net_service_fee_income = st_to_decimal(next_data.string) - lastYearSymbolSeason1.net_service_fee_income - lastYearSymbolSeason2.net_service_fee_income - lastYearSymbolSeason3.net_service_fee_income
                elif r'透過損益按公允價值衡量之金融資產及負債損益' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    if not hasPrevSeasons:
                        income_statement.gain_on_financial_assets_or_liabilities_measured = st_to_decimal(next_data.string)
                    elif symbolSeason1.gain_on_financial_assets_or_liabilities_measured and symbolSeason2.gain_on_financial_assets_or_liabilities_measured and symbolSeason3.gain_on_financial_assets_or_liabilities_measured:
                        income_statement.gain_on_financial_assets_or_liabilities_measured = st_to_decimal(next_data.string) - symbolSeason1.gain_on_financial_assets_or_liabilities_measured - symbolSeason2.gain_on_financial_assets_or_liabilities_measured - symbolSeason3.gain_on_financial_assets_or_liabilities_measured
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    if not hasLastYearPrevSeasons:
                        last_year_income_statement.gain_on_financial_assets_or_liabilities_measured = st_to_decimal(next_data.string)
                    elif lastYearSymbolSeason1.gain_on_financial_assets_or_liabilities_measured and lastYearSymbolSeason2.gain_on_financial_assets_or_liabilities_measured and lastYearSymbolSeason3.gain_on_financial_assets_or_liabilities_measured:
                        last_year_income_statement.gain_on_financial_assets_or_liabilities_measured = st_to_decimal(next_data.string) - lastYearSymbolSeason1.gain_on_financial_assets_or_liabilities_measured - lastYearSymbolSeason2.gain_on_financial_assets_or_liabilities_measured - lastYearSymbolSeason3.gain_on_financial_assets_or_liabilities_measured
                elif r'備供出售金融資產之已實現損益' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    if not hasPrevSeasons:
                        income_statement.realized_gains_for_sale_financial_assets = st_to_decimal(next_data.string)
                    elif symbolSeason1.realized_gains_for_sale_financial_assets and symbolSeason2.realized_gains_for_sale_financial_assets and symbolSeason3.realized_gains_for_sale_financial_assets:
                        income_statement.realized_gains_for_sale_financial_assets = st_to_decimal(next_data.string) - symbolSeason1.realized_gains_for_sale_financial_assets - symbolSeason2.realized_gains_for_sale_financial_assets - symbolSeason3.realized_gains_for_sale_financial_assets
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    if not hasLastYearPrevSeasons:
                        last_year_income_statement.realized_gains_for_sale_financial_assets = st_to_decimal(next_data.string)
                    elif lastYearSymbolSeason1.realized_gains_for_sale_financial_assets and lastYearSymbolSeason2.realized_gains_for_sale_financial_assets and lastYearSymbolSeason3.realized_gains_for_sale_financial_assets:
                        last_year_income_statement.realized_gains_for_sale_financial_assets = st_to_decimal(next_data.string) - lastYearSymbolSeason1.realized_gains_for_sale_financial_assets - lastYearSymbolSeason2.realized_gains_for_sale_financial_assets - lastYearSymbolSeason3.realized_gains_for_sale_financial_assets
                elif r'持有至到期日金融資產之已實現損益' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    if not hasPrevSeasons:
                        income_statement.realized_gains_on_held_to_maturity_financial_assets = st_to_decimal(next_data.string)
                    elif symbolSeason1.realized_gains_on_held_to_maturity_financial_assets and symbolSeason2.realized_gains_on_held_to_maturity_financial_assets and symbolSeason3.realized_gains_on_held_to_maturity_financial_assets:
                        income_statement.realized_gains_on_held_to_maturity_financial_assets = st_to_decimal(next_data.string) - symbolSeason1.realized_gains_on_held_to_maturity_financial_assets - symbolSeason2.realized_gains_on_held_to_maturity_financial_assets - symbolSeason3.realized_gains_on_held_to_maturity_financial_assets
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    if not hasLastYearPrevSeasons:
                        last_year_income_statement.realized_gains_on_held_to_maturity_financial_assets = st_to_decimal(next_data.string)
                    elif lastYearSymbolSeason1.realized_gains_on_held_to_maturity_financial_assets and lastYearSymbolSeason2.realized_gains_on_held_to_maturity_financial_assets and lastYearSymbolSeason3.realized_gains_on_held_to_maturity_financial_assets:
                        last_year_income_statement.realized_gains_on_held_to_maturity_financial_assets = st_to_decimal(next_data.string) - lastYearSymbolSeason1.realized_gains_on_held_to_maturity_financial_assets - lastYearSymbolSeason2.realized_gains_on_held_to_maturity_financial_assets - lastYearSymbolSeason3.realized_gains_on_held_to_maturity_financial_assets
                elif r'兌換損益' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    if not hasPrevSeasons:
                        income_statement.foreign_exchange_gain = st_to_decimal(next_data.string)
                    elif symbolSeason1.foreign_exchange_gain and symbolSeason2.foreign_exchange_gain and symbolSeason3.foreign_exchange_gain:
                        income_statement.foreign_exchange_gain = st_to_decimal(next_data.string) - symbolSeason1.foreign_exchange_gain - symbolSeason2.foreign_exchange_gain - symbolSeason3.foreign_exchange_gain
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    if not hasLastYearPrevSeasons:
                        last_year_income_statement.foreign_exchange_gain = st_to_decimal(next_data.string)
                    elif lastYearSymbolSeason1.foreign_exchange_gain and lastYearSymbolSeason2.foreign_exchange_gain and lastYearSymbolSeason3.foreign_exchange_gain:
                        last_year_income_statement.foreign_exchange_gain = st_to_decimal(next_data.string) - lastYearSymbolSeason1.foreign_exchange_gain - lastYearSymbolSeason2.foreign_exchange_gain - lastYearSymbolSeason3.foreign_exchange_gain
                elif r'資產減損（損失）迴轉利益淨額' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    if not hasPrevSeasons:
                        income_statement.reversal_of_impairment_loss_on_assets = st_to_decimal(next_data.string)
                    elif symbolSeason1.reversal_of_impairment_loss_on_assets and symbolSeason2.reversal_of_impairment_loss_on_assets and symbolSeason3.reversal_of_impairment_loss_on_assets:
                        income_statement.reversal_of_impairment_loss_on_assets = st_to_decimal(next_data.string) - symbolSeason1.reversal_of_impairment_loss_on_assets - symbolSeason2.reversal_of_impairment_loss_on_assets - symbolSeason3.reversal_of_impairment_loss_on_assets
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    if not hasLastYearPrevSeasons:
                        last_year_income_statement.reversal_of_impairment_loss_on_assets = st_to_decimal(next_data.string)
                    elif lastYearSymbolSeason1.reversal_of_impairment_loss_on_assets and lastYearSymbolSeason2.reversal_of_impairment_loss_on_assets and lastYearSymbolSeason3.reversal_of_impairment_loss_on_assets:
                        last_year_income_statement.reversal_of_impairment_loss_on_assets = st_to_decimal(next_data.string) - lastYearSymbolSeason1.reversal_of_impairment_loss_on_assets - lastYearSymbolSeason2.reversal_of_impairment_loss_on_assets - lastYearSymbolSeason3.reversal_of_impairment_loss_on_assets
                elif r'採用權益法認列之關聯企業及合資損益之份額' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    if not hasPrevSeasons:
                        income_statement.gain_on_disposal_of_investments_accounted = st_to_decimal(next_data.string)
                    elif symbolSeason1.gain_on_disposal_of_investments_accounted and symbolSeason2.gain_on_disposal_of_investments_accounted and symbolSeason3.gain_on_disposal_of_investments_accounted:
                        income_statement.gain_on_disposal_of_investments_accounted = st_to_decimal(next_data.string) - symbolSeason1.gain_on_disposal_of_investments_accounted - symbolSeason2.gain_on_disposal_of_investments_accounted - symbolSeason3.gain_on_disposal_of_investments_accounted
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    if not hasLastYearPrevSeasons:
                        last_year_income_statement.gain_on_disposal_of_investments_accounted = st_to_decimal(next_data.string)
                    elif lastYearSymbolSeason1.gain_on_disposal_of_investments_accounted and lastYearSymbolSeason2.gain_on_disposal_of_investments_accounted and lastYearSymbolSeason3.gain_on_disposal_of_investments_accounted:
                        last_year_income_statement.gain_on_disposal_of_investments_accounted = st_to_decimal(next_data.string) - lastYearSymbolSeason1.gain_on_disposal_of_investments_accounted - lastYearSymbolSeason2.gain_on_disposal_of_investments_accounted - lastYearSymbolSeason3.gain_on_disposal_of_investments_accounted
                elif r'其他利息以外淨損益' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    if not hasPrevSeasons:
                        income_statement.net_other_non_interest_income = st_to_decimal(next_data.string)
                    elif symbolSeason1.net_other_non_interest_income and symbolSeason2.net_other_non_interest_income and symbolSeason3.net_other_non_interest_income:
                        income_statement.net_other_non_interest_income = st_to_decimal(next_data.string) - symbolSeason1.net_other_non_interest_income - symbolSeason2.net_other_non_interest_income - symbolSeason3.net_other_non_interest_income
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    if not hasLastYearPrevSeasons:
                        last_year_income_statement.net_other_non_interest_income = st_to_decimal(next_data.string)
                    elif lastYearSymbolSeason1.net_other_non_interest_income and lastYearSymbolSeason2.net_other_non_interest_income and lastYearSymbolSeason3.net_other_non_interest_income:
                        last_year_income_statement.net_other_non_interest_income = st_to_decimal(next_data.string) - lastYearSymbolSeason1.net_other_non_interest_income - lastYearSymbolSeason2.net_other_non_interest_income - lastYearSymbolSeason3.net_other_non_interest_income
                elif r'利息以外淨損益' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    if not hasPrevSeasons:
                        income_statement.net_non_interest_income = st_to_decimal(next_data.string)
                    elif symbolSeason1.net_non_interest_income and symbolSeason2.net_non_interest_income and symbolSeason3.net_non_interest_income:
                        income_statement.net_non_interest_income = st_to_decimal(next_data.string) - symbolSeason1.net_non_interest_income - symbolSeason2.net_non_interest_income - symbolSeason3.net_non_interest_income
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    if not hasLastYearPrevSeasons:
                        last_year_income_statement.net_non_interest_income = st_to_decimal(next_data.string)
                    elif lastYearSymbolSeason1.net_non_interest_income and lastYearSymbolSeason2.net_non_interest_income and lastYearSymbolSeason3.net_non_interest_income:
                        last_year_income_statement.net_non_interest_income = st_to_decimal(next_data.string) - lastYearSymbolSeason1.net_non_interest_income - lastYearSymbolSeason2.net_non_interest_income - lastYearSymbolSeason3.net_non_interest_income
                elif r'淨收益' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    if not hasPrevSeasons:
                        income_statement.net_income = st_to_decimal(next_data.string)
                    elif symbolSeason1.net_income and symbolSeason2.net_income and symbolSeason3.net_income:
                        income_statement.net_income = st_to_decimal(next_data.string) - symbolSeason1.net_income - symbolSeason2.net_income - symbolSeason3.net_income
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    if not hasLastYearPrevSeasons:
                        last_year_income_statement.net_income = st_to_decimal(next_data.string)
                    elif lastYearSymbolSeason1.net_income and lastYearSymbolSeason2.net_income and lastYearSymbolSeason3.net_income:
                        last_year_income_statement.net_income = st_to_decimal(next_data.string) - lastYearSymbolSeason1.net_income - lastYearSymbolSeason2.net_income - lastYearSymbolSeason3.net_income
                elif r'呆帳費用及保證責任準備提存（各項提存）' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    if not hasPrevSeasons:
                        income_statement.total_bad_debts_expense = st_to_decimal(next_data.string)
                    elif symbolSeason1.total_bad_debts_expense and symbolSeason2.total_bad_debts_expense and symbolSeason3.total_bad_debts_expense:
                        income_statement.total_bad_debts_expense = st_to_decimal(next_data.string) - symbolSeason1.total_bad_debts_expense - symbolSeason2.total_bad_debts_expense - symbolSeason3.total_bad_debts_expense
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    if not hasLastYearPrevSeasons:
                        last_year_income_statement.total_bad_debts_expense = st_to_decimal(next_data.string)
                    elif lastYearSymbolSeason1.total_bad_debts_expense and lastYearSymbolSeason2.total_bad_debts_expense and lastYearSymbolSeason3.total_bad_debts_expense:
                        last_year_income_statement.total_bad_debts_expense = st_to_decimal(next_data.string) - lastYearSymbolSeason1.total_bad_debts_expense - lastYearSymbolSeason2.total_bad_debts_expense - lastYearSymbolSeason3.total_bad_debts_expense
                elif r'員工福利費用' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    if not hasPrevSeasons:
                        income_statement.employee_benefits_expenses = st_to_decimal(next_data.string)
                    elif symbolSeason1.employee_benefits_expenses and symbolSeason2.employee_benefits_expenses and symbolSeason3.employee_benefits_expenses:
                        income_statement.employee_benefits_expenses = st_to_decimal(next_data.string) - symbolSeason1.employee_benefits_expenses - symbolSeason2.employee_benefits_expenses - symbolSeason3.employee_benefits_expenses
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    if not hasLastYearPrevSeasons:
                        last_year_income_statement.employee_benefits_expenses = st_to_decimal(next_data.string)
                    elif lastYearSymbolSeason1.employee_benefits_expenses and lastYearSymbolSeason2.employee_benefits_expenses and lastYearSymbolSeason3.employee_benefits_expenses:
                        last_year_income_statement.employee_benefits_expenses = st_to_decimal(next_data.string) - lastYearSymbolSeason1.employee_benefits_expenses - lastYearSymbolSeason2.employee_benefits_expenses - lastYearSymbolSeason3.employee_benefits_expenses
                elif r'折舊及攤銷費用' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    if not hasPrevSeasons:
                        income_statement.depreciation_and_amortization_expense = st_to_decimal(next_data.string)
                    elif symbolSeason1.depreciation_and_amortization_expense and symbolSeason2.depreciation_and_amortization_expense and symbolSeason3.depreciation_and_amortization_expense:
                        income_statement.depreciation_and_amortization_expense = st_to_decimal(next_data.string) - symbolSeason1.depreciation_and_amortization_expense - symbolSeason2.depreciation_and_amortization_expense - symbolSeason3.depreciation_and_amortization_expense
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    if not hasLastYearPrevSeasons:
                        last_year_income_statement.depreciation_and_amortization_expense = st_to_decimal(next_data.string)
                    elif lastYearSymbolSeason1.depreciation_and_amortization_expense and lastYearSymbolSeason2.depreciation_and_amortization_expense and lastYearSymbolSeason3.depreciation_and_amortization_expense:
                        last_year_income_statement.depreciation_and_amortization_expense = st_to_decimal(next_data.string) - lastYearSymbolSeason1.depreciation_and_amortization_expense - lastYearSymbolSeason2.depreciation_and_amortization_expense - lastYearSymbolSeason3.depreciation_and_amortization_expense
                elif r'停業單位損益' in data.string.encode('utf-8') or r'停業單位損益合計' in data.string.encode('utf-8'):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        if not hasPrevSeasons:
                            income_statement.income_from_discontinued_operations = st_to_decimal(next_data.string)
                        elif symbolSeason1.income_from_discontinued_operations and symbolSeason2.income_from_discontinued_operations and symbolSeason3.income_from_discontinued_operations:
                            income_statement.income_from_discontinued_operations = st_to_decimal(next_data.string) - symbolSeason1.income_from_discontinued_operations - symbolSeason2.income_from_discontinued_operations - symbolSeason3.income_from_discontinued_operations
                        next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                        if not hasLastYearPrevSeasons:
                            last_year_income_statement.income_from_discontinued_operations = st_to_decimal(next_data.string)
                        elif lastYearSymbolSeason1.income_from_discontinued_operations and lastYearSymbolSeason2.income_from_discontinued_operations and lastYearSymbolSeason3.income_from_discontinued_operations:
                            last_year_income_statement.income_from_discontinued_operations = st_to_decimal(next_data.string) - lastYearSymbolSeason1.income_from_discontinued_operations - lastYearSymbolSeason2.income_from_discontinued_operations - lastYearSymbolSeason3.income_from_discontinued_operations
            if income_statement.basic_earnings_per_share is not None:
                income_statement.save()
                last_year_income_statement.save()
                print stock_symbol + ' data updated'
            else:
                print stock_symbol + 'time sleep'
                time.sleep(5)

    return HttpResponse("update_season_income_statement")

#balance sheet from TWSE
def show_season_balance_sheet(request):
    stock_symbol = '2823'
    year = 102
    season = 2
    url = 'http://mops.twse.com.tw/mops/web/t164sb03'
    values = {'encodeURIComponent' : '1', 'step' : '1', 'firstin' : '1', 'off' : '1',
            'keyword4' : '','code1' : '','TYPEK2' : '','checkbtn' : '',
            'queryName':'co_id', 'TYPEK':'all', 'isnew':'true', 'co_id' : stock_symbol, 'year' : year, 'season' : str(season).zfill(2) }
    values = {'encodeURIComponent' : '1', 'id' : '', 'key' : '', 'TYPEK' : 'sii', 'step' : '2',
              'year' : '102', 'season' : '2', 'co_id' : stock_symbol, 'firstin' : '1'}
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

def update_season_balance_sheet(request):
    if 'year' in request.GET and  'season' in request.GET:
        year = int(request.GET['year'])
        season = int(request.GET['season'])
    else:
        year = 102
        season = 3
    stock_ids = StockId.objects.all()
    for stock_id in stock_ids:
        stock_symbol = stock_id.symbol
        if not SeasonBalanceSheet.objects.filter(symbol=stock_symbol, year=year+1911, season=season):
            print stock_symbol + ' loaded'
            url = 'http://mops.twse.com.tw/mops/web/t164sb03'
            values = {'encodeURIComponent' : '1', 'step' : '1', 'firstin' : '1', 'off' : '1',
                    'keyword4' : '','code1' : '','TYPEK2' : '','checkbtn' : '',
                    'queryName':'co_id', 'TYPEK':'all', 'isnew':'true', 'co_id' : stock_symbol, 
                    'year' : year, 'season' : str(season).zfill(2) }
            values = {'encodeURIComponent' : '1', 'id' : '', 'key' : '', 'TYPEK' : 'sii', 'step' : '2',
              'year' : year, 'season' : str(season).zfill(2), 'co_id' : stock_symbol, 'firstin' : '1'}
            url_data = urllib.urlencode(values)
            req = urllib2.Request(url, url_data)
            response = urllib2.urlopen(req)
            soup = BeautifulSoup(response,from_encoding="utf-8")
           
            balance_sheet_datas = soup.find_all("td", {'style' : 'text-align:left;white-space:nowrap;'})
            balance_sheet = SeasonBalanceSheet()
            balance_sheet.symbol = stock_symbol
            balance_sheet.year = str(1911+year)
            balance_sheet.season = season

            balance_sheet.date = season_to_date(1911+year, season)
            balance_sheet.surrogate_key = stock_symbol + '_' + str(1911+year) + str(season).zfill(2)

            last_balance_sheet = SeasonBalanceSheet()
            last_balance_sheet.symbol = stock_symbol
            last_balance_sheet.year = str(1910+year)
            last_balance_sheet.season = season
            last_balance_sheet.date = season_to_date(1910+year, season)
            last_balance_sheet.surrogate_key = stock_symbol + '_' + str(1910+year) + str(season).zfill(2)

            for data in balance_sheet_datas:
                if r'現金及約當現金' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.cash_and_cash_equivalents = st_to_decimal(next_data.string)
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_balance_sheet.cash_and_cash_equivalents = st_to_decimal(next_data.string)
                elif r'透過損益按公允價值衡量之金融資產－流動' in data.string.encode('utf-8') or r'備供出售金融資產－流動淨額' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.current_financial_assets = st_to_decimal(next_data.string)
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_balance_sheet.current_financial_assets = st_to_decimal(next_data.string)
                elif r'應收票據淨額' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.notes_receivable = st_to_decimal(next_data.string)
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_balance_sheet.notes_receivable = st_to_decimal(next_data.string)
                elif r'應收帳款淨額' in data.string.encode('utf-8') or r'應收款項淨額' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.accounts_receivable = st_to_decimal(next_data.string)
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_balance_sheet.accounts_receivable = st_to_decimal(next_data.string)
                elif r'存貨' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.inventories = st_to_decimal(next_data.string)
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_balance_sheet.inventories = st_to_decimal(next_data.string)
                elif r'預付款項' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.prepayments = st_to_decimal(next_data.string)
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_balance_sheet.prepayments = st_to_decimal(next_data.string)
                elif r'其他流動資產' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.other_current_assets = st_to_decimal(next_data.string)
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_balance_sheet.other_current_assets = st_to_decimal(next_data.string)
                elif r'流動資產合計' in data.string.encode('utf-8') and r'非' not in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.total_current_assets = st_to_decimal(next_data.string)
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_balance_sheet.total_current_assets = st_to_decimal(next_data.string)
                elif r'備供出售金融資產－非流動淨額' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.non_current_available_for_sale_financial_assets = st_to_decimal(next_data.string)
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_balance_sheet.non_current_available_for_sale_financial_assets = st_to_decimal(next_data.string)
                elif r'不動產、廠房及設備' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.property_plant_and_equipment = st_to_decimal(next_data.string)
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_balance_sheet.property_plant_and_equipment = st_to_decimal(next_data.string)
                elif r'投資性不動產淨額' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.investment_property = st_to_decimal(next_data.string)
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_balance_sheet.investment_property = st_to_decimal(next_data.string)
                elif r'無形資產' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        balance_sheet.intangible_assets = st_to_decimal(next_data.string)
                        next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                        last_balance_sheet.intangible_assets = st_to_decimal(next_data.string)
                elif r'遞延所得稅資產' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.deferred_tax_assets = st_to_decimal(next_data.string)
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_balance_sheet.deferred_tax_assets = st_to_decimal(next_data.string)
                elif r'其他非流動資產' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.other_non_current_assets = st_to_decimal(next_data.string)
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_balance_sheet.other_non_current_assets = st_to_decimal(next_data.string)
                elif r'非流動資產合計' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.total_non_current_assets = st_to_decimal(next_data.string)
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_balance_sheet.total_non_current_assets = st_to_decimal(next_data.string)
                elif r'資產總額' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.total_assets = st_to_decimal(next_data.string)
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_balance_sheet.total_assets = st_to_decimal(next_data.string)
                elif r'短期借款' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.short_term_borrowings = st_to_decimal(next_data.string)
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_balance_sheet.short_term_borrowings = st_to_decimal(next_data.string)
                elif r'透過損益按公允價值衡量之金融負債－流動' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.current_financial_liabilities = st_to_decimal(next_data.string)
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_balance_sheet.current_financial_liabilities = st_to_decimal(next_data.string)
                elif r'應付票據' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.notes_payable = st_to_decimal(next_data.string)
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_balance_sheet.notes_payable = st_to_decimal(next_data.string)
                elif r'應付帳款' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.accounts_payable = st_to_decimal(next_data.string)
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_balance_sheet.accounts_payable = st_to_decimal(next_data.string)
                elif r'其他應付款' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.other_payables = st_to_decimal(next_data.string)
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_balance_sheet.other_payables = st_to_decimal(next_data.string)
                elif r'當期所得稅負債' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.current_tax_liabilities = st_to_decimal(next_data.string)
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_balance_sheet.current_tax_liabilities = st_to_decimal(next_data.string)
                elif r'負債準備－流動' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.current_provisions = st_to_decimal(next_data.string)
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_balance_sheet.current_provisions = st_to_decimal(next_data.string)
                elif r'其他流動負債' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.other_current_liabilities = st_to_decimal(next_data.string)
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_balance_sheet.other_current_liabilities = st_to_decimal(next_data.string)
                elif r'流動負債合計' in data.string.encode('utf-8') and r'非' not in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.total_current_liabilities = st_to_decimal(next_data.string)
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_balance_sheet.total_current_liabilities = st_to_decimal(next_data.string)
                elif r'遞延所得稅負債' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.deferred_tax_liabilities = st_to_decimal(next_data.string)
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_balance_sheet.deferred_tax_liabilities = st_to_decimal(next_data.string)
                elif r'其他非流動負債' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.other_non_current_liabilities = st_to_decimal(next_data.string)
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_balance_sheet.other_non_current_liabilities = st_to_decimal(next_data.string)
                elif r'非流動負債合計' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.total_non_current_liabilities = st_to_decimal(next_data.string)
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_balance_sheet.total_non_current_liabilities = st_to_decimal(next_data.string)
                elif r'負債總額' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.total_liabilities = st_to_decimal(next_data.string)
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_balance_sheet.total_liabilities = st_to_decimal(next_data.string)
                elif r'普通股股本' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.ordinary_share = st_to_decimal(next_data.string)
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_balance_sheet.ordinary_share = st_to_decimal(next_data.string)
                elif r'股本合計' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.total_capital_stock = st_to_decimal(next_data.string)
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_balance_sheet.total_capital_stock = st_to_decimal(next_data.string)
                elif r'資本公積－發行溢價' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.additional_paid_in_capital = st_to_decimal(next_data.string)
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_balance_sheet.additional_paid_in_capital = st_to_decimal(next_data.string)
                elif r'資本公積－庫藏股票交易' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.treasury_share_transactions = st_to_decimal(next_data.string)
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_balance_sheet.treasury_share_transactions = st_to_decimal(next_data.string)
                elif r'資本公積－合併溢額' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.net_assets_from_merger = st_to_decimal(next_data.string)
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_balance_sheet.net_assets_from_merger = st_to_decimal(next_data.string)
                elif r'資本公積合計' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.total_capital_surplus = st_to_decimal(next_data.string)
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_balance_sheet.total_capital_surplus = st_to_decimal(next_data.string)
                elif r'法定盈餘公積' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.legal_reserve = st_to_decimal(next_data.string)
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_balance_sheet.legal_reserve = st_to_decimal(next_data.string)
                elif r'特別盈餘公積' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.special_reserve = st_to_decimal(next_data.string)
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_balance_sheet.special_reserve = st_to_decimal(next_data.string)
                elif r'未分配盈餘（或待彌補虧損）' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.unappropriated_retained_earnings = st_to_decimal(next_data.string)
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_balance_sheet.unappropriated_retained_earnings = st_to_decimal(next_data.string)
                elif r'保留盈餘合計' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.retained_earnings = st_to_decimal(next_data.string)
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_balance_sheet.retained_earnings = st_to_decimal(next_data.string)
                elif r'國外營運機構財務報表換算之兌換差額' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.exchange_differences_of_foreign_financial_statements = st_to_decimal(next_data.string)
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_balance_sheet.exchange_differences_of_foreign_financial_statements = st_to_decimal(next_data.string)
                elif r'備供出售金融資產未實現損益' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.unrealised_gains_for_sale_financial_assets = st_to_decimal(next_data.string)
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_balance_sheet.unrealised_gains_for_sale_financial_assets = st_to_decimal(next_data.string)
                elif r'其他權益合計' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.other_equity_interest = st_to_decimal(next_data.string)
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_balance_sheet.other_equity_interest = st_to_decimal(next_data.string)
                elif r'歸屬於母公司業主之權益合計' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.equity_attributable_to_owners_of_parent = st_to_decimal(next_data.string)
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_balance_sheet.equity_attributable_to_owners_of_parent = st_to_decimal(next_data.string)
                elif r'非控制權益' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.non_controlling_interests = st_to_decimal(next_data.string)
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_balance_sheet.non_controlling_interests = st_to_decimal(next_data.string)
                elif r'權益總額' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.total_equity = st_to_decimal(next_data.string)
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_balance_sheet.total_equity = st_to_decimal(next_data.string)
                elif r'預收股款（權益項下）之約當發行股數（單位：股）' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.equivalent_issue_shares_of_advance_receipts = st_to_decimal(next_data.string)
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_balance_sheet.equivalent_issue_shares_of_advance_receipts = st_to_decimal(next_data.string)
                elif r'母公司暨子公司所持有之母公司庫藏股股數（單位：股）' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.number_of_shares_in_entity_held_by_entity = st_to_decimal(next_data.string)
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_balance_sheet.number_of_shares_in_entity_held_by_entity = st_to_decimal(next_data.string)
            if balance_sheet.cash_and_cash_equivalents:
                balance_sheet.save()
                last_balance_sheet.save()
            else:
                print stock_symbol + ' time sleep'
                time.sleep(5)

            print stock_symbol + ' data updated'
    
    return HttpResponse('balance sheet updated')

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
