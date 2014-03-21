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
from bs4 import BeautifulSoup
import html5lib
import datetime
from core.utils import st_to_decimal, season_to_date, last_season

#income statement from TWSE 綜合損益表
def show_season_income_statement(request):
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
    soup = BeautifulSoup(response,from_encoding="utf-8")
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

#綜合損益表
def update_season_income_statement(request):
    if 'year' in request.GET and  'season' in request.GET:
        year = int(request.GET['year'])
        season = int(request.GET['season'])
    else:
        year = 102
        season = 4
    stock_ids = StockId.objects.all()
    for stock_id in stock_ids:
        stock_symbol = stock_id.symbol
        if not (SeasonIncomeStatement.objects.filter(symbol=stock_symbol, year=year+1911, season=season) and SeasonIncomeStatement.objects.filter(symbol=stock_symbol, year=year+1910, season=season)):
            url = 'http://mops.twse.com.tw/mops/web/ajax_t164sb04'
            values = {'encodeURIComponent' : '1', 'step' : '1', 'firstin' : '1', 'off' : '1',
            'keyword4' : '','code1' : '','TYPEK2' : '','checkbtn' : '',
            'queryName':'co_id', 'TYPEK':'all', 'isnew':'false', 'co_id' : stock_symbol, 'year' : year, 'season' : str(season).zfill(2) }
            values = {'encodeURIComponent' : '1', 'id' : '', 'key' : '', 'TYPEK' : 'sii', 'step' : '2',
                      'year' : year, 'season' : str(season).zfill(2), 'co_id' : stock_symbol, 'firstin' : '1'}
            url_data = urllib.urlencode(values)
            req = urllib2.Request(url, url_data)
            response = urllib2.urlopen(req)
            soup = BeautifulSoup(response,from_encoding="utf-8")
            
            season_income_datas = soup.find_all("td", {'style' : 'text-align:left;white-space:nowrap;'})
            income_statement = SeasonIncomeStatement()
            income_statement.symbol = stock_symbol
            income_statement.year = str(1911+year)
            income_statement.season = season
            income_statement.surrogate_key = stock_symbol + '_' + str(1911+year) + str(season).zfill(2)

            income_statement.date = season_to_date(1911+year, season)

            last_income_statement = SeasonIncomeStatement()
            last_income_statement.symbol = stock_symbol
            last_income_statement.year = str(1910+year)
            last_income_statement.season = season

            last_income_statement.date = season_to_date(1910+year, season)
            
            last_income_statement.surrogate_key = stock_symbol + '_' + str(1910+year) + str(season).zfill(2)

            owners_of_parent = 0
            print stock_symbol + ' loaded'
            for data in season_income_datas:
                if r'營業收入合計' in data.string.encode('utf-8') or r'收入合計' == data.string.encode('utf-8') or r'淨收益' == data.string.encode('utf-8') or r'收益合計' == data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    income_statement.operating_revenue = st_to_decimal(next_data.string)
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_income_statement.operating_revenue = st_to_decimal(next_data.string)
                elif r'營業成本合計' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    income_statement.operating_cost = st_to_decimal(next_data.string)
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_income_statement.operating_cost = st_to_decimal(next_data.string)
                elif r'營業毛利（毛損）' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    income_statement.gross_profit_from_operations = st_to_decimal(next_data.string)
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_income_statement.gross_profit_from_operations = st_to_decimal(next_data.string)
                elif r'推銷費用' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    income_statement.selling_expenses = st_to_decimal(next_data.string)
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_income_statement.selling_expenses = st_to_decimal(next_data.string)
                elif r'管理費用' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    income_statement.administrative_expenses = st_to_decimal(next_data.string)
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_income_statement.administrative_expenses = st_to_decimal(next_data.string)
                elif r'研究發展費用' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    income_statement.research_and_development_expenses = st_to_decimal(next_data.string)
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_income_statement.research_and_development_expenses = st_to_decimal(next_data.string)
                elif r'營業費用合計' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    income_statement.operating_expenses = st_to_decimal(next_data.string)
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_income_statement.operating_expenses = st_to_decimal(next_data.string)
                elif r'營業利益（損失）' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    income_statement.net_operating_income = st_to_decimal(next_data.string)
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_income_statement.net_operating_income = st_to_decimal(next_data.string)
                elif r'其他收入' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    income_statement.other_income = st_to_decimal(next_data.string)
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_income_statement.other_income = st_to_decimal(next_data.string)
                elif r'其他利益及損失淨額' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    income_statement.other_gains_and_losses = st_to_decimal(next_data.string)
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_income_statement.other_gains_and_losses = st_to_decimal(next_data.string)
                elif r'財務成本淨額' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    income_statement.finance_costs = st_to_decimal(next_data.string)
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_income_statement.finance_costs = st_to_decimal(next_data.string)
                elif r'營業外收入及支出合計' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    income_statement.non_operating_income_and_expenses = st_to_decimal(next_data.string)
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_income_statement.non_operating_income_and_expenses = st_to_decimal(next_data.string)
                elif r'稅前淨利（淨損）' in data.string.encode('utf-8') or r'繼續營業單位稅前淨利（淨損）' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    income_statement.profit_from_continuing_operations_before_tax = st_to_decimal(next_data.string)
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_income_statement.profit_from_continuing_operations_before_tax = st_to_decimal(next_data.string)
                elif r'所得稅費用（利益）合計' in data.string.encode('utf-8') or r'所得稅（費用）利益' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    income_statement.tax_expense = st_to_decimal(next_data.string)
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_income_statement.tax_expense = st_to_decimal(next_data.string)
                elif r'繼續營業單位本期淨利（淨損）' in data.string.encode('utf-8') or r'繼續營業單位本期稅後淨利（淨損）' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    income_statement.profit_from_continuing_operations = st_to_decimal(next_data.string)
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_income_statement.profit_from_continuing_operations = st_to_decimal(next_data.string)
                elif r'本期淨利（淨損）' in data.string.encode('utf-8') or r'本期稅後淨利（淨損）' in data.string.encode('utf-8'):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        income_statement.profit = st_to_decimal(next_data.string)
                        next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                        last_income_statement.profit = st_to_decimal(next_data.string)
                elif r'國外營運機構財務報表換算之兌換差額' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    income_statement.exchange_differences_on_translation = st_to_decimal(next_data.string)
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_income_statement.exchange_differences_on_translation = st_to_decimal(next_data.string)
                elif r'備供出售金融資產未實現評價損益' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    income_statement.unrealised_gains_for_sale_financial_assets = st_to_decimal(next_data.string)
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_income_statement.unrealised_gains_for_sale_financial_assets = st_to_decimal(next_data.string)
                elif r'與其他綜合損益組成部分相關之所得稅' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    income_statement.income_tax_of_other_comprehensive_income = st_to_decimal(next_data.string)
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_income_statement.income_tax_of_other_comprehensive_income = st_to_decimal(next_data.string)
                elif r'其他綜合損益（淨額）' in data.string.encode('utf-8') or r'其他綜合損益（稅後）淨額' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    income_statement.other_comprehensive_income = st_to_decimal(next_data.string)
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_income_statement.other_comprehensive_income = st_to_decimal(next_data.string)
                elif r'本期綜合損益總額' in data.string.encode('utf-8') or r'本期綜合損益總額（稅後）' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    income_statement.total_comprehensive_income = st_to_decimal(next_data.string)
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_income_statement.total_comprehensive_income = st_to_decimal(next_data.string)
                elif r'母公司業主（淨利／損）' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    income_statement.profit_to_owners_of_parent = st_to_decimal(next_data.string)
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_income_statement.profit_to_owners_of_parent = st_to_decimal(next_data.string)
                elif r'非控制權益（淨利／損）' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    income_statement.profit_to_non_controlling_interests = st_to_decimal(next_data.string)
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_income_statement.profit_to_non_controlling_interests = st_to_decimal(next_data.string)
                elif r'母公司業主（綜合損益）' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    income_statement.comprehensive_income_to_owners_of_parent = st_to_decimal(next_data.string)
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_income_statement.comprehensive_income_to_owners_of_parent = st_to_decimal(next_data.string)
                elif r'母公司業主' in data.string.encode('utf-8'):
                    if owners_of_parent == 0:
                        next_data = data.next_sibling.next_sibling
                        income_statement.profit_to_owners_of_parent = st_to_decimal(next_data.string)
                        next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                        last_income_statement.profit_to_owners_of_parent = st_to_decimal(next_data.string)
                        owners_of_parent = 1
                    else:
                        next_data = data.next_sibling.next_sibling
                        income_statement.comprehensive_income_to_owners_of_parent = st_to_decimal(next_data.string)
                        next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                        last_income_statement.comprehensive_income_to_owners_of_parent =st_to_decimal(next_data.string)
                elif r'非控制權益（綜合損益）' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    income_statement.comprehensive_income_to_non_controlling_interests = st_to_decimal(next_data.string)
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_income_statement.comprehensive_income_to_non_controlling_interests = st_to_decimal(next_data.string)
                elif r'基本每股盈餘' in data.string.encode('utf-8'):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        income_statement.basic_earnings_per_share = st_to_decimal(next_data.string)
                        next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                        last_income_statement.basic_earnings_per_share = st_to_decimal(next_data.string)
                elif r'稀釋每股盈餘' in data.string.encode('utf-8'):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        income_statement.diluted_earnings_per_share = st_to_decimal(next_data.string)
                        next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                        last_income_statement.diluted_earnings_per_share = st_to_decimal(next_data.string)
                elif r'利息收入' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    income_statement.interest_income = st_to_decimal(next_data.string)
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_income_statement.interest_income = st_to_decimal(next_data.string)
                elif r'減：利息費用' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    income_statement.interest_expenses = st_to_decimal(next_data.string)
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_income_statement.interest_expenses = st_to_decimal(next_data.string)
                elif r'利息淨收益' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    income_statement.net_income_of_interest = st_to_decimal(next_data.string)
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_income_statement.net_income_of_interest = st_to_decimal(next_data.string)
                elif r'手續費淨收益' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    income_statement.net_service_fee_income = st_to_decimal(next_data.string)
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_income_statement.net_service_fee_income = st_to_decimal(next_data.string)
                elif r'透過損益按公允價值衡量之金融資產及負債損益' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    income_statement.gain_on_financial_assets_or_liabilities_measured = st_to_decimal(next_data.string)
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_income_statement.gain_on_financial_assets_or_liabilities_measured = st_to_decimal(next_data.string)
                elif r'備供出售金融資產之已實現損益' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    income_statement.realized_gains_for_sale_financial_assets = st_to_decimal(next_data.string)
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_income_statement.realized_gains_for_sale_financial_assets = st_to_decimal(next_data.string)
                elif r'持有至到期日金融資產之已實現損益' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    income_statement.realized_gains_on_held_to_maturity_financial_assets = st_to_decimal(next_data.string)
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_income_statement.realized_gains_on_held_to_maturity_financial_assets = st_to_decimal(next_data.string)
                elif r'兌換損益' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    income_statement.foreign_exchange_gain = st_to_decimal(next_data.string)
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_income_statement.foreign_exchange_gain = st_to_decimal(next_data.string)
                elif r'資產減損（損失）迴轉利益淨額' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    income_statement.reversal_of_impairment_loss_on_assets = st_to_decimal(next_data.string)
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_income_statement.reversal_of_impairment_loss_on_assets = st_to_decimal(next_data.string)
                elif r'採用權益法認列之關聯企業及合資損益之份額' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    income_statement.gain_on_disposal_of_investments_accounted = st_to_decimal(next_data.string)
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_income_statement.gain_on_disposal_of_investments_accounted = st_to_decimal(next_data.string)
                elif r'其他利息以外淨損益' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    income_statement.net_other_non_interest_income = st_to_decimal(next_data.string)
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_income_statement.net_other_non_interest_income = st_to_decimal(next_data.string)
                elif r'利息以外淨損益' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    income_statement.net_non_interest_income = st_to_decimal(next_data.string)
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_income_statement.net_non_interest_income = st_to_decimal(next_data.string)
                elif r'淨收益' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    income_statement.net_income = st_to_decimal(next_data.string)
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_income_statement.net_income = st_to_decimal(next_data.string)
                elif r'呆帳費用及保證責任準備提存（各項提存）' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    income_statement.total_bad_debts_expense = st_to_decimal(next_data.string)
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_income_statement.total_bad_debts_expense = st_to_decimal(next_data.string)
                elif r'員工福利費用' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    income_statement.employee_benefits_expenses = st_to_decimal(next_data.string)
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_income_statement.employee_benefits_expenses = st_to_decimal(next_data.string)
                elif r'折舊及攤銷費用' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    income_statement.depreciation_and_amortization_expense = st_to_decimal(next_data.string)
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_income_statement.depreciation_and_amortization_expense = st_to_decimal(next_data.string)
                elif r'停業單位損益' in data.string.encode('utf-8') or r'停業單位損益合計' in data.string.encode('utf-8'):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        income_statement.income_from_discontinued_operations = st_to_decimal(next_data.string)
                        next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                        last_income_statement.income_from_discontinued_operations = st_to_decimal(next_data.string)
            if income_statement.basic_earnings_per_share is not None:
                income_statement.save()
                last_income_statement.save()
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
    today = datetime.date.today()
    for stock_id in stock_ids:
        stock_symbol = stock_id.symbol
        (last_season_year, last_season_season) = last_season(today)
        ratioInDb = SeasonFinancialRatio.objects.filter(symbol=stock_symbol, year=last_season_year, season=last_season_season)
        if ratioInDb:
            # print stock_symbol + ' exists'
            continue
        url = 'http://jsjustweb.jihsun.com.tw/z/zc/zcr/zcr_' + stock_symbol + '.djhtm'
        webcode = urllib.urlopen(url)
        soup = BeautifulSoup(webcode)
        stage_datas = soup.find_all('td', {'class':'t2'})

        isDataStart = False
        arrRatioDatas = []
        for stage_data in stage_datas:
            if isDataStart:
                year = int(stage_data.string.split('Q')[0].split('.')[0]) + 1911
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
