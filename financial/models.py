from django.db import models

class SeasonIncomeStatement(models.Model):
    surrogate_key = models.CharField(max_length=50, primary_key=True)
    symbol = models.CharField(max_length=20, db_index=True)
    year = models.IntegerField(db_index=True)
    season = models.IntegerField(db_index=True)
    operating_revenue = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    operating_cost = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    gross_profit_from_operations = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    selling_expenses = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    administrative_expenses = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    research_and_development_expenses = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    operating_expenses = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    net_operating_income = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    other_income = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    other_gains_and_losses = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    finance_costs = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    non_operating_income_and_expenses = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    profit_from_continuing_operations_before_tax = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    tax_expense = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    profit_from_continuing_operations = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    profit = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    exchange_differences_on_translation = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    unrealised_gains_for_sale_financial_assets = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    income_tax_of_other_comprehensive_income = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    other_comprehensive_income = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    total_comprehensive_income = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    profit_to_owners_of_parent = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    profit_to_non_controlling_interests = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    comprehensive_income_to_owners_of_parent = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    comprehensive_income_to_non_controlling_interests = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    basic_earnings_per_share = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    diluted_earnings_per_share = models.DecimalField(max_digits=20, decimal_places=2, null=True)

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

class SeasonFinancialRatio(models.Model):
    surrogate_key = models.CharField(max_length=20, primary_key=True)
    year = models.IntegerField(db_index=True)
    season = models.IntegerField(db_index=True)
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

class SeasonBalanceSheet(models.Model):
    surrogate_key = models.CharField(max_length=20, primary_key=True)
    year = models.IntegerField(db_index=True)
    season = models.IntegerField(db_index=True)
    symbol = models.CharField(max_length=20, db_index=True)
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


# class SeasonBalanceSheet2(models.Model):
#     surrogate_key = models.CharField(max_length=20, primary_key=True)
#     year = models.IntegerField(db_index=True)
#     season = models.IntegerField(db_index=True)
#     symbol = models.CharField(max_length=20, db_index=True)
#     cash = models.DecimalField(max_digits=20, decimal_places=0, null=True)
#     short_term_investment = models.DecimalField(max_digits=20, decimal_places=0, null=True)
#     accounts_and_notes_receivable = models.DecimalField(max_digits=20, decimal_places=0, null=True)
#     other_receivable = models.DecimalField(max_digits=20, decimal_places=0, null=True)
#     short_term_debt = models.DecimalField(max_digits=20, decimal_places=0, null=True)
#     inventories = models.DecimalField(max_digits=20, decimal_places=0, null=True)
#     construction_in_progress = models.DecimalField(max_digits=20, decimal_places=0, null=True)
#     accounts_prepaid = models.DecimalField(max_digits=20, decimal_places=0, null=True)
#     other_current_assets = models.DecimalField(max_digits=20, decimal_places=0, null=True)
#     current_assets = models.DecimalField(max_digits=20, decimal_places=0, null=True)
#     long_term_investment = models.DecimalField(max_digits=20, decimal_places=0, null=True)
#     land_cost = models.DecimalField(max_digits=20, decimal_places=0, null=True)
#     building_and_construction_cost = models.DecimalField(max_digits=20, decimal_places=0, null=True)
#     machinery_and_equipment_cost = models.DecimalField(max_digits=20, decimal_places=0, null=True)
#     other_equipment_cost = models.DecimalField(max_digits=20, decimal_places=0, null=True)
#     reval_fixed_assets = models.DecimalField(max_digits=20, decimal_places=0, null=True)
#     accumulated_fixed_assets = models.DecimalField(max_digits=20, decimal_places=0, null=True)
#     loss_res_fixed_assets = models.DecimalField(max_digits=20, decimal_places=0, null=True)
#     long_term_construction_in_progress = models.DecimalField(max_digits=20, decimal_places=0, null=True)
#     fixed_assets = models.DecimalField(max_digits=20, decimal_places=0, null=True)
#     deferred_assets = models.DecimalField(max_digits=20, decimal_places=0, null=True)
#     intangible_assets = models.DecimalField(max_digits=20, decimal_places=0, null=True)
#     other_non_curr_assets = models.DecimalField(max_digits=20, decimal_places=0, null=True)
#     other_assets = models.DecimalField(max_digits=20, decimal_places=0, null=True)
#     total_assets = models.DecimalField(max_digits=20, decimal_places=0, null=True)
#     short_term_borrowing = models.DecimalField(max_digits=20, decimal_places=0, null=True)
#     bills_issued = models.DecimalField(max_digits=20, decimal_places=0, null=True)
#     accounts_and_notes_payable = models.DecimalField(max_digits=20, decimal_places=0, null=True)
#     accrued_expenses = models.DecimalField(max_digits=20, decimal_places=0, null=True)
#     advances_customers = models.DecimalField(max_digits=20, decimal_places=0, null=True)
#     other_payable = models.DecimalField(max_digits=20, decimal_places=0, null=True)
#     accrued_income_tax = models.DecimalField(max_digits=20, decimal_places=0, null=True)
#     long_term_liabilities_due_whthin_one_year = models.DecimalField(max_digits=20, decimal_places=0, null=True)
#     other_current_liabilities = models.DecimalField(max_digits=20, decimal_places=0, null=True)
#     total_current_liabilities = models.DecimalField(max_digits=20, decimal_places=0, null=True)
#     long_term_liabilities = models.DecimalField(max_digits=20, decimal_places=0, null=True)
#     deferred_credit = models.DecimalField(max_digits=20, decimal_places=0, null=True)
#     accrued_pension_pay = models.DecimalField(max_digits=20, decimal_places=0, null=True)
#     deferred_tax = models.DecimalField(max_digits=20, decimal_places=0, null=True)
#     res_for_land_reval = models.DecimalField(max_digits=20, decimal_places=0, null=True)
#     other_spec_reserve = models.DecimalField(max_digits=20, decimal_places=0, null=True)
#     misc_long_term_liabilities = models.DecimalField(max_digits=20, decimal_places=0, null=True)
#     other_long_term_liabilities = models.DecimalField(max_digits=20, decimal_places=0, null=True)
#     total_liabilities = models.DecimalField(max_digits=20, decimal_places=0, null=True)
#     total_equity = models.DecimalField(max_digits=20, decimal_places=0, null=True)
#     common_stocks = models.DecimalField(max_digits=20, decimal_places=0, null=True)
#     preferred_stocks = models.DecimalField(max_digits=20, decimal_places=0, null=True)
#     capital_reserve = models.DecimalField(max_digits=20, decimal_places=0, null=True)
#     legal_reserve = models.DecimalField(max_digits=20, decimal_places=0, null=True)
#     appropriated_reserve = models.DecimalField(max_digits=20, decimal_places=0, null=True)
#     unappropriated_reserve = models.DecimalField(max_digits=20, decimal_places=0, null=True)
#     value_loss_long_term_investment = models.DecimalField(max_digits=20, decimal_places=0, null=True)
#     minority_interests = models.DecimalField(max_digits=20, decimal_places=0, null=True)
#     total_liabilities_and_equity = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    
