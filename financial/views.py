#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib2
import urllib
from django.http import HttpResponse
from HTMLParser import HTMLParser
import time
from decimal import Decimal
from stocks.models import StockId
from financial.models import SeasonFinancialRatio, SeasonBalanceSheet, SeasonIncomeStatement
from bs4 import BeautifulSoup
import html5lib
from html5lib import sanitizer
from html5lib import treebuilders


#income statement from TWSE 綜合損益表
def show_season_income_statement(request):
    stock_symbol = '1409'
    year = 102
    season = 2
    url = 'http://mops.twse.com.tw/mops/web/ajax_t164sb04'
    values = {'encodeURIComponent' : '1', 'step' : '1', 'firstin' : '1', 'off' : '1',
              'keyword4' : '','code1' : '','TYPEK2' : '','checkbtn' : '',
              'queryName':'co_id', 'TYPEK':'all', 'isnew':'true', 'co_id' : stock_symbol, 'year' : year, 'season' : str(season).zfill(2) }
    values = {'encodeURIComponent' : '1', 'id' : '', 'key' : '', 'TYPEK' : 'sii', 'step' : '2',
              'year' : '102', 'season' : '2', 'co_id' : stock_symbol, 'firstin' : '1'}
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
                    print 'hello'
                    print Decimal(data.next_sibling.next_sibling.string.strip().replace(',',''))
    req = urllib2.Request(url, url_data)
    response = urllib2.urlopen(req)
    return HttpResponse(response.read())

def update_season_income_statement(request):
    stock_ids = StockId.objects.all()
    for stock_id in stock_ids:
        stock_symbol = stock_id.symbol
        year = 102
        season = 1
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

            last_income_statement = SeasonIncomeStatement()
            last_income_statement.symbol = stock_symbol
            last_income_statement.year = str(1910+year)
            last_income_statement.season = season
            last_income_statement.surrogate_key = stock_symbol + '_' + str(1910+year) + str(season).zfill(2)

            owners_of_parent = 0
            print stock_symbol + ' loaded'
            for data in season_income_datas:
                if r'營業收入合計' in data.string.encode('utf-8') or r'收入合計' == data.string.encode('utf-8') or r'淨收益' == data.string.encode('utf-8') or r'收益合計' == data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    income_statement.operating_revenue = Decimal(next_data.string.strip().replace(',',''))
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_income_statement.operating_revenue = Decimal(next_data.string.strip().replace(',',''))
                elif r'營業成本合計' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    income_statement.operating_cost = Decimal(next_data.string.strip().replace(',',''))
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_income_statement.operating_cost = Decimal(next_data.string.strip().replace(',',''))
                elif r'營業毛利（毛損）' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    income_statement.gross_profit_from_operations = Decimal(next_data.string.strip().replace(',',''))
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_income_statement.gross_profit_from_operations = Decimal(next_data.string.strip().replace(',',''))
                elif r'推銷費用' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    income_statement.selling_expenses = Decimal(next_data.string.strip().replace(',',''))
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_income_statement.selling_expenses = Decimal(next_data.string.strip().replace(',',''))
                elif r'管理費用' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    income_statement.administrative_expenses = Decimal(next_data.string.strip().replace(',',''))
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_income_statement.administrative_expenses = Decimal(next_data.string.strip().replace(',',''))
                elif r'研究發展費用' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    income_statement.research_and_development_expenses = Decimal(next_data.string.strip().replace(',',''))
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_income_statement.research_and_development_expenses = Decimal(next_data.string.strip().replace(',',''))
                elif r'營業費用合計' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    income_statement.operating_expenses = Decimal(next_data.string.strip().replace(',',''))
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_income_statement.operating_expenses = Decimal(next_data.string.strip().replace(',',''))
                elif r'營業利益（損失）' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    income_statement.net_operating_income = Decimal(next_data.string.strip().replace(',',''))
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_income_statement.net_operating_income = Decimal(next_data.string.strip().replace(',',''))
                elif r'其他收入' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    income_statement.other_income = Decimal(next_data.string.strip().replace(',',''))
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_income_statement.other_income = Decimal(next_data.string.strip().replace(',',''))
                elif r'其他利益及損失淨額' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    income_statement.other_gains_and_losses = Decimal(next_data.string.strip().replace(',',''))
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_income_statement.other_gains_and_losses = Decimal(next_data.string.strip().replace(',',''))
                elif r'財務成本淨額' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    income_statement.finance_costs = Decimal(next_data.string.strip().replace(',',''))
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_income_statement.finance_costs = Decimal(next_data.string.strip().replace(',',''))
                elif r'營業外收入及支出合計' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    income_statement.non_operating_income_and_expenses = Decimal(next_data.string.strip().replace(',',''))
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_income_statement.non_operating_income_and_expenses = Decimal(next_data.string.strip().replace(',',''))
                elif r'稅前淨利（淨損）' in data.string.encode('utf-8') or r'繼續營業單位稅前淨利（淨損）' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    income_statement.profit_from_continuing_operations_before_tax = Decimal(next_data.string.strip().replace(',',''))
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_income_statement.profit_from_continuing_operations_before_tax = Decimal(next_data.string.strip().replace(',',''))
                elif r'所得稅費用（利益）合計' in data.string.encode('utf-8') or r'所得稅（費用）利益' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    income_statement.tax_expense = Decimal(next_data.string.strip().replace(',',''))
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_income_statement.tax_expense = Decimal(next_data.string.strip().replace(',',''))
                elif r'繼續營業單位本期淨利（淨損）' in data.string.encode('utf-8') or r'繼續營業單位本期稅後淨利（淨損）' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    income_statement.profit_from_continuing_operations = Decimal(next_data.string.strip().replace(',',''))
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_income_statement.profit_from_continuing_operations = Decimal(next_data.string.strip().replace(',',''))
                elif r'本期淨利（淨損）' in data.string.encode('utf-8') or r'本期稅後淨利（淨損）' in data.string.encode('utf-8'):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        income_statement.profit = Decimal(next_data.string.strip().replace(',',''))
                        next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                        last_income_statement.profit = Decimal(next_data.string.strip().replace(',',''))
                elif r'國外營運機構財務報表換算之兌換差額' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    income_statement.exchange_differences_on_translation = Decimal(next_data.string.strip().replace(',',''))
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_income_statement.exchange_differences_on_translation = Decimal(next_data.string.strip().replace(',',''))
                elif r'備供出售金融資產未實現評價損益' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    income_statement.unrealised_gains_for_sale_financial_assets = Decimal(next_data.string.strip().replace(',',''))
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_income_statement.unrealised_gains_for_sale_financial_assets = Decimal(next_data.string.strip().replace(',',''))
                elif r'與其他綜合損益組成部分相關之所得稅' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    income_statement.income_tax_of_other_comprehensive_income = Decimal(next_data.string.strip().replace(',',''))
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_income_statement.income_tax_of_other_comprehensive_income = Decimal(next_data.string.strip().replace(',',''))
                elif r'其他綜合損益（淨額）' in data.string.encode('utf-8') or r'其他綜合損益（稅後）淨額' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    income_statement.other_comprehensive_income = Decimal(next_data.string.strip().replace(',',''))
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_income_statement.other_comprehensive_income = Decimal(next_data.string.strip().replace(',',''))
                elif r'本期綜合損益總額' in data.string.encode('utf-8') or r'本期綜合損益總額（稅後）' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    income_statement.total_comprehensive_income = Decimal(next_data.string.strip().replace(',',''))
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_income_statement.total_comprehensive_income = Decimal(next_data.string.strip().replace(',',''))
                elif r'母公司業主（淨利／損）' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    income_statement.profit_to_owners_of_parent = Decimal(next_data.string.strip().replace(',',''))
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_income_statement.profit_to_owners_of_parent = Decimal(next_data.string.strip().replace(',',''))
                elif r'非控制權益（淨利／損）' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    income_statement.profit_to_non_controlling_interests = Decimal(next_data.string.strip().replace(',',''))
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_income_statement.profit_to_non_controlling_interests = Decimal(next_data.string.strip().replace(',',''))
                elif r'母公司業主（綜合損益）' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    income_statement.comprehensive_income_to_owners_of_parent = Decimal(next_data.string.strip().replace(',',''))
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_income_statement.comprehensive_income_to_owners_of_parent = Decimal(next_data.string.strip().replace(',',''))
                elif r'母公司業主' in data.string.encode('utf-8'):
                    if owners_of_parent == 0:
                        next_data = data.next_sibling.next_sibling
                        income_statement.profit_to_owners_of_parent = Decimal(next_data.string.strip().replace(',',''))
                        next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                        last_income_statement.profit_to_owners_of_parent = Decimal(next_data.string.strip().replace(',',''))
                        owners_of_parent = 1
                    else:
                        next_data = data.next_sibling.next_sibling
                        income_statement.comprehensive_income_to_owners_of_parent = Decimal(next_data.string.strip().replace(',',''))
                        next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                        last_income_statement.comprehensive_income_to_owners_of_parent = Decimal(next_data.string.strip().replace(',',''))
                elif r'非控制權益（綜合損益）' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    income_statement.comprehensive_income_to_non_controlling_interests = Decimal(next_data.string.strip().replace(',',''))
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_income_statement.comprehensive_income_to_non_controlling_interests = Decimal(next_data.string.strip().replace(',',''))
                elif r'基本每股盈餘' in data.string.encode('utf-8'):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        income_statement.basic_earnings_per_share = Decimal(next_data.string.strip().replace(',',''))
                        next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                        last_income_statement.basic_earnings_per_share = Decimal(next_data.string.strip().replace(',',''))
                elif r'稀釋每股盈餘' in data.string.encode('utf-8'):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        income_statement.diluted_earnings_per_share = Decimal(next_data.string.strip().replace(',',''))
                        next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                        last_income_statement.diluted_earnings_per_share = Decimal(next_data.string.strip().replace(',',''))
                elif r'利息收入' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    income_statement.interest_income = Decimal(next_data.string.strip().replace(',',''))
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_income_statement.interest_income = Decimal(next_data.string.strip().replace(',',''))
                elif r'減：利息費用' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    income_statement.interest_expenses = Decimal(next_data.string.strip().replace(',',''))
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_income_statement.interest_expenses = Decimal(next_data.string.strip().replace(',',''))
                elif r'利息淨收益' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    income_statement.net_income_of_interest = Decimal(next_data.string.strip().replace(',',''))
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_income_statement.net_income_of_interest = Decimal(next_data.string.strip().replace(',',''))
                elif r'手續費淨收益' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    income_statement.net_service_fee_income = Decimal(next_data.string.strip().replace(',',''))
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_income_statement.net_service_fee_income = Decimal(next_data.string.strip().replace(',',''))
                elif r'透過損益按公允價值衡量之金融資產及負債損益' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    income_statement.gain_on_financial_assets_or_liabilities_measured = Decimal(next_data.string.strip().replace(',',''))
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_income_statement.gain_on_financial_assets_or_liabilities_measured = Decimal(next_data.string.strip().replace(',',''))
                elif r'備供出售金融資產之已實現損益' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    income_statement.realized_gains_for_sale_financial_assets = Decimal(next_data.string.strip().replace(',',''))
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_income_statement.realized_gains_for_sale_financial_assets = Decimal(next_data.string.strip().replace(',',''))
                elif r'持有至到期日金融資產之已實現損益' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    income_statement.realized_gains_on_held_to_maturity_financial_assets = Decimal(next_data.string.strip().replace(',',''))
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_income_statement.realized_gains_on_held_to_maturity_financial_assets = Decimal(next_data.string.strip().replace(',',''))
                elif r'兌換損益' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    income_statement.foreign_exchange_gain = Decimal(next_data.string.strip().replace(',',''))
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_income_statement.foreign_exchange_gain = Decimal(next_data.string.strip().replace(',',''))
                elif r'資產減損（損失）迴轉利益淨額' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    income_statement.reversal_of_impairment_loss_on_assets = Decimal(next_data.string.strip().replace(',',''))
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_income_statement.reversal_of_impairment_loss_on_assets = Decimal(next_data.string.strip().replace(',',''))
                elif r'採用權益法認列之關聯企業及合資損益之份額' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    income_statement.gain_on_disposal_of_investments_accounted = Decimal(next_data.string.strip().replace(',',''))
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_income_statement.gain_on_disposal_of_investments_accounted = Decimal(next_data.string.strip().replace(',',''))
                elif r'其他利息以外淨損益' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    income_statement.net_other_non_interest_income = Decimal(next_data.string.strip().replace(',',''))
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_income_statement.net_other_non_interest_income = Decimal(next_data.string.strip().replace(',',''))
                elif r'利息以外淨損益' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    income_statement.net_non_interest_income = Decimal(next_data.string.strip().replace(',',''))
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_income_statement.net_non_interest_income = Decimal(next_data.string.strip().replace(',',''))
                elif r'淨收益' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    income_statement.net_income = Decimal(next_data.string.strip().replace(',',''))
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_income_statement.net_income = Decimal(next_data.string.strip().replace(',',''))
                elif r'呆帳費用及保證責任準備提存（各項提存）' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    income_statement.total_bad_debts_expense = Decimal(next_data.string.strip().replace(',',''))
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_income_statement.total_bad_debts_expense = Decimal(next_data.string.strip().replace(',',''))
                elif r'員工福利費用' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    income_statement.employee_benefits_expenses = Decimal(next_data.string.strip().replace(',',''))
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_income_statement.employee_benefits_expenses = Decimal(next_data.string.strip().replace(',',''))
                elif r'折舊及攤銷費用' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    income_statement.depreciation_and_amortization_expense = Decimal(next_data.string.strip().replace(',',''))
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_income_statement.depreciation_and_amortization_expense = Decimal(next_data.string.strip().replace(',',''))
                elif r'停業單位損益' in data.string.encode('utf-8') or r'停業單位損益合計' in data.string.encode('utf-8'):
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        income_statement.income_from_discontinued_operations = Decimal(next_data.string.strip().replace(',',''))
                        next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                        last_income_statement.income_from_discontinued_operations = Decimal(next_data.string.strip().replace(',',''))
            if income_statement.basic_earnings_per_share is not None:
                income_statement.save()
                last_income_statement.save()
                print stock_symbol + ' data updated'
            else:
                print stock_symbol + 'time sleep'
                time.sleep(30)

    return HttpResponse("update_season_income_statement")

#balance sheet from TWSE
def show_season_balance_sheet(request):
    stock_symbol = '2823'
    year = 102
    season = 2
    url = 'http://mops.twse.com.tw/mops/web/t164sb03'
    values = {'encodeURIComponent' : '1', 'step' : '1', 'firstin' : '1', 'off' : '1',
<<<<<<< HEAD
            'keyword4' : '','code1' : '','TYPEK2' : '','checkbtn' : '',
            'queryName':'co_id', 'TYPEK':'all', 'isnew':'true', 'co_id' : stock_symbol, 'year' : year, 'season' : str(season).zfill(2) }
    url_data = urllib.urlencode(values) 

=======
              'keyword4' : '','code1' : '','TYPEK2' : '','checkbtn' : '',
              'queryName':'co_id', 'TYPEK':'all', 'isnew':'true', 'co_id' : stock_symbol, 'year' : year, 'season' : str(season).zfill(2) }
    values = {'encodeURIComponent' : '1', 'id' : '', 'key' : '', 'TYPEK' : 'sii', 'step' : '2',
              'year' : '102', 'season' : '2', 'co_id' : '2823', 'firstin' : '1'}
    url_data = urllib.urlencode(values)
>>>>>>> 82b03a188e4a2a8e8d0cb6ee40b46b2d2d9379c6
    req = urllib2.Request(url, url_data)
    response = urllib2.urlopen(req)

    soup = BeautifulSoup(response,from_encoding="utf-8")
    # print soup 詳細資料
    detail_button = soup.find_all("input", {'type': 'button', 'value': r'詳細資訊'})
    print detail_button

    balance_sheet_datas = soup.find_all("td", {'style' : 'text-align:left;white-space:nowrap;'})
    for data in balance_sheet_datas:
        if r'現金及約當現金' in data.string.encode('utf-8'):
            print Decimal(data.next_sibling.next_sibling.string.strip().replace(',',''))
    req = urllib2.Request(url, url_data)
    response = urllib2.urlopen(req)
    return HttpResponse(response.read())

def update_season_balance_sheet(request):
    stock_ids = StockId.objects.all()
    for stock_id in stock_ids:
        stock_symbol = stock_id.symbol
        year = 102
        season = 102

        if not SeasonBalanceSheet.objects.filter(symbol=stock_symbol, year=year+1911, season=season):

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
            balance_sheet.surrogate_key = stock_symbol + '_' + str(1911+year) + str(season).zfill(2)
            for data in balance_sheet_datas:
                if r'現金及約當現金' in data.string.encode('utf-8'):
                    balance_sheet.cash_and_cash_equivalents = Decimal(data.next_sibling.next_sibling.string.strip().replace(',',''))
                elif r'透過損益按公允價值衡量之金融資產－流動' in data.string.encode('utf-8') or r'備供出售金融資產－流動淨額' in data.string.encode('utf-8'):
                    balance_sheet.current_financial_assets = Decimal(data.next_sibling.next_sibling.string.strip().replace(',',''))
                elif r'應收票據淨額' in data.string.encode('utf-8'):
                    balance_sheet.notes_receivable = Decimal(data.next_sibling.next_sibling.string.strip().replace(',',''))
                elif r'應收帳款淨額' in data.string.encode('utf-8') or r'應收款項淨額' in data.string.encode('utf-8'):
                    balance_sheet.accounts_receivable = Decimal(data.next_sibling.next_sibling.string.strip().replace(',',''))
                elif r'存貨' in data.string.encode('utf-8'):
                    balance_sheet.inventories = Decimal(data.next_sibling.next_sibling.string.strip().replace(',',''))
                elif r'預付款項' in data.string.encode('utf-8'):
                    balance_sheet.prepayments = Decimal(data.next_sibling.next_sibling.string.strip().replace(',',''))
                elif r'其他流動資產' in data.string.encode('utf-8'):
                    balance_sheet.other_current_assets = Decimal(data.next_sibling.next_sibling.string.strip().replace(',',''))
                elif r'流動資產合計' in data.string.encode('utf-8') and r'非' not in data.string.encode('utf-8'):
                    balance_sheet.total_current_assets = Decimal(data.next_sibling.next_sibling.string.strip().replace(',',''))
                elif r'備供出售金融資產－非流動淨額' in data.string.encode('utf-8'):
                    balance_sheet.non_current_available_for_sale_financial_assets = Decimal(data.next_sibling.next_sibling.string.strip().replace(',',''))
                elif r'不動產、廠房及設備' in data.string.encode('utf-8'):
                    balance_sheet.property_plant_and_equipment = Decimal(data.next_sibling.next_sibling.string.strip().replace(',',''))
                elif r'投資性不動產淨額' in data.string.encode('utf-8'):
                    balance_sheet.investment_property = Decimal(data.next_sibling.next_sibling.string.strip().replace(',',''))
                elif r'無形資產' in data.string.encode('utf-8'):
                    if data.next_sibling.next_sibling.string is not None:
                        balance_sheet.intangible_assets = Decimal(data.next_sibling.next_sibling.string.strip().replace(',',''))
                elif r'遞延所得稅資產' in data.string.encode('utf-8'):
                    balance_sheet.deferred_tax_assets = Decimal(data.next_sibling.next_sibling.string.strip().replace(',',''))
                elif r'其他非流動資產' in data.string.encode('utf-8'):
                    balance_sheet.other_non_current_assets = Decimal(data.next_sibling.next_sibling.string.strip().replace(',',''))
                elif r'非流動資產合計' in data.string.encode('utf-8'):
                    balance_sheet.total_non_current_assets = Decimal(data.next_sibling.next_sibling.string.strip().replace(',',''))
                elif r'資產總額' in data.string.encode('utf-8'):
                    balance_sheet.total_assets = Decimal(data.next_sibling.next_sibling.string.strip().replace(',',''))
                elif r'短期借款' in data.string.encode('utf-8'):
                    balance_sheet.short_term_borrowings = Decimal(data.next_sibling.next_sibling.string.strip().replace(',',''))
                elif r'透過損益按公允價值衡量之金融負債－流動' in data.string.encode('utf-8'):
                    balance_sheet.current_financial_liabilities = Decimal(data.next_sibling.next_sibling.string.strip().replace(',',''))
                elif r'應付票據' in data.string.encode('utf-8'):
                    balance_sheet.notes_payable = Decimal(data.next_sibling.next_sibling.string.strip().replace(',',''))
                elif r'應付帳款' in data.string.encode('utf-8'):
                    balance_sheet.accounts_payable = Decimal(data.next_sibling.next_sibling.string.strip().replace(',',''))
                elif r'其他應付款' in data.string.encode('utf-8'):
                    balance_sheet.other_payables = Decimal(data.next_sibling.next_sibling.string.strip().replace(',',''))
                elif r'當期所得稅負債' in data.string.encode('utf-8'):
                    balance_sheet.current_tax_liabilities = Decimal(data.next_sibling.next_sibling.string.strip().replace(',',''))
                elif r'負債準備－流動' in data.string.encode('utf-8'):
                    balance_sheet.current_provisions = Decimal(data.next_sibling.next_sibling.string.strip().replace(',',''))
                elif r'其他流動負債' in data.string.encode('utf-8'):
                    balance_sheet.other_current_liabilities = Decimal(data.next_sibling.next_sibling.string.strip().replace(',',''))
                elif r'流動負債合計' in data.string.encode('utf-8') and r'非' not in data.string.encode('utf-8'):
                    balance_sheet.total_current_liabilities = Decimal(data.next_sibling.next_sibling.string.strip().replace(',',''))
                elif r'遞延所得稅負債' in data.string.encode('utf-8'):
                    balance_sheet.deferred_tax_liabilities = Decimal(data.next_sibling.next_sibling.string.strip().replace(',',''))
                elif r'其他非流動負債' in data.string.encode('utf-8'):
                    balance_sheet.other_non_current_liabilities = Decimal(data.next_sibling.next_sibling.string.strip().replace(',',''))
                elif r'非流動負債合計' in data.string.encode('utf-8'):
                    balance_sheet.total_non_current_liabilities = Decimal(data.next_sibling.next_sibling.string.strip().replace(',',''))
                elif r'負債總額' in data.string.encode('utf-8'):
                    balance_sheet.total_liabilities = Decimal(data.next_sibling.next_sibling.string.strip().replace(',',''))
                elif r'普通股股本' in data.string.encode('utf-8'):
                    balance_sheet.ordinary_share = Decimal(data.next_sibling.next_sibling.string.strip().replace(',',''))
                elif r'股本合計' in data.string.encode('utf-8'):
                    balance_sheet.total_capital_stock = Decimal(data.next_sibling.next_sibling.string.strip().replace(',',''))
                elif r'資本公積－發行溢價' in data.string.encode('utf-8'):
                    balance_sheet.additional_paid_in_capital = Decimal(data.next_sibling.next_sibling.string.strip().replace(',',''))
                elif r'資本公積－庫藏股票交易' in data.string.encode('utf-8'):
                    balance_sheet.treasury_share_transactions = Decimal(data.next_sibling.next_sibling.string.strip().replace(',',''))
                elif r'資本公積－合併溢額' in data.string.encode('utf-8'):
                    balance_sheet.net_assets_from_merger = Decimal(data.next_sibling.next_sibling.string.strip().replace(',',''))
                elif r'資本公積合計' in data.string.encode('utf-8'):
                    balance_sheet.total_capital_surplus = Decimal(data.next_sibling.next_sibling.string.strip().replace(',',''))
                elif r'法定盈餘公積' in data.string.encode('utf-8'):
                    balance_sheet.legal_reserve = Decimal(data.next_sibling.next_sibling.string.strip().replace(',',''))
                elif r'特別盈餘公積' in data.string.encode('utf-8'):
                    balance_sheet.special_reserve = Decimal(data.next_sibling.next_sibling.string.strip().replace(',',''))
                elif r'未分配盈餘（或待彌補虧損）' in data.string.encode('utf-8'):
                    balance_sheet.unappropriated_retained_earnings = Decimal(data.next_sibling.next_sibling.string.strip().replace(',',''))
                elif r'保留盈餘合計' in data.string.encode('utf-8'):
                    balance_sheet.retained_earnings = Decimal(data.next_sibling.next_sibling.string.strip().replace(',',''))
                elif r'國外營運機構財務報表換算之兌換差額' in data.string.encode('utf-8'):
                    balance_sheet.exchange_differences_of_foreign_financial_statements = Decimal(data.next_sibling.next_sibling.string.strip().replace(',',''))
                elif r'備供出售金融資產未實現損益' in data.string.encode('utf-8'):
                    balance_sheet.unrealised_gains_for_sale_financial_assets = Decimal(data.next_sibling.next_sibling.string.strip().replace(',',''))
                elif r'其他權益合計' in data.string.encode('utf-8'):
                    balance_sheet.other_equity_interest = Decimal(data.next_sibling.next_sibling.string.strip().replace(',',''))
                elif r'歸屬於母公司業主之權益合計' in data.string.encode('utf-8'):
                    balance_sheet.equity_attributable_to_owners_of_parent = Decimal(data.next_sibling.next_sibling.string.strip().replace(',',''))
                elif r'非控制權益' in data.string.encode('utf-8'):
                    balance_sheet.non_controlling_interests = Decimal(data.next_sibling.next_sibling.string.strip().replace(',',''))
                elif r'權益總額' in data.string.encode('utf-8'):
                    balance_sheet.total_equity = Decimal(data.next_sibling.next_sibling.string.strip().replace(',',''))
                elif r'預收股款（權益項下）之約當發行股數（單位：股）' in data.string.encode('utf-8'):
                    balance_sheet.equivalent_issue_shares_of_advance_receipts = Decimal(data.next_sibling.next_sibling.string.strip().replace(',',''))
                elif r'母公司暨子公司所持有之母公司庫藏股股數（單位：股）' in data.string.encode('utf-8'):
                    balance_sheet.number_of_shares_in_entity_held_by_entity = Decimal(data.next_sibling.next_sibling.string.strip().replace(',',''))
            if balance_sheet.cash_and_cash_equivalents:
                balance_sheet.save()
            else:
                print stock_symbol + ' time sleep'
                time.sleep(10)

            print stock_symbol + ' data updated'
    
    return HttpResponse('balance sheet updated')

def update_season_financial_ratio(request):
    stock_ids = StockId.objects.all()
    for stock_id in stock_ids:
        stock_symbol = stock_id.symbol
        url = 'http://jsjustweb.jihsun.com.tw/z/zc/zcr/zcr_' + stock_symbol + '.djhtm'
        webcode = urllib.urlopen(url)
        ratio = ParseSeasonFinancialRatio()
        if webcode.code == 200:
            ratio.feed(webcode.read())
            webcode.close()
        else:
            return HttpResponse('update season financial ratio failed')
        
        if not ratio.season_data:
            time.sleep(0.5)
            webcode = urllib.urlopen(url)
            ratio.feed(webcode.read())
            webcode.close()

        if ratio.season_data:
            for data in ratio.season_data:
                year = int(data.season.split('Q')[0].split('.')[0]) + 1911
                season = int(data.season.split('Q')[0].split('.')[1])
                season_ratio = SeasonFinancialRatio()
                season_ratio.surrogate_key = stock_symbol + '_' + str(year) + str(season).zfill(2)
                season_ratio.year = year
                season_ratio.season = season
                season_ratio.symbol = stock_symbol
                if data.gross_profit_margin != 'nil' and data.gross_profit_margin != 'N/A':
                    season_ratio.gross_profit_margin = Decimal(data.gross_profit_margin.replace(',',''))
                if data.operating_profit_margin != 'nil' and data.operating_profit_margin != 'N/A':
                    season_ratio.operating_profit_margin = Decimal(data.operating_profit_margin.replace(',', ''))
                if data.net_before_tax_profit_margin != 'nil' and data.net_before_tax_profit_margin != 'N/A':
                    season_ratio.net_before_tax_profit_margin = Decimal(data.net_before_tax_profit_margin.replace(',',''))
                if data.net_after_tax_profit_margin != 'nil' and data.net_after_tax_profit_margin != 'N/A':
                    season_ratio.net_after_tax_profit_margin = Decimal(data.net_after_tax_profit_margin.replace(',',''))
                if data.net_value_per_share != 'nil' and data.net_value_per_share != 'N/A':
                    season_ratio.net_value_per_share = Decimal(data.net_value_per_share.replace(',',''))
                if data.revenue_per_share != 'nil' and data.net_value_per_share != 'N/A':
                    season_ratio.revenue_per_share = Decimal(data.revenue_per_share.replace(',',''))
                if data.operating_profit_per_share != 'nil' and data.operating_profit_per_share != 'N/A':
                    season_ratio.operating_profit_per_share = Decimal(data.operating_profit_per_share.replace(',',''))
                if data.net_before_tax_profit_per_share != 'nil' and data.net_before_tax_profit_per_share != 'N/A':
                    season_ratio.net_before_tax_profit_per_share = Decimal(data.net_before_tax_profit_per_share.replace(',',''))
                if data.return_on_equity != 'nil' and data.return_on_equity != 'N/A':
                    season_ratio.return_on_equity = Decimal(data.return_on_equity.replace(',',''))
                if data.return_on_assets != 'nil' and data.return_on_assets != 'N/A':
                    season_ratio.return_on_assets = Decimal(data.return_on_assets.replace(',',''))
                if data.net_after_tax_profit_per_share != 'nil' and data.net_after_tax_profit_per_share != 'N/A':
                    season_ratio.net_after_tax_profit_per_share = Decimal(data.net_after_tax_profit_per_share.replace(',',''))
                if data.revenue_growth_rate != 'nil' and data.revenue_growth_rate != 'N/A':
                    season_ratio.revenue_growth_rate = Decimal(data.revenue_growth_rate.replace(',',''))
                if data.operating_profit_growth_rate != 'nil' and data.operating_profit_growth_rate != 'N/A':
                    season_ratio.operating_profit_growth_rate = Decimal(data.operating_profit_growth_rate.replace(',',''))
                if data.net_before_tax_profit_growth_rate != 'nil' and data.net_before_tax_profit_growth_rate != 'N/A':
                    season_ratio.net_before_tax_profit_growth_rate = Decimal(data.net_before_tax_profit_growth_rate.replace(',',''))
                if data.net_after_tax_profit_growth_rate != 'nil' and data.net_after_tax_profit_growth_rate != 'N/A':
                    season_ratio.net_after_tax_profit_growth_rate = Decimal(data.net_after_tax_profit_growth_rate.replace(',',''))
                if data.assets_growth_rate != 'nil' and data.assets_growth_rate != 'N/A':
                    season_ratio.assets_growth_rate = Decimal(data.assets_growth_rate.replace(',',''))
                if data.net_value_growth_rate != 'nil' and data.net_value_growth_rate != 'N/A':
                    season_ratio.net_value_growth_rate = Decimal(data.net_value_growth_rate.replace(',',''))
                if data.fixed_assets_growth_rate != 'nil' and data.fixed_assets_growth_rate != 'N/A':
                    season_ratio.fixed_assets_growth_rate = Decimal(data.fixed_assets_growth_rate.replace(',',''))
                if data.current_ratio != 'nil' and data.current_ratio != 'N/A':
                    season_ratio.current_ratio = Decimal(data.current_ratio.replace(',',''))
                if data.quick_ratio != 'nil' and data.quick_ratio != 'N/A':
                    season_ratio.quick_ratio = Decimal(data.quick_ratio.replace(',',''))
                if data.debt_ratio != 'nil' and data.debt_ratio != 'N/A':
                    season_ratio.debt_ratio = Decimal(data.debt_ratio.replace(',',''))
                if data.interest_cover != 'nil' and data.interest_cover != 'N/A':
                    season_ratio.interest_cover = Decimal(data.interest_cover.replace(',',''))
                if data.account_receivable_turnover_ratio != 'nil' and data.account_receivable_turnover_ratio != 'N/A':
                    season_ratio.account_receivable_turnover_ratio = Decimal(data.account_receivable_turnover_ratio.replace(',',''))
                if data.inventory_turnover_ratio != 'nil' and data.inventory_turnover_ratio != 'N/A':
                    season_ratio.inventory_turnover_ratio = Decimal(data.inventory_turnover_ratio.replace(',',''))
                if data.fixed_assets_turnover_ratio != 'nil' and data.fixed_assets_turnover_ratio != 'N/A':
                    season_ratio.fixed_assets_turnover_ratio = Decimal(data.fixed_assets_turnover_ratio.replace(',',''))
                if data.assets_turnover_ratio != 'nil' and data.assets_turnover_ratio != 'N/A':
                    season_ratio.assets_turnover_ratio = Decimal(data.assets_turnover_ratio.replace(',',''))
                if data.revenue_per_employee != 'nil' and data.revenue_per_employee != 'N/A':
                    season_ratio.revenue_per_employee = Decimal(data.revenue_per_employee.replace(',',''))
                if data.equity_turnover_ratio != 'nil' and data.equity_turnover_ratio != 'N/A':
                    season_ratio.equity_turnover_ratio = Decimal(data.equity_turnover_ratio.replace(',',''))
                if data.debt_equity_ratio != 'nil' and data.debt_equity_ratio != 'N/A':
                    season_ratio.debt_equity_ratio = Decimal(data.debt_equity_ratio.replace(',',''))
                if data.long_term_funds_to_fixed_assets != 'nil' and data.long_term_funds_to_fixed_assets != 'N/A':
                    season_ratio.long_term_funds_to_fixed_assets = Decimal(data.long_term_funds_to_fixed_assets.replace(',',''))
                season_ratio.save()
            """print season_ratio.surrogate_key + ' ' + data.gross_profit_margin + ' ' + data.operating_profit_margin + ' ' + \
                  data.net_before_tax_profit_margin + ' ' + data.net_after_tax_profit_margin + ' ' + \
                  data.net_value_per_share + ' ' + data.revenue_per_share + ' ' + data.operating_profit_per_share
            print data.net_before_tax_profit_per_share + ' ' + data.return_on_equity + ' ' + data.return_on_assets + ' ' + \
                  data.net_after_tax_profit_per_share + ' ' + data.revenue_growth_rate + ' ' + \
                  data.operating_profit_growth_rate + ' ' + data.net_before_tax_profit_growth_rate + ' ' + \
                  data.net_after_tax_profit_growth_rate + ' ' + data.assets_growth_rate
            print data.net_value_growth_rate + ' ' + data.fixed_assets_growth_rate + ' ' + data.current_ratio + ' ' + \
                  data.quick_ratio + ' ' + data.debt_ratio + ' ' + data.interest_cover + ' ' + \
                  data.account_receivable_turnover_ratio + ' ' + data.inventory_turnover_ratio + ' ' + \
                  data.fixed_assets_turnover_ratio + ' ' + data.assets_turnover_ratio
            print data.revenue_per_employee + ' ' + data.equity_turnover_ratio + ' ' + data.debt_equity_ratio + ' ' + \
                  data.long_term_funds_to_fixed_assets"""
            print ('update ' + stock_symbol + ' season financial ratio')
    return HttpResponse('update season financial ratio')

class ParseSeasonFinancialRatio(HTMLParser):
    def reset(self):
        HTMLParser.reset(self)
        self.season_info = False
        self.gross_profit_margin_info = False
        self.gross_profit_margin_data = False
        self.operating_profit_margin_info = False
        self.operating_profit_margin_data = False
        self.net_before_tax_profit_margin_info = False
        self.net_before_tax_profit_margin_data = False
        self.net_after_tax_profit_margin_info = False
        self.net_after_tax_profit_margin_data = False
        self.net_value_per_share_info = False
        self.net_value_per_share_data = False
        self.revenue_per_share_info = False
        self.revenue_per_share_data = False
        self.operating_profit_per_share_info = False
        self.operating_profit_per_share_data = False
        self.net_before_tax_profit_per_share_info = False
        self.net_before_tax_profit_per_share_data = False
        self.return_on_equity_info = False
        self.return_on_equity_data = False
        self.return_on_assets_info = False
        self.return_on_assets_data = False
        self.net_after_tax_profit_per_share_info = False
        self.net_after_tax_profit_per_share_data = False
        self.revenue_growth_rate_info = False
        self.revenue_growth_rate_data = False
        self.operating_profit_growth_rate_info = False
        self.operating_profit_growth_rate_data = False
        self.net_before_tax_profit_growth_rate_info = False
        self.net_before_tax_profit_growth_rate_data = False
        self.net_after_tax_profit_growth_rate_info = False
        self.net_after_tax_profit_growth_rate_data = False
        self.assets_growth_rate_info = False
        self.assets_growth_rate_data = False
        self.net_value_growth_rate_info = False
        self.net_value_growth_rate_data = False
        self.fixed_assets_growth_rate_info = False
        self.fixed_assets_growth_rate_data = False
        self.current_ratio_info = False
        self.current_ratio_data = False
        self.quick_ratio_info = False
        self.quick_ratio_data = False
        self.debt_ratio_info = False
        self.debt_ratio_data = False
        self.interest_cover_info = False
        self.interest_cover_data = False
        self.account_receivable_turnover_ratio_info = False
        self.account_receivable_turnover_ratio_data = False
        self.inventory_turnover_ratio_info = False
        self.inventory_turnover_ratio_data = False
        self.fixed_assets_turnover_ratio_info = False
        self.fixed_assets_turnover_ratio_data = False
        self.assets_turnover_ratio_info = False
        self.assets_turnover_ratio_data = False
        self.revenue_per_employee_info = False
        self.revenue_per_employee_data = False
        self.equity_turnover_ratio_info = False
        self.equity_turnover_ratio_data = False
        self.debt_equity_ratio_info = False
        self.debt_equity_ratio_data = False
        self.long_term_funds_to_fixed_assets_info = False
        self.long_term_funds_to_fixed_assets_data = False
        self.season_data = []
        self.cell = 0

    def handle_starttag(self, tag, attrs):
        if tag == 'td':
            if attrs[0][1] == 't2':
                self.season_info = True
            else:
                self.season_info = False
            if self.gross_profit_margin_info:
                if attrs[0][1] == 't3n1' or attrs[0][1] == 't3r1':
                    self.gross_profit_margin_data = True
            elif self.operating_profit_margin_info:
                if attrs[0][1] == 't3n1' or attrs[0][1] == 't3r1':
                    self.operating_profit_margin_data = True
            elif self.net_before_tax_profit_margin_info:
                if attrs[0][1] == 't3n1' or attrs[0][1] == 't3r1':
                    self.net_before_tax_profit_margin_data = True
            elif self.net_after_tax_profit_margin_info:
                if attrs[0][1] == 't3n1' or attrs[0][1] == 't3r1':
                    self.net_after_tax_profit_margin_data = True
            elif self.net_value_per_share_info:
                if attrs[0][1] == 't3n1' or attrs[0][1] == 't3r1':
                    self.net_value_per_share_data = True
            elif self.revenue_per_share_info:
                if attrs[0][1] == 't3n1' or attrs[0][1] == 't3r1':
                    self.revenue_per_share_data = True
            elif self.operating_profit_per_share_info:
                if attrs[0][1] == 't3n1' or attrs[0][1] == 't3r1':
                    self.operating_profit_per_share_data = True
            elif self.net_before_tax_profit_per_share_info:
                if attrs[0][1] == 't3n1' or attrs[0][1] == 't3r1':
                    self.net_before_tax_profit_per_share_data = True
            elif self.return_on_equity_info:
                if attrs[0][1] == 't3n1' or attrs[0][1] == 't3r1':
                    self.return_on_equity_data = True
            elif self.return_on_assets_info:
                if attrs[0][1] == 't3n1' or attrs[0][1] == 't3r1':
                    self.return_on_assets_data = True
            elif self.net_after_tax_profit_per_share_info:
                if attrs[0][1] == 't3n1' or attrs[0][1] == 't3r1':
                    self.net_after_tax_profit_per_share_data = True
            elif self.revenue_growth_rate_info:
                if attrs[0][1] == 't3n1' or attrs[0][1] == 't3r1':
                    self.revenue_growth_rate_data = True
            elif self.operating_profit_growth_rate_info:
                if attrs[0][1] == 't3n1' or attrs[0][1] == 't3r1':
                    self.operating_profit_growth_rate_data = True
            elif self.net_before_tax_profit_growth_rate_info:
                if attrs[0][1] == 't3n1' or attrs[0][1] == 't3r1':
                    self.net_before_tax_profit_growth_rate_data = True
            elif self.net_after_tax_profit_growth_rate_info:
                if attrs[0][1] == 't3n1' or attrs[0][1] == 't3r1':
                    self.net_after_tax_profit_growth_rate_data = True
            elif self.assets_growth_rate_info:
                if attrs[0][1] == 't3n1' or attrs[0][1] == 't3r1':
                    self.assets_growth_rate_data = True
            elif self.net_value_growth_rate_info:
                if attrs[0][1] == 't3n1' or attrs[0][1] == 't3r1':
                    self.net_value_growth_rate_data = True
            elif self.fixed_assets_growth_rate_info:
                if attrs[0][1] == 't3n1' or attrs[0][1] == 't3r1':
                    self.fixed_assets_growth_rate_data = True
            elif self.current_ratio_info:
                if attrs[0][1] == 't3n1' or attrs[0][1] == 't3r1':
                    self.current_ratio_data = True
            elif self.quick_ratio_info:
                if attrs[0][1] == 't3n1' or attrs[0][1] == 't3r1':
                    self.quick_ratio_data = True
            elif self.debt_ratio_info:
                if attrs[0][1] == 't3n1' or attrs[0][1] == 't3r1':
                    self.debt_ratio_data = True
            elif self.interest_cover_info:
                if attrs[0][1] == 't3n1' or attrs[0][1] == 't3r1':
                    self.interest_cover_data = True
            elif self.account_receivable_turnover_ratio_info:
                if attrs[0][1] == 't3n1' or attrs[0][1] == 't3r1':
                    self.account_receivable_turnover_ratio_data = True
            elif self.inventory_turnover_ratio_info:
                if attrs[0][1] == 't3n1' or attrs[0][1] == 't3r1':
                    self.inventory_turnover_ratio_data = True
            elif self.fixed_assets_turnover_ratio_info:
                if attrs[0][1] == 't3n1' or attrs[0][1] == 't3r1':
                    self.fixed_assets_turnover_ratio_data = True
            elif self.assets_turnover_ratio_info:
                if attrs[0][1] == 't3n1' or attrs[0][1] == 't3r1':
                    self.assets_turnover_ratio_data = True
            elif self.revenue_per_employee_info:
                if attrs[0][1] == 't3n1' or attrs[0][1] == 't3r1':
                    self.revenue_per_employee_data = True
            elif self.equity_turnover_ratio_info:
                if attrs[0][1] == 't3n1' or attrs[0][1] == 't3r1':
                    self.equity_turnover_ratio_data = True
            elif self.debt_equity_ratio_info:
                if attrs[0][1] == 't3n1' or attrs[0][1] == 't3r1':
                    self.debt_equity_ratio_data = True
            elif self.long_term_funds_to_fixed_assets_info:
                if attrs[0][1] == 't3n1' or attrs[0][1] == 't3r1':
                    self.long_term_funds_to_fixed_assets_data = True
        else:
            self.season_info = False

    def handle_endtag(self, tag):
        if tag == 'tr':
            self.season_info = False
            self.gross_profit_margin_info = False
            self.operating_profit_margin_info = False
            self.net_before_tax_profit_margin_info = False
            self.net_after_tax_profit_margin_info = False
            self.net_value_per_share_info = False
            self.revenue_per_share_info = False
            self.operating_profit_per_share_info = False
            self.net_before_tax_profit_per_share_info = False
            self.return_on_equity_info = False
            self.return_on_assets_info = False
            self.net_after_tax_profit_per_share_info = False
            self.revenue_growth_rate_info = False
            self.operating_profit_growth_rate_info = False
            self.net_before_tax_profit_growth_rate_info = False
            self.net_after_tax_profit_growth_rate_info = False
            self.assets_growth_rate_info = False
            self.net_value_growth_rate_info = False
            self.fixed_assets_growth_rate_info = False
            self.current_ratio_info = False
            self.quick_ratio_info = False
            self.debt_ratio_info = False
            self.interest_cover_info = False
            self.account_receivable_turnover_ratio_info = False
            self.inventory_turnover_ratio_info = False
            self.fixed_assets_turnover_ratio_info = False
            self.assets_turnover_ratio_info = False
            self.revenue_per_employee_info = False
            self.equity_turnover_ratio_info = False
            self.debt_equity_ratio_info = False
            self.long_term_funds_to_fixed_assets_info = False
            self.cell = 0

    def handle_data(self, text):
        if text.decode('cp950').encode('utf-8') == r'期別':
            self.season_info_start = True
            self.season_info = False
        elif text.decode('cp950').encode('utf-8') == r'營業毛利率':
            self.gross_profit_margin_info = True
        elif text.decode('cp950').encode('utf-8') == r'營業利益率':
            self.operating_profit_margin_info = True
        elif text.decode('cp950').encode('utf-8') == r'稅前淨利率':
            self.net_before_tax_profit_margin_info = True
        elif text.decode('cp950').encode('utf-8') == r'稅後淨利率':
            self.net_after_tax_profit_margin_info = True
        elif text.decode('cp950').encode('utf-8') == r'每股淨值(元)':
            self.net_value_per_share_info = True
        elif text.decode('cp950').encode('utf-8') == r'每股營業額(元)':
            self.revenue_per_share_info = True
        elif text.decode('cp950').encode('utf-8') == r'每股營業利益(元)':
            self.operating_profit_per_share_info = True
        elif text.decode('cp950').encode('utf-8') == r'每股稅前淨利(元)':
            self.net_before_tax_profit_per_share_info = True
        elif text.decode('cp950').encode('utf-8') == r'股東權益報酬率':
            self.return_on_equity_info = True
        elif text.decode('cp950').encode('utf-8') == r'資產報酬率':
            self.return_on_assets_info = True
        elif text.decode('cp950').encode('utf-8') == r'每股稅後淨利(元)':
            self.net_after_tax_profit_per_share_info = True
        elif text.decode('cp950').encode('utf-8') == r'營收成長率':
            self.revenue_growth_rate_info = True
        elif text.decode('cp950').encode('utf-8') == r'營業利益成長率':
            self.operating_profit_growth_rate_info = True
        elif text.decode('cp950').encode('utf-8') == r'稅前淨利成長率':
            self.net_before_tax_profit_growth_rate_info = True
        elif text.decode('cp950').encode('utf-8') == r'稅後淨利成長率':
            self.net_after_tax_profit_growth_rate_info = True
        elif text.decode('cp950').encode('utf-8') == r'總資產成長率':
            self.assets_growth_rate_info = True
        elif text.decode('cp950').encode('utf-8') == r'淨值成長率':
            self.net_value_growth_rate_info = True
        elif text.decode('cp950').encode('utf-8') == r'固定資產成長率':
            self.fixed_assets_growth_rate_info = True
        elif text.decode('cp950').encode('utf-8') == r'流動比率':
            self.current_ratio_info = True
        elif text.decode('cp950').encode('utf-8') == r'速動比率':
            self.quick_ratio_info = True
        elif text.decode('cp950').encode('utf-8') == r'負債比率':
            self.debt_ratio_info = True
        elif text.decode('cp950').encode('utf-8') == r'利息保障倍數':
            self.interest_cover_info = True
        elif text.decode('cp950').encode('utf-8') == r'應收帳款週轉率(次)':
            self.account_receivable_turnover_ratio_info = True
        elif text.decode('cp950').encode('utf-8') == r'存貨週轉率(次)':
            self.inventory_turnover_ratio_info = True
        elif text.decode('cp950').encode('utf-8') == r'固定資產週轉率(次)':
            self.fixed_assets_turnover_ratio_info = True
        elif text.decode('cp950').encode('utf-8') == r'總資產週轉率(次)':
            self.assets_turnover_ratio_info = True
        elif text.decode('cp950').encode('utf-8') == r'員工平均營業額(千元)':
            self.revenue_per_employee_info = True
        elif text.decode('cp950').encode('utf-8') == r'淨值週轉率':
            self.equity_turnover_ratio_info = True
        elif text.decode('cp950').encode('utf-8') == r'負債對淨值比率':
            self.debt_equity_ratio_info = True
        elif text.decode('cp950').encode('utf-8') == r'長期資金適合率':
            self.long_term_funds_to_fixed_assets_info = True
        elif self.season_info:
            ratio = Ratio()
            ratio.season = text
            self.season_data.append(ratio)
            self.season_info = False
        elif self.gross_profit_margin_data:
            ratio = self.season_data[self.cell]
            ratio.gross_profit_margin = text
            self.cell += 1
            self.cell %= len(self.season_data)
            self.gross_profit_margin_data = False
        elif self.operating_profit_margin_data:
            ratio = self.season_data[self.cell]
            ratio.operating_profit_margin = text
            self.cell += 1
            self.cell %= len(self.season_data)
            self.operating_profit_margin_data = False
        elif self.net_before_tax_profit_margin_data:
            ratio = self.season_data[self.cell]
            ratio.net_before_tax_profit_margin = text
            self.cell += 1
            self.cell %= len(self.season_data)
            self.net_before_tax_profit_margin_data = False
        elif self.net_after_tax_profit_margin_data:
            ratio = self.season_data[self.cell]
            ratio.net_after_tax_profit_margin = text
            self.cell += 1
            self.cell %= len(self.season_data)
            self.net_after_tax_profit_margin_data = False
        elif self.net_value_per_share_data:
            ratio = self.season_data[self.cell]
            ratio.net_value_per_share = text
            self.cell += 1
            self.cell %= len(self.season_data)
            self.net_value_per_share_data = False
        elif self.revenue_per_share_data:
            ratio = self.season_data[self.cell]
            ratio.revenue_per_share = text
            self.cell += 1
            self.cell %= len(self.season_data)
            self.revenue_per_share_data  = False
        elif self.operating_profit_per_share_data:
            ratio = self.season_data[self.cell]
            ratio.operating_profit_per_share = text
            self.cell += 1
            self.cell %= len(self.season_data)
            self.operating_profit_per_share_data = False
        elif self.net_before_tax_profit_per_share_data:
            ratio = self.season_data[self.cell]
            ratio.net_before_tax_profit_per_share = text
            self.cell += 1
            self.cell %= len(self.season_data)
            self.net_before_tax_profit_per_share_data = False
        elif self.return_on_equity_data:
            ratio = self.season_data[self.cell]
            ratio.return_on_equity = text
            self.cell += 1
            self.cell %= len(self.season_data)
            self.return_on_equity_data = False
        elif self.return_on_assets_data:
            ratio = self.season_data[self.cell]
            ratio.return_on_assets = text
            self.cell += 1
            self.cell %= len(self.season_data)
            self.return_on_assets_data = False
        elif self.net_after_tax_profit_per_share_data:
            ratio = self.season_data[self.cell]
            ratio.net_after_tax_profit_per_share = text
            self.cell += 1
            self.cell %= len(self.season_data)
            self.net_after_tax_profit_per_share_data = False
        elif self.revenue_growth_rate_data:
            ratio = self.season_data[self.cell]
            ratio.revenue_growth_rate = text
            self.cell += 1
            self.cell %= len(self.season_data)
            self.revenue_growth_rate_data = False
        elif self.operating_profit_growth_rate_data:
            ratio = self.season_data[self.cell]
            ratio.operating_profit_growth_rate = text
            self.cell += 1
            self.cell %= len(self.season_data)
            self.operating_profit_growth_rate_data = False
        elif self.net_before_tax_profit_growth_rate_data:
            ratio = self.season_data[self.cell]
            ratio.net_before_tax_profit_growth_rate = text
            self.cell += 1
            self.cell %= len(self.season_data)
            self.net_before_tax_profit_growth_rate_data = False
        elif self.net_after_tax_profit_growth_rate_data:
            ratio = self.season_data[self.cell]
            ratio.net_after_tax_profit_growth_rate = text
            self.cell += 1
            self.cell %= len(self.season_data)
            self.net_after_tax_profit_growth_rate_data = False
        elif self.assets_growth_rate_data:
            ratio = self.season_data[self.cell]
            ratio.assets_growth_rate = text
            self.cell += 1
            self.cell %= len(self.season_data)
            self.assets_growth_rate_data = False
        elif self.net_value_growth_rate_data:
            ratio = self.season_data[self.cell]
            ratio.net_value_growth_rate = text
            self.cell += 1
            self.cell %= len(self.season_data)
            self.net_value_growth_rate_data = False
        elif self.fixed_assets_growth_rate_data:
            ratio = self.season_data[self.cell]
            ratio.fixed_assets_growth_rate = text
            self.cell += 1
            self.cell %= len(self.season_data)
            self.fixed_assets_growth_rate_data = False
        elif self.current_ratio_data:
            ratio = self.season_data[self.cell]
            ratio.current_ratio = text
            self.cell += 1
            self.cell %= len(self.season_data)
            self.current_ratio_data = False
        elif self.quick_ratio_data:
            ratio = self.season_data[self.cell]
            ratio.quick_ratio = text
            self.cell += 1
            self.cell %= len(self.season_data)
            self.quick_ratio_data = False
        elif self.debt_ratio_data:
            ratio = self.season_data[self.cell]
            ratio.debt_ratio = text
            self.cell += 1
            self.cell %= len(self.season_data)
            self.debt_ratio_data = False
        elif self.interest_cover_data:
            ratio = self.season_data[self.cell]
            ratio.interest_cover = text
            self.cell += 1
            self.cell %= len(self.season_data)
            self.interest_cover_data = False
        elif self.account_receivable_turnover_ratio_data:
            ratio = self.season_data[self.cell]
            ratio.account_receivable_turnover_ratio = text
            self.cell += 1
            self.cell %= len(self.season_data)
            self.account_receivable_turnover_ratio_data = False
        elif self.inventory_turnover_ratio_data:
            ratio = self.season_data[self.cell]
            ratio.inventory_turnover_ratio = text
            self.cell += 1
            self.cell %= len(self.season_data)
            self.inventory_turnover_ratio_data = False
        elif self.fixed_assets_turnover_ratio_data:
            ratio = self.season_data[self.cell]
            ratio.fixed_assets_turnover_ratio = text
            self.cell += 1
            self.cell %= len(self.season_data)
            self.fixed_assets_turnover_ratio_data = False
        elif self.assets_turnover_ratio_data:
            ratio = self.season_data[self.cell]
            ratio.assets_turnover_ratio = text
            self.cell += 1
            self.cell %= len(self.season_data)
            self.assets_turnover_ratio_data = False
        elif self.revenue_per_employee_data:
            ratio = self.season_data[self.cell]
            ratio.revenue_per_employee = text
            self.cell += 1
            self.cell %= len(self.season_data)
            self.revenue_per_employee_data = False
        elif self.equity_turnover_ratio_data:
            ratio = self.season_data[self.cell]
            ratio.equity_turnover_ratio = text
            self.cell += 1
            self.cell %= len(self.season_data)
            self.equity_turnover_ratio_data = False
        elif self.debt_equity_ratio_data:
            ratio = self.season_data[self.cell]
            ratio.debt_equity_ratio = text
            self.cell += 1
            self.cell %= len(self.season_data)
            self.debt_equity_ratio_data = False
        elif self.long_term_funds_to_fixed_assets_data:
            ratio = self.season_data[self.cell]
            ratio.long_term_funds_to_fixed_assets = text
            self.cell += 1
            self.cell %= len(self.season_data)
            self.long_term_funds_to_fixed_assets_data = False
            
class Ratio:
    def __init__(self):
        self.season = ''
        self.gross_profit_margin = ''
        self.operating_profit_margin = ''
        self.net_before_tax_profit_margin = '' 
        self.net_after_tax_profit_margin = ''
        self.net_value_per_share = ''
        self.revenue_per_share = ''
        self.operating_profit_per_share = ''
        self.net_before_tax_profit_per_share = ''
        self.return_on_equity = ''
        self.return_on_assets = ''
        self.net_after_tax_profit_per_share = ''
        self.revenue_growth_rate = ''
        self.operating_profit_growth_rate = ''
        self.net_before_tax_profit_growth_rate = ''
        self.net_after_tax_profit_growth_rate = ''
        self.assets_growth_rate = ''
        self.net_value_growth_rate = ''
        self.fixed_assets_growth_rate = ''
        self.current_ratio = ''
        self.quick_ratio = ''
        self.debt_ratio = ''
        self.interest_cover = ''
        self.account_receivable_turnover_ratio = ''
        self.inventory_turnover_ratio = ''
        self.fixed_assets_turnover_ratio = ''
        self.assets_turnover_ratio = ''
        self.revenue_per_employee = ''
        self.equity_turnover_ratio = ''
        self.debt_equity_ratio = ''
        self.long_term_funds_to_fixed_assets = ''
