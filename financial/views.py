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


#income statement from TWSE
def update_season_income_statement(request):
    stock_ids = StockId.objects.all()
    for stock_id in stock_ids:
        stock_symbol = stock_id.symbol
        year = 102
        season = 2

        if not SeasonIncomeStatement.objects.filter(symbol=stock_symbol, year=year+1911, season=season):

            url = 'http://mops.twse.com.tw/mops/web/ajax_t164sb04'
            values = {'encodeURIComponent' : '1', 'step' : '1', 'firstin' : '1', 'off' : '1',
            'keyword4' : '','code1' : '','TYPEK2' : '','checkbtn' : '',
            'queryName':'co_id', 'TYPEK':'all', 'isnew':'false', 'co_id' : stock_symbol, 'year' : year, 'season' : str(season).zfill(2) }
            url_data = urllib.urlencode(values) 

            req = urllib2.Request(url, url_data)
            response = urllib2.urlopen(req) 

            soup = BeautifulSoup(response,from_encoding="utf-8")
            season_income_datas = soup.find_all("td", {'style' : 'text-align:left;white-space:nowrap;'})    

            income_statement = SeasonIncomeStatement()
            income_statement.symbol = stock_symbol
            income_statement.year = str(1911+year)
            income_statement.season = season
            income_statement.surrogate_key = stock_symbol + '_' + str(year) + str(season).zfill(2)
            for data in season_income_datas:
                if '營業收入合計' in data.string.encode('utf-8'):
                    income_statement.operating_revenue = Decimal(data.next_sibling.next_sibling.string.strip().replace(',',''))
                elif '營業成本合計' in data.string.encode('utf-8'):
                    income_statement.operating_cost = Decimal(data.next_sibling.next_sibling.string.strip().replace(',',''))
                elif '營業毛利（毛損）' in data.string.encode('utf-8'):
                    income_statement.gross_profit_from_operations = Decimal(data.next_sibling.next_sibling.string.strip().replace(',',''))
                elif '推銷費用' in data.string.encode('utf-8'):
                    income_statement.selling_expenses = Decimal(data.next_sibling.next_sibling.string.strip().replace(',',''))
                elif '管理費用' in data.string.encode('utf-8'):
                    income_statement.administrative_expenses = Decimal(data.next_sibling.next_sibling.string.strip().replace(',',''))
                elif '研究發展費用' in data.string.encode('utf-8'):
                    income_statement.research_and_development_expenses = Decimal(data.next_sibling.next_sibling.string.strip().replace(',',''))
                elif '營業費用合計' in data.string.encode('utf-8'):
                    income_statement.operating_expenses = Decimal(data.next_sibling.next_sibling.string.strip().replace(',',''))
                elif '營業利益（損失）' in data.string.encode('utf-8'):
                    income_statement.net_operating_income = Decimal(data.next_sibling.next_sibling.string.strip().replace(',',''))
                elif '其他收入' in data.string.encode('utf-8'):
                    income_statement.other_income = Decimal(data.next_sibling.next_sibling.string.strip().replace(',',''))
                elif '其他利益及損失淨額' in data.string.encode('utf-8'):
                    income_statement.other_gains_and_losses = Decimal(data.next_sibling.next_sibling.string.strip().replace(',',''))
                elif r'財務成本淨額' in data.string.encode('utf-8'):
                    income_statement.finance_costs = Decimal(data.next_sibling.next_sibling.string.strip().replace(',',''))
                elif r'營業外收入及支出合計' in data.string.encode('utf-8'):
                    income_statement.non_operating_income_and_expenses = Decimal(data.next_sibling.next_sibling.string.strip().replace(',',''))
                elif r'稅前淨利（淨損）' in data.string.encode('utf-8'):
                    income_statement.profit_from_continuing_operations_before_tax = Decimal(data.next_sibling.next_sibling.string.strip().replace(',',''))
                elif r'所得稅費用（利益）合計' in data.string.encode('utf-8'):
                    income_statement.tax_expense = Decimal(data.next_sibling.next_sibling.string.strip().replace(',',''))
                elif r'繼續營業單位本期淨利（淨損）' in data.string.encode('utf-8'):
                    income_statement.profit_from_continuing_operations = Decimal(data.next_sibling.next_sibling.string.strip().replace(',',''))
                elif r'本期淨利（淨損）' in data.string.encode('utf-8'):
                    income_statement.profit = Decimal(data.next_sibling.next_sibling.string.strip().replace(',',''))
                elif r'國外營運機構財務報表換算之兌換差額' in data.string.encode('utf-8'):
                    income_statement.exchange_differences_on_translation = Decimal(data.next_sibling.next_sibling.string.strip().replace(',',''))
                elif r'備供出售金融資產未實現評價損益' in data.string.encode('utf-8'):
                    income_statement.unrealised_gains_for_sale_financial_assets = Decimal(data.next_sibling.next_sibling.string.strip().replace(',',''))
                elif r'與其他綜合損益組成部分相關之所得稅' in data.string.encode('utf-8'):
                    income_statement.income_tax_of_other_comprehensive_income = Decimal(data.next_sibling.next_sibling.string.strip().replace(',',''))
                elif r'其他綜合損益（淨額）' in data.string.encode('utf-8'):
                    income_statement.other_comprehensive_income = Decimal(data.next_sibling.next_sibling.string.strip().replace(',',''))
                elif r'本期綜合損益總額' in data.string.encode('utf-8'):
                    income_statement.total_comprehensive_income = Decimal(data.next_sibling.next_sibling.string.strip().replace(',',''))
                elif r'母公司業主（淨利／損）' in data.string.encode('utf-8'):
                    income_statement.profit_to_owners_of_parent = Decimal(data.next_sibling.next_sibling.string.strip().replace(',',''))
                elif r'非控制權益（淨利／損）' in data.string.encode('utf-8'):
                    income_statement.profit_to_non_controlling_interests = Decimal(data.next_sibling.next_sibling.string.strip().replace(',',''))
                elif r'母公司業主（綜合損益）' in data.string.encode('utf-8'):
                    income_statement.comprehensive_income_to_owners_of_parent = Decimal(data.next_sibling.next_sibling.string.strip().replace(',',''))
                elif r'非控制權益（綜合損益）' in data.string.encode('utf-8'):
                    income_statement.comprehensive_income_to_non_controlling_interests = Decimal(data.next_sibling.next_sibling.string.strip().replace(',',''))
                elif r'基本每股盈餘' in data.string.encode('utf-8'):
                    if data.next_sibling.next_sibling.string is not None:
                        income_statement.basic_earnings_per_share = Decimal(data.next_sibling.next_sibling.string.strip().replace(',',''))
                elif r'稀釋每股盈餘' in data.string.encode('utf-8'):
                    if data.next_sibling.next_sibling.string is not None:
                        income_statement.diluted_earnings_per_share = Decimal(data.next_sibling.next_sibling.string.strip().replace(',',''))    

            income_statement.save()
            print stock_symbol + ' data updated'

    return HttpResponse("update_season_income_statement")

#資產負債表
def update_season_balance_sheet(request):
    stock_symbol = '1537'
    year = 102
    season = 2
    url = 'http://mops.twse.com.tw/mops/web/t164sb03'
    values = {'encodeURIComponent' : '1', 'step' : '1', 'firstin' : '1', 'off' : '1',
            'keyword4' : '','code1' : '','TYPEK2' : '','checkbtn' : '',
            'queryName':'co_id', 'TYPEK':'all', 'isnew':'true', 'co_id' : stock_symbol, 'year' : year, 'season' : str(season).zfill(2) }
    url_data = urllib.urlencode(values) 

    req = urllib2.Request(url, url_data)
    response = urllib2.urlopen(req) 

    soup = BeautifulSoup(response,from_encoding="utf-8")
    balance_sheet_datas = soup.find_all("td", {'style' : 'text-align:left;white-space:nowrap;'})

    balance_sheet = SeasonBalanceSheet()
    balance_sheet.symbol = stock_symbol
    balance_sheet.year = str(1911+year)
    balance_sheet.season = season
    balance_sheet.surrogate_key = stock_symbol + '_' + str(year) + str(season).zfill(2)
    for data in balance_sheet_datas:
        if r'現金及約當現金' in data.string.encode('utf-8'):
            balance_sheet.cash_and_cash_equivalents = Decimal(data.next_sibling.next_sibling.string.strip().replace(',',''))



    response = urllib2.urlopen(req)
    the_page = response.read()
    return HttpResponse(the_page)

#資產負債表
# def update_season_balance_sheet2(request):
#     stock_symbol = '2454'
#     url = 'http://jsjustweb.jihsun.com.tw/z/zc/zcp/zcpa/zcpa_' + stock_symbol + '.djhtm'
#     data = urllib.urlopen(url)
#     soup = BeautifulSoup(data)

#     season_datas = soup.find_all("td", { "class": "t2" })
#     season_info = False
#     totaldata = []
#     for season_data in season_datas:
#         if season_info:
#             balanceSheet = SeasonBalanceSheet()
#             year = int(season_data.string.split('Q')[0].split('.')[0]) + 1911
#             season = int(season_data.string.split('Q')[0].split('.')[1])
#             balanceSheet.year = year
#             balanceSheet.season = season
#             balanceSheet.symbol = stock_symbol
#             balanceSheet.surrogate_key = stock_symbol + '_' + str(year) + str(season).zfill(2)
#             totaldata.append(balanceSheet)
#         elif season_data.string.encode('utf-8') == r'期別':
#             season_info = True

#     none_data = 'N/A'
#     season_datas = soup.find_all("td", { "class": "t4t1" })
#     for season_data in season_datas:
#         data = season_data
#         # print season_data.string.encode('utf-8')
#         if r'現金及約當現金' in season_data.string.encode('utf-8'):
#             for i in range(8):
#                 next = data.next_sibling.next_sibling
#                 data = next
#                 if data.string != none_data:
#                     totaldata[i].cash = Decimal(data.string.replace(',',''))
#                 else:
#                     totaldata[i].cash = 0
#         elif r'短期投資' in season_data.string.encode('utf-8'):
#             for i in range(8):
#                 next = data.next_sibling.next_sibling
#                 data = next
#                 if data.string != none_data:
#                     totaldata[i].short_term_investment = Decimal(data.string.replace(',', ''))
#                 else:
#                     totaldata[i].short_term_investment = 0
#         elif r'應收帳款及票據' in season_data.string.encode('utf-8'):
#             for i in range(8):
#                 next = data.next_sibling.next_sibling
#                 data = next
#                 if data.string != none_data:
#                     totaldata[i].accounts_and_notes_receivable = Decimal(data.string.replace(',',''))
#                 else:
#                     totaldata[i].accounts_and_notes_receivable = 0
#         elif r'其他應收款' in season_data.string.encode('utf-8'):
#             for i in range(8):
#                 next = data.next_sibling.next_sibling
#                 data = next
#                 if data.string != none_data:
#                     totaldata[i].other_receivable = Decimal(data.string.replace(',',''))
#                 else:
#                     totaldata[i].other_receivable = 0
#         elif r'短期借支' in season_data.string.encode('utf-8'):
#             for i in range(8):
#                 next = data.next_sibling.next_sibling
#                 data = next
#                 if data.string != none_data:
#                     totaldata[i].short_term_debt = Decimal(data.string.replace(',',''))
#                 else:
#                     totaldata[i].short_term_debt = 0
#         elif r'存貨' in season_data.string.encode('utf-8'):
#             for i in range(8):
#                 next = data.next_sibling.next_sibling
#                 data = next
#                 if data.string != none_data:
#                     totaldata[i].inventories = Decimal(data.string.replace(',',''))
#                 else:
#                     totaldata[i].inventories = 0
#         elif r'在建工程' in season_data.string.encode('utf-8'):
#             for i in range(8):
#                 next = data.next_sibling.next_sibling
#                 data = next
#                 if data.string != none_data:
#                     totaldata[i].construction_in_progress = Decimal(data.string.replace(',',''))
#                 else:
#                     totaldata[i].construction_in_progress = 0
#         elif r'預付費用及預付款' in season_data.string.encode('utf-8'):
#             for i in range(8):
#                 next = data.next_sibling.next_sibling
#                 data = next
#                 if data.string != none_data:
#                     totaldata[i].accounts_prepaid = Decimal(data.string.replace(',',''))
#                 else:
#                     totaldata[i].accounts_prepaid = 0
#         elif r'其他流動資產' in season_data.string.encode('utf-8'):
#             for i in range(8):
#                 next = data.next_sibling.next_sibling
#                 data = next
#                 if data.string != none_data:
#                     totaldata[i].other_current_assets = Decimal(data.string.replace(',',''))
#                 else:
#                     totaldata[i].other_current_assets = 0
#         elif r'流動資產' in season_data.string.encode('utf-8'):
#             for i in range(8):
#                 next = data.next_sibling.next_sibling
#                 data = next
#                 if data.string != none_data:
#                     totaldata[i].current_assets = Decimal(data.string.replace(',',''))
#                 else:
#                     totaldata[i].current_assets = 0
#         elif r'長期投資' in season_data.string.encode('utf-8') and r'長期投資評價損失' not in season_data.string.encode('utf-8'):
#             for i in range(8):
#                 next = data.next_sibling.next_sibling
#                 data = next
#                 if data.string != none_data:
#                     totaldata[i].long_term_investment = Decimal(data.string.replace(',',''))
#                 else:
#                     totaldata[i].long_term_investment = 0
#         elif r'土地成本' in season_data.string.encode('utf-8'):
#             for i in range(8):
#                 next = data.next_sibling.next_sibling
#                 data = next
#                 if data.string != none_data:
#                     totaldata[i].land_cost = Decimal(data.string.replace(',',''))
#                 else:
#                     totaldata[i].land_cost = 0
#         elif r'房屋及建築成本' in season_data.string.encode('utf-8'):
#             for i in range(8):
#                 next = data.next_sibling.next_sibling
#                 data = next
#                 if data.string != none_data:
#                     totaldata[i].building_and_construction_cost = Decimal(data.string.replace(',',''))
#                 else:
#                     totaldata[i].building_and_construction_cost = 0
#         elif r'機器及儀器設備成本' in season_data.string.encode('utf-8'):
#             for i in range(8):
#                 next = data.next_sibling.next_sibling
#                 data = next
#                 if data.string != none_data:
#                     totaldata[i].machinery_and_equipment_cost = Decimal(data.string.replace(',',''))
#                 else:
#                     totaldata[i].machinery_and_equipment_cost = 0
#         elif r'其他設備成本' in season_data.string.encode('utf-8'):
#             for i in range(8):
#                 next = data.next_sibling.next_sibling
#                 data = next
#                 if data.string != none_data:
#                     totaldata[i].other_equipment_cost = Decimal(data.string.replace(',',''))
#                 else:
#                     totaldata[i].other_equipment_cost = 0
#         elif r'固定資產重估增值' in season_data.string.encode('utf-8'):
#             for i in range(8):
#                 next = data.next_sibling.next_sibling
#                 data = next
#                 if data.string != none_data:
#                     totaldata[i].reval_fixed_assets = Decimal(data.string.replace(',',''))
#                 else:
#                     totaldata[i].reval_fixed_assets = 0
#         elif r'固定資產累計折舊' in season_data.string.encode('utf-8'):
#             for i in range(8):
#                 next = data.next_sibling.next_sibling
#                 data = next
#                 if data.string != none_data:
#                     totaldata[i].accumulated_fixed_assets = Decimal(data.string.replace(',',''))
#                 else:
#                     totaldata[i].accumulated_fixed_assets = 0
#         elif r'固定資產損失準備' in season_data.string.encode('utf-8'):
#             for i in range(8):
#                 next = data.next_sibling.next_sibling
#                 data = next
#                 if data.string != none_data:
#                     totaldata[i].loss_res_fixed_assets = Decimal(data.string.replace(',',''))
#                 else:
#                     totaldata[i].loss_res_fixed_assets = 0
#         elif r'未完工程及預付款' in season_data.string.encode('utf-8'):
#             for i in range(8):
#                 next = data.next_sibling.next_sibling
#                 data = next
#                 if data.string != none_data:
#                     totaldata[i].long_term_construction_in_progress = Decimal(data.string.replace(',',''))
#                 else:
#                     totaldata[i].long_term_construction_in_progress = 0
#         elif r'固定資產' in season_data.string.encode('utf-8'):
#             for i in range(8):
#                 next = data.next_sibling.next_sibling
#                 data = next
#                 if data.string != none_data:
#                     totaldata[i].fixed_assets = Decimal(data.string.replace(',',''))
#                 else:
#                     totaldata[i].fixed_assets = 0
#         elif r'遞延資產' in season_data.string.encode('utf-8'):
#             for i in range(8):
#                 next = data.next_sibling.next_sibling
#                 data = next
#                 if data.string != none_data:
#                     totaldata[i].deferred_assets = Decimal(data.string.replace(',',''))
#                 else:
#                     totaldata[i].deferred_assets = 0
#         elif r'無形資產' in season_data.string.encode('utf-8'):
#             for i in range(8):
#                 next = data.next_sibling.next_sibling
#                 data = next
#                 if data.string != none_data:
#                     totaldata[i].intangible_assets = Decimal(data.string.replace(',',''))
#                 else:
#                     totaldata[i].intangible_assets = 0
#         elif r'什項資產' in season_data.string.encode('utf-8'):
#             for i in range(8):
#                 next = data.next_sibling.next_sibling
#                 data = next
#                 if data.string != none_data:
#                     totaldata[i].other_non_curr_assets = Decimal(data.string.replace(',',''))
#                 else:
#                     totaldata[i].other_non_curr_assets = 0
#         elif r'其他資產' in season_data.string.encode('utf-8'):
#             for i in range(8):
#                 next = data.next_sibling.next_sibling
#                 data = next
#                 if data.string != none_data:
#                     totaldata[i].other_assets = Decimal(data.string.replace(',',''))
#                 else:
#                     totaldata[i].other_assets = 0
#         elif r'資產總額' in season_data.string.encode('utf-8'):
#             for i in range(8):
#                 next = data.next_sibling.next_sibling
#                 data = next
#                 if data.string != none_data:
#                     totaldata[i].total_assets = Decimal(data.string.replace(',',''))
#                 else:
#                     totaldata[i].total_assets = 0
#         elif r'短期借款' in season_data.string.encode('utf-8'):
#             for i in range(8):
#                 next = data.next_sibling.next_sibling
#                 data = next
#                 if data.string != none_data:
#                     totaldata[i].short_term_borrowing = Decimal(data.string.replace(',',''))
#                 else:
#                     totaldata[i].short_term_borrowing = 0
#         elif r'應付商業本票' in season_data.string.encode('utf-8'):
#             for i in range(8):
#                 next = data.next_sibling.next_sibling
#                 data = next
#                 if data.string != none_data:
#                     totaldata[i].bills_issued = Decimal(data.string.replace(',',''))
#                 else:
#                     totaldata[i].bills_issued = 0
#         elif r'應付帳款及票據' in season_data.string.encode('utf-8'):
#             for i in range(8):
#                 next = data.next_sibling.next_sibling
#                 data = next
#                 if data.string != none_data:
#                     totaldata[i].accounts_and_notes_payable = Decimal(data.string.replace(',',''))
#                 else:
#                     totaldata[i].accounts_and_notes_payable = 0
#         elif r'應付費用' in season_data.string.encode('utf-8'):
#             for i in range(8):
#                 next = data.next_sibling.next_sibling
#                 data = next
#                 if data.string != none_data:
#                     totaldata[i].accrued_expenses = Decimal(data.string.replace(',',''))
#                 else:
#                     totaldata[i].accrued_expenses = 0
#         elif r'預收款項' in season_data.string.encode('utf-8'):
#             for i in range(8):
#                 next = data.next_sibling.next_sibling
#                 data = next
#                 if data.string != none_data:
#                     totaldata[i].advances_customers = Decimal(data.string.replace(',',''))
#                 else:
#                     totaldata[i].advances_customers = 0
#         elif r'其他應付款' in season_data.string.encode('utf-8'):
#             for i in range(8):
#                 next = data.next_sibling.next_sibling
#                 data = next
#                 if data.string != none_data:
#                     totaldata[i].other_payable = Decimal(data.string.replace(',',''))
#                 else:
#                     totaldata[i].other_payable = 0
#         elif r'應付所得稅' in season_data.string.encode('utf-8'):
#             for i in range(8):
#                 next = data.next_sibling.next_sibling
#                 data = next
#                 if data.string != none_data:
#                     totaldata[i].accrued_income_tax = Decimal(data.string.replace(',',''))
#                 else:
#                     totaldata[i].accrued_income_tax = 0
#         elif r'一年內到期長期負債' in season_data.string.encode('utf-8'):
#             for i in range(8):
#                 next = data.next_sibling.next_sibling
#                 data = next
#                 if data.string != none_data:
#                     totaldata[i].long_term_liabilities_due_whthin_one_year = Decimal(data.string.replace(',',''))
#                 else:
#                     totaldata[i].long_term_liabilities_due_whthin_one_year = 0
#         elif r'其他流動負債' in season_data.string.encode('utf-8'):
#             for i in range(8):
#                 next = data.next_sibling.next_sibling
#                 data = next
#                 if data.string != none_data:
#                     totaldata[i].other_current_liabilities = Decimal(data.string.replace(',',''))
#                 else:
#                     totaldata[i].other_current_liabilities = 0
#         elif r'流動負債' in season_data.string.encode('utf-8'):
#             for i in range(8):
#                 next = data.next_sibling.next_sibling
#                 data = next
#                 if data.string != none_data:
#                     totaldata[i].total_current_liabilities = Decimal(data.string.replace(',',''))
#                 else:
#                     totaldata[i].total_current_liabilities = 0
#         elif r'長期負債' in season_data.string.encode('utf-8'):
#             for i in range(8):
#                 next = data.next_sibling.next_sibling
#                 data = next
#                 if data.string != none_data:
#                     totaldata[i].long_term_liabilities = Decimal(data.string.replace(',',''))
#                 else:
#                     totaldata[i].long_term_liabilities = 0
#         elif r'遞延貸項' in season_data.string.encode('utf-8'):
#             for i in range(8):
#                 next = data.next_sibling.next_sibling
#                 data = next
#                 if data.string != none_data:
#                     totaldata[i].deferred_credit = Decimal(data.string.replace(',',''))
#                 else:
#                     totaldata[i].deferred_credit = 0
#         elif r'退休金準備' in season_data.string.encode('utf-8'):
#             for i in range(8):
#                 next = data.next_sibling.next_sibling
#                 data = next
#                 if data.string != none_data:
#                     totaldata[i].accrued_pension_pay = Decimal(data.string.replace(',',''))
#                 else:
#                     totaldata[i].accrued_pension_pay = 0
#         elif r'遞延所得稅' in season_data.string.encode('utf-8'):
#             for i in range(8):
#                 next = data.next_sibling.next_sibling
#                 data = next
#                 if data.string != none_data:
#                     totaldata[i].deferred_tax = Decimal(data.string.replace(',',''))
#                 else:
#                     totaldata[i].deferred_tax = 0
#         elif r'土地增值稅準備' in season_data.string.encode('utf-8'):
#             for i in range(8):
#                 next = data.next_sibling.next_sibling
#                 data = next
#                 if data.string != none_data:
#                     totaldata[i].res_for_land_reval = Decimal(data.string.replace(',',''))
#                 else:
#                     totaldata[i].res_for_land_reval = 0
#         elif r'各項損失準備' in season_data.string.encode('utf-8'):
#             for i in range(8):
#                 next = data.next_sibling.next_sibling
#                 data = next
#                 if data.string != none_data:
#                     totaldata[i].other_spec_reserve = Decimal(data.string.replace(',',''))
#                 else:
#                     totaldata[i].other_spec_reserve = 0
#         elif r'什項負債' in season_data.string.encode('utf-8'):
#             for i in range(8):
#                 next = data.next_sibling.next_sibling
#                 data = next
#                 if data.string != none_data:
#                     totaldata[i].misc_long_term_liabilities = Decimal(data.string.replace(',',''))
#                 else:
#                     totaldata[i].misc_long_term_liabilities = 0
#         elif r'其他負債及準備' in season_data.string.encode('utf-8'):
#             for i in range(8):
#                 next = data.next_sibling.next_sibling
#                 data = next
#                 if data.string != none_data:
#                     totaldata[i].other_long_term_liabilities = Decimal(data.string.replace(',',''))
#                 else:
#                     totaldata[i].other_long_term_liabilities = 0
#         elif r'負債總額' in season_data.string.encode('utf-8'):
#             for i in range(8):
#                 next = data.next_sibling.next_sibling
#                 data = next
#                 if data.string != none_data:
#                     totaldata[i].total_liabilities = Decimal(data.string.replace(',',''))
#                 else:
#                     totaldata[i].total_liabilities = 0
#         elif r'股東權益總額' in season_data.string.encode('utf-8'):
#             for i in range(8):
#                 next = data.next_sibling.next_sibling
#                 data = next
#                 if data.string != none_data:
#                     totaldata[i].total_equity = Decimal(data.string.replace(',',''))
#                 else:
#                     totaldata[i].total_equity = 0
#         elif r'普通股股本' in season_data.string.encode('utf-8'):
#             for i in range(8):
#                 next = data.next_sibling.next_sibling
#                 data = next
#                 if data.string != none_data:
#                     totaldata[i].common_stocks = Decimal(data.string.replace(',',''))
#                 else:
#                     totaldata[i].common_stocks = 0
#         elif r'特別股股本' in season_data.string.encode('utf-8'):
#             for i in range(8):
#                 next = data.next_sibling.next_sibling
#                 data = next
#                 if data.string != none_data:
#                     totaldata[i].preferred_stocks = Decimal(data.string.replace(',',''))
#                 else:
#                     totaldata[i].preferred_stocks = 0
#         elif r'資本公積' in season_data.string.encode('utf-8'):
#             for i in range(8):
#                 next = data.next_sibling.next_sibling
#                 data = next
#                 if data.string != none_data:
#                     totaldata[i].capital_reserve = Decimal(data.string.replace(',',''))
#                 else:
#                     totaldata[i].capital_reserve = 0
#         elif r'法定盈餘公積' in season_data.string.encode('utf-8'):
#             for i in range(8):
#                 next = data.next_sibling.next_sibling
#                 data = next
#                 if data.string != none_data:
#                     totaldata[i].legal_reserve = Decimal(data.string.replace(',',''))
#                 else:
#                     totaldata[i].legal_reserve = 0
#         elif r'特別盈餘公積' in season_data.string.encode('utf-8'):
#             for i in range(8):
#                 next = data.next_sibling.next_sibling
#                 data = next
#                 if data.string != none_data:
#                     totaldata[i].appropriated_reserve = Decimal(data.string.replace(',',''))
#                 else:
#                     totaldata[i].appropriated_reserve = 0
#         elif r'未分配盈餘' in season_data.string.encode('utf-8'):
#             for i in range(8):
#                 next = data.next_sibling.next_sibling
#                 data = next
#                 if data.string != none_data:
#                     totaldata[i].unappropriated_reserve = Decimal(data.string.replace(',',''))
#                 else:
#                     totaldata[i].unappropriated_reserve = 0
#         elif r'長期投資評價損失' in season_data.string.encode('utf-8'):
#             for i in range(8):
#                 next = data.next_sibling.next_sibling
#                 data = next
#                 if data.string != none_data:
#                     totaldata[i].value_loss_long_term_investment = Decimal(data.string.replace(',',''))
#                 else:
#                     totaldata[i].value_loss_long_term_investment = 0
#         elif r'少數股權' in season_data.string.encode('utf-8'):
#             for i in range(8):
#                 next = data.next_sibling.next_sibling
#                 data = next
#                 if data.string != none_data:
#                     totaldata[i].minority_interests = Decimal(data.string.replace(',',''))
#                 else:
#                     totaldata[i].minority_interests = 0
#         elif r'負債及股東權益總額' in season_data.string.encode('utf-8'):
#             for i in range(8):
#                 next = data.next_sibling.next_sibling
#                 data = next
#                 if data.string != none_data:
#                     totaldata[i].total_liabilities_and_equity = Decimal(data.string.replace(',',''))
#                 else:
#                     totaldata[i].total_liabilities_and_equity = 0
#     for i in range(len(totaldata)):
#         totaldata[i].save()
#     # for season_data in season_datas:
#         # print season_data
#     # print season_datas
#     return HttpResponse('BeautifulSoup')

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
