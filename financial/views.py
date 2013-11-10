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

#綜合損益表
def update_season_income_statement(request):
    stock_ids = StockId.objects.all()
    for stock_id in stock_ids:
        stock_symbol = stock_id.symbol
        year = 102
        season = 3
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
            
            has_data = soup.find_all('font', {'color': 'red'})
            if has_data:
                print stock_symbol + ' not updated'
                continue
            season_income_datas = soup.find_all("td", {'style' : 'text-align:left;white-space:nowrap;'})
            income_statement = SeasonIncomeStatement()
            income_statement.symbol = stock_symbol
            income_statement.year = str(1911+year)
            income_statement.season = season
            income_statement.surrogate_key = stock_symbol + '_' + str(1911+year) + str(season).zfill(2)

            if season == 1:
                income_statement.date = datetime.date(1911+year, 1, 1)
            elif season == 2:
                income_statement.date = datetime.date(1911+year, 4, 1)
            elif season == 3:
                income_statement.date = datetime.date(1911+year, 7, 1)
            elif season == 4:
                income_statement.date = datetime.date(1911+year, 10, 1)

            last_income_statement = SeasonIncomeStatement()
            last_income_statement.symbol = stock_symbol
            last_income_statement.year = str(1910+year)
            last_income_statement.season = season

            if season == 1:
                last_income_statement.date = datetime.date(1910+year, 1, 1)
            elif season == 2:
                last_income_statement.date = datetime.date(1910+year, 4, 1)
            elif season == 3:
                last_income_statement.date = datetime.date(1910+year, 7, 1)
            elif season == 4:
                last_income_statement.date = datetime.date(1910+year, 10, 1)
            
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
            print Decimal(next_data.string.strip().replace(',',''))
            next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
            print Decimal(next_data.string.strip().replace(',',''))
    req = urllib2.Request(url, url_data)
    response = urllib2.urlopen(req)
    return HttpResponse(response.read())

def update_season_balance_sheet(request):
    stock_ids = StockId.objects.all()
    for stock_id in stock_ids:
        stock_symbol = stock_id.symbol
        year = 102
        season = 3
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
            has_data = soup.find_all('font', {'color': 'red'})
            if has_data:
                print stock_symbol + ' not updated'
                continue
            balance_sheet_datas = soup.find_all("td", {'style' : 'text-align:left;white-space:nowrap;'})
            balance_sheet = SeasonBalanceSheet()
            balance_sheet.symbol = stock_symbol
            balance_sheet.year = str(1911+year)
            balance_sheet.season = season
            if season == 1:
                balance_sheet.date = datetime.date(1911+year, 1, 1)
            elif season == 2:
                balance_sheet.date = datetime.date(1911+year, 4, 1)
            elif season == 3:
                balance_sheet.date = datetime.date(1911+year, 7, 1)
            elif season == 4:
                balance_sheet.date = datetime.date(1911+year, 10, 1)
            balance_sheet.surrogate_key = stock_symbol + '_' + str(1911+year) + str(season).zfill(2)

            last_balance_sheet = SeasonBalanceSheet()
            last_balance_sheet.symbol = stock_symbol
            last_balance_sheet.year = str(1910+year)
            last_balance_sheet.season = season

            if season == 1:
                last_balance_sheet.date = datetime.date(1910+year, 1, 1)
            elif season == 2:
                last_balance_sheet.date = datetime.date(1910+year, 4, 1)
            elif season == 3:
                last_balance_sheet.date = datetime.date(1910+year, 7, 1)
            elif season == 4:
                last_balance_sheet.date = datetime.date(1910+year, 10, 1)
            last_balance_sheet.surrogate_key = stock_symbol + '_' + str(1910+year) + str(season).zfill(2)

            for data in balance_sheet_datas:
                if r'現金及約當現金' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.cash_and_cash_equivalents = Decimal(next_data.string.strip().replace(',',''))
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_balance_sheet.cash_and_cash_equivalents = Decimal(next_data.string.strip().replace(',',''))
                elif r'透過損益按公允價值衡量之金融資產－流動' in data.string.encode('utf-8') or r'備供出售金融資產－流動淨額' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.current_financial_assets = Decimal(next_data.string.strip().replace(',',''))
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_balance_sheet.current_financial_assets = Decimal(next_data.string.strip().replace(',',''))
                elif r'應收票據淨額' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.notes_receivable = Decimal(next_data.string.strip().replace(',',''))
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_balance_sheet.notes_receivable = Decimal(next_data.string.strip().replace(',',''))
                elif r'應收帳款淨額' in data.string.encode('utf-8') or r'應收款項淨額' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.accounts_receivable = Decimal(next_data.string.strip().replace(',',''))
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_balance_sheet.accounts_receivable = Decimal(next_data.string.strip().replace(',',''))
                elif r'存貨' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.inventories = Decimal(next_data.string.strip().replace(',',''))
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_balance_sheet.inventories = Decimal(next_data.string.strip().replace(',',''))
                elif r'預付款項' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.prepayments = Decimal(next_data.string.strip().replace(',',''))
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_balance_sheet.prepayments = Decimal(next_data.string.strip().replace(',',''))
                elif r'其他流動資產' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.other_current_assets = Decimal(next_data.string.strip().replace(',',''))
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_balance_sheet.other_current_assets = Decimal(next_data.string.strip().replace(',',''))
                elif r'流動資產合計' in data.string.encode('utf-8') and r'非' not in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.total_current_assets = Decimal(next_data.string.strip().replace(',',''))
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_balance_sheet.total_current_assets = Decimal(next_data.string.strip().replace(',',''))
                elif r'備供出售金融資產－非流動淨額' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.non_current_available_for_sale_financial_assets = Decimal(next_data.string.strip().replace(',',''))
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_balance_sheet.non_current_available_for_sale_financial_assets = Decimal(next_data.string.strip().replace(',',''))
                elif r'不動產、廠房及設備' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.property_plant_and_equipment = Decimal(next_data.string.strip().replace(',',''))
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_balance_sheet.property_plant_and_equipment = Decimal(next_data.string.strip().replace(',',''))
                elif r'投資性不動產淨額' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.investment_property = Decimal(next_data.string.strip().replace(',',''))
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_balance_sheet.investment_property = Decimal(next_data.string.strip().replace(',',''))
                elif r'無形資產' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    if data.next_sibling.next_sibling.string is not None:
                        next_data = data.next_sibling.next_sibling
                        balance_sheet.intangible_assets = Decimal(next_data.string.strip().replace(',',''))
                        next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                        last_balance_sheet.intangible_assets = Decimal(next_data.string.strip().replace(',',''))
                elif r'遞延所得稅資產' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.deferred_tax_assets = Decimal(next_data.string.strip().replace(',',''))
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_balance_sheet.deferred_tax_assets = Decimal(next_data.string.strip().replace(',',''))
                elif r'其他非流動資產' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.other_non_current_assets = Decimal(next_data.string.strip().replace(',',''))
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_balance_sheet.other_non_current_assets = Decimal(next_data.string.strip().replace(',',''))
                elif r'非流動資產合計' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.total_non_current_assets = Decimal(next_data.string.strip().replace(',',''))
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_balance_sheet.total_non_current_assets = Decimal(next_data.string.strip().replace(',',''))
                elif r'資產總額' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.total_assets = Decimal(next_data.string.strip().replace(',',''))
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_balance_sheet.total_assets = Decimal(next_data.string.strip().replace(',',''))
                elif r'短期借款' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.short_term_borrowings = Decimal(next_data.string.strip().replace(',',''))
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_balance_sheet.short_term_borrowings = Decimal(next_data.string.strip().replace(',',''))
                elif r'透過損益按公允價值衡量之金融負債－流動' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.current_financial_liabilities = Decimal(next_data.string.strip().replace(',',''))
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_balance_sheet.current_financial_liabilities = Decimal(next_data.string.strip().replace(',',''))
                elif r'應付票據' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.notes_payable = Decimal(next_data.string.strip().replace(',',''))
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_balance_sheet.notes_payable = Decimal(next_data.string.strip().replace(',',''))
                elif r'應付帳款' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.accounts_payable = Decimal(next_data.string.strip().replace(',',''))
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_balance_sheet.accounts_payable = Decimal(next_data.string.strip().replace(',',''))
                elif r'其他應付款' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.other_payables = Decimal(next_data.string.strip().replace(',',''))
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_balance_sheet.other_payables = Decimal(next_data.string.strip().replace(',',''))
                elif r'當期所得稅負債' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.current_tax_liabilities = Decimal(next_data.string.strip().replace(',',''))
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_balance_sheet.current_tax_liabilities = Decimal(next_data.string.strip().replace(',',''))
                elif r'負債準備－流動' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.current_provisions = Decimal(next_data.string.strip().replace(',',''))
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_balance_sheet.current_provisions = Decimal(next_data.string.strip().replace(',',''))
                elif r'其他流動負債' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.other_current_liabilities = Decimal(next_data.string.strip().replace(',',''))
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_balance_sheet.other_current_liabilities = Decimal(next_data.string.strip().replace(',',''))
                elif r'流動負債合計' in data.string.encode('utf-8') and r'非' not in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.total_current_liabilities = Decimal(next_data.string.strip().replace(',',''))
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_balance_sheet.total_current_liabilities = Decimal(next_data.string.strip().replace(',',''))
                elif r'遞延所得稅負債' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.deferred_tax_liabilities = Decimal(next_data.string.strip().replace(',',''))
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_balance_sheet.deferred_tax_liabilities = Decimal(next_data.string.strip().replace(',',''))
                elif r'其他非流動負債' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.other_non_current_liabilities = Decimal(next_data.string.strip().replace(',',''))
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_balance_sheet.other_non_current_liabilities = Decimal(next_data.string.strip().replace(',',''))
                elif r'非流動負債合計' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.total_non_current_liabilities = Decimal(next_data.string.strip().replace(',',''))
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_balance_sheet.total_non_current_liabilities = Decimal(next_data.string.strip().replace(',',''))
                elif r'負債總額' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.total_liabilities = Decimal(next_data.string.strip().replace(',',''))
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_balance_sheet.total_liabilities = Decimal(next_data.string.strip().replace(',',''))
                elif r'普通股股本' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.ordinary_share = Decimal(next_data.string.strip().replace(',',''))
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_balance_sheet.ordinary_share = Decimal(next_data.string.strip().replace(',',''))
                elif r'股本合計' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.total_capital_stock = Decimal(next_data.string.strip().replace(',',''))
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_balance_sheet.total_capital_stock = Decimal(next_data.string.strip().replace(',',''))
                elif r'資本公積－發行溢價' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.additional_paid_in_capital = Decimal(next_data.string.strip().replace(',',''))
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_balance_sheet.additional_paid_in_capital = Decimal(next_data.string.strip().replace(',',''))
                elif r'資本公積－庫藏股票交易' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.treasury_share_transactions = Decimal(next_data.string.strip().replace(',',''))
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_balance_sheet.treasury_share_transactions = Decimal(next_data.string.strip().replace(',',''))
                elif r'資本公積－合併溢額' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.net_assets_from_merger = Decimal(next_data.string.strip().replace(',',''))
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_balance_sheet.net_assets_from_merger = Decimal(next_data.string.strip().replace(',',''))
                elif r'資本公積合計' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.total_capital_surplus = Decimal(next_data.string.strip().replace(',',''))
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_balance_sheet.total_capital_surplus = Decimal(next_data.string.strip().replace(',',''))
                elif r'法定盈餘公積' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.legal_reserve = Decimal(next_data.string.strip().replace(',',''))
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_balance_sheet.legal_reserve = Decimal(next_data.string.strip().replace(',',''))
                elif r'特別盈餘公積' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.special_reserve = Decimal(next_data.string.strip().replace(',',''))
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_balance_sheet.special_reserve = Decimal(next_data.string.strip().replace(',',''))
                elif r'未分配盈餘（或待彌補虧損）' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.unappropriated_retained_earnings = Decimal(next_data.string.strip().replace(',',''))
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_balance_sheet.unappropriated_retained_earnings = Decimal(next_data.string.strip().replace(',',''))
                elif r'保留盈餘合計' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.retained_earnings = Decimal(next_data.string.strip().replace(',',''))
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_balance_sheet.retained_earnings = Decimal(next_data.string.strip().replace(',',''))
                elif r'國外營運機構財務報表換算之兌換差額' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.exchange_differences_of_foreign_financial_statements = Decimal(next_data.string.strip().replace(',',''))
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_balance_sheet.exchange_differences_of_foreign_financial_statements = Decimal(next_data.string.strip().replace(',',''))
                elif r'備供出售金融資產未實現損益' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.unrealised_gains_for_sale_financial_assets = Decimal(next_data.string.strip().replace(',',''))
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_balance_sheet.unrealised_gains_for_sale_financial_assets = Decimal(next_data.string.strip().replace(',',''))
                elif r'其他權益合計' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.other_equity_interest = Decimal(next_data.string.strip().replace(',',''))
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_balance_sheet.other_equity_interest = Decimal(next_data.string.strip().replace(',',''))
                elif r'歸屬於母公司業主之權益合計' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.equity_attributable_to_owners_of_parent = Decimal(next_data.string.strip().replace(',',''))
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_balance_sheet.equity_attributable_to_owners_of_parent = Decimal(next_data.string.strip().replace(',',''))
                elif r'非控制權益' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.non_controlling_interests = Decimal(next_data.string.strip().replace(',',''))
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_balance_sheet.non_controlling_interests = Decimal(next_data.string.strip().replace(',',''))
                elif r'權益總額' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.total_equity = Decimal(next_data.string.strip().replace(',',''))
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_balance_sheet.total_equity = Decimal(next_data.string.strip().replace(',',''))
                elif r'預收股款（權益項下）之約當發行股數（單位：股）' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.equivalent_issue_shares_of_advance_receipts = Decimal(next_data.string.strip().replace(',',''))
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_balance_sheet.equivalent_issue_shares_of_advance_receipts = Decimal(next_data.string.strip().replace(',',''))
                elif r'母公司暨子公司所持有之母公司庫藏股股數（單位：股）' in data.string.encode('utf-8'):
                    next_data = data.next_sibling.next_sibling
                    balance_sheet.number_of_shares_in_entity_held_by_entity = Decimal(next_data.string.strip().replace(',',''))
                    next_data = next_data.next_sibling.next_sibling.next_sibling.next_sibling
                    last_balance_sheet.number_of_shares_in_entity_held_by_entity = Decimal(next_data.string.strip().replace(',',''))
            if balance_sheet.cash_and_cash_equivalents:
                balance_sheet.save()
                last_balance_sheet.save()
            else:
                print stock_symbol + ' time sleep'
                time.sleep(30)

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
                year_ratio.symbol = stock_symbol
                arrRatioDatas.append(year_ratio)
            if stage_data.string.encode('utf-8') == r'期別':
                isDataStart = True
        ratio_datas = soup.find_all('td', {'class':'t4t1'})
        for ratio_data in ratio_datas:
            next = ratio_data.next_sibling.next_sibling
            if ratio_data.string.encode('utf-8') == r'營業毛利率':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.gross_profit_margin = Decimal(next.string.replace(',',''))
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'營業利益率':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.operating_profit_margin = Decimal(next.string.replace(',',''))
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'稅前淨利率':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.net_before_tax_profit_margin = Decimal(next.string.replace(',',''))
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'稅後淨利率':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.net_after_tax_profit_margin = Decimal(next.string.replace(',',''))
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'每股淨值(元)':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.net_value_per_share = Decimal(next.string.replace(',',''))
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'每股營業額(元)':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.revenue_per_share = Decimal(next.string.replace(',',''))
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'每股營業利益(元)':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.operating_profit_per_share = Decimal(next.string.replace(',',''))
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'每股稅前淨利(元)':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.net_before_tax_profit_per_share = Decimal(next.string.replace(',',''))
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'股東權益報酬率':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.return_on_equity = Decimal(next.string.replace(',',''))
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'資產報酬率':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.return_on_assets = Decimal(next.string.replace(',',''))
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'每股稅後淨利(元)':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.net_after_tax_profit_per_share = Decimal(next.string.replace(',',''))
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'營收成長率':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.revenue_growth_rate = Decimal(next.string.replace(',',''))
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'營業利益成長率':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.operating_profit_growth_rate = Decimal(next.string.replace(',',''))
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'稅前淨利成長率':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.net_before_tax_profit_growth_rate = Decimal(next.string.replace(',',''))
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'稅後淨利成長率':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.net_after_tax_profit_growth_rate = Decimal(next.string.replace(',',''))
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'總資產成長率':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.assets_growth_rate = Decimal(next.string.replace(',',''))
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'淨值成長率':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.net_value_growth_rate = Decimal(next.string.replace(',',''))
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'固定資產成長率':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.fixed_assets_growth_rate = Decimal(next.string.replace(',',''))
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'流動比率':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.current_ratio = Decimal(next.string.replace(',',''))
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'速動比率':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.quick_ratio = Decimal(next.string.replace(',',''))
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'負債比率':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.debt_ratio = Decimal(next.string.replace(',',''))
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'利息保障倍數':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.interest_cover = Decimal(next.string.replace(',',''))
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'應收帳款週轉率(次)':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.account_receivable_turnover_ratio = Decimal(next.string.replace(',',''))
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'存貨週轉率(次)':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.inventory_turnover_ratio = Decimal(next.string.replace(',',''))
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'固定資產週轉率(次)':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.fixed_assets_turnover_ratio = Decimal(next.string.replace(',',''))
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'總資產週轉率(次)':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.assets_turnover_ratio = Decimal(next.string.replace(',',''))
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'員工平均營業額(千元)':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.revenue_per_employee = Decimal(next.string.replace(',',''))
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'淨值週轉率':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.equity_turnover_ratio = Decimal(next.string.replace(',',''))
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'負債對淨值比率':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.debt_equity_ratio = Decimal(next.string.replace(',',''))
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'長期資金適合率':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.long_term_funds_to_fixed_assets = Decimal(next.string.replace(',',''))
                    next = next.next_sibling.next_sibling
        for ratio in arrRatioDatas:
            ratio.save()
        print ('update ' + stock_symbol + ' season financial ratio')

    return HttpResponse('update year financial ratio')

def update_season_financial_ratio(request):
    stock_ids = StockId.objects.all()
    today = datetime.date.today()
    for stock_id in stock_ids:
        stock_symbol = stock_id.symbol
        (last_season_year, last_season_season) = last_season(today)
        ratioInDb = SeasonFinancialRatio.objects.filter(symbol=stock_symbol, year=last_season_year, season=last_season_season-1)
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
                        ratio.gross_profit_margin = Decimal(next.string.replace(',',''))
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'營業利益率':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.operating_profit_margin = Decimal(next.string.replace(',',''))
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'稅前淨利率':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.net_before_tax_profit_margin = Decimal(next.string.replace(',',''))
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'稅後淨利率':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.net_after_tax_profit_margin = Decimal(next.string.replace(',',''))
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'每股淨值(元)':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.net_value_per_share = Decimal(next.string.replace(',',''))
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'每股營業額(元)':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.revenue_per_share = Decimal(next.string.replace(',',''))
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'每股營業利益(元)':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.operating_profit_per_share = Decimal(next.string.replace(',',''))
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'每股稅前淨利(元)':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.net_before_tax_profit_per_share = Decimal(next.string.replace(',',''))
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'股東權益報酬率':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.return_on_equity = Decimal(next.string.replace(',',''))
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'資產報酬率':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.return_on_assets = Decimal(next.string.replace(',',''))
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'每股稅後淨利(元)':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.net_after_tax_profit_per_share = Decimal(next.string.replace(',',''))
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'營收成長率':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.revenue_growth_rate = Decimal(next.string.replace(',',''))
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'營業利益成長率':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.operating_profit_growth_rate = Decimal(next.string.replace(',',''))
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'稅前淨利成長率':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.net_before_tax_profit_growth_rate = Decimal(next.string.replace(',',''))
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'稅後淨利成長率':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.net_after_tax_profit_growth_rate = Decimal(next.string.replace(',',''))
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'總資產成長率':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.assets_growth_rate = Decimal(next.string.replace(',',''))
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'淨值成長率':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.net_value_growth_rate = Decimal(next.string.replace(',',''))
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'固定資產成長率':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.fixed_assets_growth_rate = Decimal(next.string.replace(',',''))
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'流動比率':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.current_ratio = Decimal(next.string.replace(',',''))
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'速動比率':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.quick_ratio = Decimal(next.string.replace(',',''))
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'負債比率':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.debt_ratio = Decimal(next.string.replace(',',''))
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'利息保障倍數':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.interest_cover = Decimal(next.string.replace(',',''))
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'應收帳款週轉率(次)':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.account_receivable_turnover_ratio = Decimal(next.string.replace(',',''))
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'存貨週轉率(次)':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.inventory_turnover_ratio = Decimal(next.string.replace(',',''))
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'固定資產週轉率(次)':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.fixed_assets_turnover_ratio = Decimal(next.string.replace(',',''))
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'總資產週轉率(次)':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.assets_turnover_ratio = Decimal(next.string.replace(',',''))
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'員工平均營業額(千元)':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.revenue_per_employee = Decimal(next.string.replace(',',''))
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'淨值週轉率':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.equity_turnover_ratio = Decimal(next.string.replace(',',''))
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'負債對淨值比率':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.debt_equity_ratio = Decimal(next.string.replace(',',''))
                    next = next.next_sibling.next_sibling
            elif ratio_data.string.encode('utf-8') == r'長期資金適合率':
                for ratio in arrRatioDatas:
                    if next.string != 'nil' and next.string != 'N/A':
                        ratio.long_term_funds_to_fixed_assets = Decimal(next.string.replace(',',''))
                    next = next.next_sibling.next_sibling
        for ratio in arrRatioDatas:
            ratio.save()
        print ('update ' + stock_symbol + ' season financial ratio')

    return HttpResponse('update season financial ratio')

def last_season(day):
    year = day.year
    month = day.month
    if month <= 3:
        season = 4
        year -= 1
    elif month >= 4 and month <= 6:
        season = 1
    elif month >= 7 and month <= 9:
        season = 2
    elif month >= 10:
        season = 3
    return year, season
