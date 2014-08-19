#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.db import models

# 綜合損益表
class SeasonIncomeStatement(models.Model):
    surrogate_key = models.CharField(max_length=50, primary_key=True)
    symbol = models.CharField(max_length=20, db_index=True)
    year = models.IntegerField(db_index=True)
    season = models.IntegerField(db_index=True)
    date = models.DateField(db_index=True)
    # 營業收入合計
    operating_revenue = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    # 營業成本合計
    operating_cost = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    # 營業毛利(毛損)
    gross_profit_from_operations = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    # 已實現銷貨損益
    realized_profit_from_sales = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    # 營業毛利(毛損)淨額
    net_gross_profit_from_operations = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    # 推銷費用
    selling_expenses = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    # 管理費用
    administrative_expenses = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    # 研究發展費用
    research_and_development_expenses = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    # 營業費用合計
    operating_expenses = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    # 其他收益及費損淨額
    net_other_income = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    # 營業利益
    net_operating_income = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    # 其它收入
    other_income = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    # 其它利益及損失金額
    other_gains_and_losses = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    # 財務成本淨額
    finance_costs = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    # 採用權益法認列之關聯企業及合資損益之份額淨額
    # Share of profit (loss) of associates and joint ventures accounted for using equity method, net
    share_of_profit_of_associates = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    # 營業外收入及支出合計
    non_operating_income_and_expenses = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    # 稅前淨利(淨損)
    profit_from_continuing_operations_before_tax = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    # 所得稅費用(利益合計)
    tax_expense = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    # 繼續營業單位本期淨利(淨損)
    profit_from_continuing_operations = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    # 本期淨利
    profit = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    # 國外營運機構財務報表換算之兌換差額
    exchange_differences_on_translation = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    # 備供出售金融資產未實現評價損益
    unrealised_gains_for_sale_financial_assets = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    # 採用權益法認列之關聯企業及合資之其他綜合損益之份額合計
    # Total share of other comprehensive income of associates and joint ventures accounted for using equity method 
    total_share_of_income_of_associates = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    # 與其他綜合損益組成部分相關之所得稅
    income_tax_of_other_comprehensive_income = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    # 其他綜合損益（淨額）
    other_comprehensive_income = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    # 本期綜合損益總額
    total_comprehensive_income = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    # 母公司業主（淨利／損）
    profit_to_owners_of_parent = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    # 非控制權益（淨利／損）
    profit_to_non_controlling_interests = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    # 母公司業主（綜合損益）
    comprehensive_income_to_owners_of_parent = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    # 非控制權益（綜合損益）
    comprehensive_income_to_non_controlling_interests = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    # 基本每股盈餘
    basic_earnings_per_share = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    # 稀釋每股盈餘
    diluted_earnings_per_share = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    interest_income = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    interest_expenses = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    net_income_of_interest = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    net_service_fee_income = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    gain_on_financial_assets_or_liabilities_measured = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    realized_gains_for_sale_financial_assets = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    realized_gains_on_held_to_maturity_financial_assets = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    foreign_exchange_gain = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    reversal_of_impairment_loss_on_assets = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    gain_on_disposal_of_investments_accounted = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    net_other_non_interest_income = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    net_non_interest_income = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    net_income = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    total_bad_debts_expense = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    employee_benefits_expenses = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    depreciation_and_amortization_expense = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    income_from_discontinued_operations = models.DecimalField(max_digits=20, decimal_places=0, null=True)


    def percent_operating_revenue(self):
        return operating_revenue / operating_revenue
    def percent_operating_cost(self):
        return operating_cost / operating_revenue
    def percent_gross_profit_from_operations(self):
        return gross_profit_from_operations / operating_revenue
    def percent_selling_expenses(self):
        return selling_expenses / operating_revenue
    def percent_administrative_expenses(self):
        return administrative_expenses / operating_revenue
    def percent_research_and_development_expenses(self):
        return research_and_development_expenses / operating_revenue
    def percent_operating_expenses(self):
        return operating_expenses / operating_revenue
    def percent_net_operating_income(self):
        return net_operating_income / operating_revenue
    def percent_other_income(self):
        return other_income / operating_revenue
    def percent_other_gains_and_losses(self):
        return other_gains_and_losses / operating_revenue
    def percent_finance_costs(self):
        return finance_costs / operating_revenue
    def percent_non_operating_income_and_expenses(self):
        return non_operating_income_and_expenses / operating_revenue
    def percent_profit_from_continuing_operations_before_tax(self):
        return profit_from_continuing_operations_before_tax / operating_revenue
    def percent_tax_expense(self):
        return tax_expense / operating_revenue
    def percent_profit_from_continuing_operations(self):
        return profit_from_continuing_operations / operating_revenue
    def percent_profit(self):
        return profit / operating_revenue
    def percent_exchange_differences_on_translation(self):
        return exchange_differences_on_translation / operating_revenue
    def percent_unrealised_gains_for_sale_financial_assets(self):
        return unrealised_gains_for_sale_financial_assets / operating_revenue
    def percent_income_tax_of_other_comprehensive_income(self):
        return other_comprehensive_income / operating_revenue
    def percent_total_comprehensive_income(self):
        return total_comprehensive_income / operating_revenue
    def percent_profit_to_owners_of_parent(self):
        return profit_to_owners_of_parent / operating_revenue
    def percent_profit_to_non_controlling_interests(self):
        return profit_to_non_controlling_interests / operating_revenue
    def percent_comprehensive_income_to_owners_of_parent(self):
        return comprehensive_income_to_owners_of_parent / operating_revenue
    def percent_comprehensive_income_to_non_controlling_interests(self):
        return comprehensive_income_to_non_controlling_interests / operating_revenue

class YearFinancialRatio(models.Model):
    surrogate_key = models.CharField(max_length=20, primary_key=True)
    year = models.IntegerField(db_index=True)
    date = models.DateField(db_index=True)
    symbol = models.CharField(max_length=20, db_index=True)
    gross_profit_margin = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    operating_profit_margin = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    net_before_tax_profit_margin = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    net_after_tax_profit_margin = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    net_value_per_share = models.DecimalField(max_digits=20, decimal_places=4, null=True)
    revenue_per_share = models.DecimalField(max_digits=20, decimal_places=4, null=True)
    operating_profit_per_share = models.DecimalField(max_digits=20, decimal_places=4, null=True)
    net_before_tax_profit_per_share = models.DecimalField(max_digits=20, decimal_places=4, null=True)
    return_on_equity = models.DecimalField(max_digits=20, decimal_places=4, null=True)
    return_on_assets = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    net_after_tax_profit_per_share = models.DecimalField(max_digits=20, decimal_places=4, null=True)
    revenue_growth_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    operating_profit_growth_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    net_before_tax_profit_growth_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    net_after_tax_profit_growth_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    assets_growth_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    net_value_growth_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    fixed_assets_growth_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    current_ratio = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    quick_ratio = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    debt_ratio = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    interest_cover = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    account_receivable_turnover_ratio = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    inventory_turnover_ratio = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    fixed_assets_turnover_ratio = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    assets_turnover_ratio = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    revenue_per_employee = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    equity_turnover_ratio = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    debt_equity_ratio = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    long_term_funds_to_fixed_assets = models.DecimalField(max_digits=10, decimal_places=2, null=True)

    chinese_map = {
        'revenue_growth_rate' : r'營收成長率',
        'operating_profit_growth_rate' : r'營業利益成長率',
        'net_before_tax_profit_growth_rate' : r'稅前淨利成長率',
        'net_after_tax_profit_growth_rate' : r'稅後淨利成長率',
        'assets_growth_rate' : r'總資產成長率',
        'net_value_growth_rate' : r'淨值成長率',
        'fixed_assets_growth_rate' : r'固定資產成長率',
    }

    def chinese(self, source):
        chinese_name = self.chinese_map[source]
        return chinese_name

class SeasonFinancialRatio(models.Model):
    surrogate_key = models.CharField(max_length=20, primary_key=True)
    year = models.IntegerField(db_index=True)
    season = models.IntegerField(db_index=True)
    symbol = models.CharField(max_length=20, db_index=True)
    date = models.DateField(db_index=True)
    gross_profit_margin = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    operating_profit_margin = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    net_before_tax_profit_margin = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    net_after_tax_profit_margin = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    net_value_per_share = models.DecimalField(max_digits=20, decimal_places=4, null=True)
    revenue_per_share = models.DecimalField(max_digits=20, decimal_places=4, null=True)
    operating_profit_per_share = models.DecimalField(max_digits=20, decimal_places=4, null=True)
    net_before_tax_profit_per_share = models.DecimalField(max_digits=20, decimal_places=4, null=True)
    return_on_equity = models.DecimalField(max_digits=20, decimal_places=4, null=True)
    return_on_assets = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    net_after_tax_profit_per_share = models.DecimalField(max_digits=20, decimal_places=4, null=True)
    revenue_growth_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    operating_profit_growth_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    net_before_tax_profit_growth_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    net_after_tax_profit_growth_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    assets_growth_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    net_value_growth_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    fixed_assets_growth_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    current_ratio = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    quick_ratio = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    debt_ratio = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    interest_cover = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    account_receivable_turnover_ratio = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    inventory_turnover_ratio = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    fixed_assets_turnover_ratio = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    assets_turnover_ratio = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    revenue_per_employee = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    equity_turnover_ratio = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    debt_equity_ratio = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    long_term_funds_to_fixed_assets = models.DecimalField(max_digits=10, decimal_places=2, null=True)

    chinese_map = {
        'revenue_growth_rate' : r'營收成長率',
        'operating_profit_growth_rate' : r'營業利益成長率',
        'net_before_tax_profit_growth_rate' : r'稅前淨利成長率',
        'net_after_tax_profit_growth_rate' : r'稅後淨利成長率',
        'assets_growth_rate' : r'總資產成長率',
        'net_value_growth_rate' : r'淨值成長率',
        'fixed_assets_growth_rate' : r'固定資產成長率'
    }

    def chinese(self, source):
        chinese_name = self.chinese_map[source]
        return chinese_name

# 資產負債表
class SeasonBalanceSheet(models.Model):
    surrogate_key = models.CharField(max_length=20, primary_key=True)
    year = models.IntegerField(db_index=True)
    season = models.IntegerField(db_index=True)
    symbol = models.CharField(max_length=20, db_index=True)
    date = models.DateField(db_index=True)
    cash_and_cash_equivalents = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    current_financial_assets = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    notes_receivable = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    accounts_receivable = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    inventories = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    prepayments = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    other_current_assets = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    total_current_assets = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    non_current_available_for_sale_financial_assets = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    property_plant_and_equipment = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    investment_property = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    intangible_assets = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    deferred_tax_assets = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    other_non_current_assets = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    total_non_current_assets = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    total_assets = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    short_term_borrowings = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    current_financial_liabilities = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    notes_payable = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    accounts_payable = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    other_payables = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    current_tax_liabilities = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    current_provisions = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    other_current_liabilities = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    total_current_liabilities = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    deferred_tax_liabilities = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    other_non_current_liabilities = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    total_non_current_liabilities = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    total_liabilities = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    ordinary_share = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    total_capital_stock = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    additional_paid_in_capital = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    treasury_share_transactions = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    net_assets_from_merger = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    total_capital_surplus = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    legal_reserve = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    special_reserve = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    unappropriated_retained_earnings = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    retained_earnings = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    exchange_differences_of_foreign_financial_statements = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    unrealised_gains_for_sale_financial_assets = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    other_equity_interest = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    equity_attributable_to_owners_of_parent = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    non_controlling_interests = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    total_equity = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    equivalent_issue_shares_of_advance_receipts = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    number_of_shares_in_entity_held_by_entity = models.DecimalField(max_digits=20, decimal_places=0, null=True)
