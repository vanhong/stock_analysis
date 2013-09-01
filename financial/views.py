#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib
from django.http import HttpResponse
from HTMLParser import HTMLParser
import time
from decimal import Decimal
from stocks.models import StockId
from financial.models import SeasonFinancialRatio

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
