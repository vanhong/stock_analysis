from django.conf.urls import patterns, include, url
from django.conf.urls import *
from django.conf import settings
from stock_analysis.views import set_stockid
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('stock_analysis.views',
    (r'^analysis/$', 'analysis', {'template_name': 'revenue.html', 'drawTool': 'new Revenue.Tool();'}),
    (r'^revenue/$', 'analysis', {'template_name': 'revenue.html', 'drawTool': 'new Revenue.Tool();'}),
    (r'^dividend/$', 'analysis', {'template_name': 'dividend.html', 'drawTool': 'new Dividend.Tool();'}),
    (r'^profitability/$', 'analysis', {'template_name': 'profitability.html', 'drawTool': 'new Profitability.Tool();'}),
    (r'^performance_per_share/$', 'analysis', {'template_name': 'performance_per_share.html', 'drawTool': 'new PerformancePerShare.Tool();'}),
    (r'^roe/$', 'analysis', {'template_name': 'roe_roa.html', 'drawTool': 'new ROE.Tool();'}),
    (r'^current_ratio/$', 'analysis', {'template_name': 'current_ratio.html', 'drawTool': 'new CurrentRatio.Tool();'}),
    (r'^debt_ratio/$', 'analysis', {'template_name': 'debt_ratio.html', 'drawTool': 'new DebtRatio.Tool();'}),
    (r'^turnover_ratio/$', 'analysis', {'template_name': 'turnover_ratio.html', 'drawTool': 'new TurnoverRatio.Tool();'}),
    (r'^interest_cover/$', 'analysis', {'template_name': 'interest_cover.html', 'drawTool': 'new InterestCover.Tool();'}),
    (r'^revenue_growth_rate/$', 'analysis', {'template_name': 'growth_rate.html', 'drawTool': 'new GrowthRate.Tool();'}),
    (r'^operating_profit_growth_rate/$', 'analysis', {'template_name': 'growth_rate.html', 'drawTool': 'new GrowthRate.Tool();'}),
    (r'^net_before_tax_profit_growth_rate/$', 'analysis', {'template_name': 'growth_rate.html', 'drawTool': 'new GrowthRate.Tool();'}),
    (r'^net_after_tax_profit_growth_rate/$', 'analysis', {'template_name': 'growth_rate.html', 'drawTool': 'new GrowthRate.Tool();'}),
    (r'^assets_growth_rate/$', 'analysis', {'template_name': 'growth_rate.html', 'drawTool': 'new GrowthRate.Tool();'}),
    (r'^net_value_growth_rate/$', 'analysis', {'template_name': 'growth_rate.html', 'drawTool': 'new GrowthRate.Tool();'}),
    (r'^fixed_assets_growth_rate/$', 'analysis', {'template_name': 'growth_rate.html', 'drawTool': 'new GrowthRate.Tool();'}),

    (r'^get_performance_per_share_table/$', 'get_performance_per_share_table'),
    (r'^get_month_revenue_table/$', 'get_month_revenue_table'),
    (r'^get_season_revenue_table/$', 'get_season_revenue_table'),
    (r'^get_season_profit_table/$', 'get_season_profit_table'),
    (r'^get_dividend_table/$', 'get_dividend_table'),
    (r'^get_profitability_table/$', 'get_profitability_table'),
    (r'^get_roe_roa_table/$', 'get_roe_roa_table'),
    (r'^get_current_ratio_table/$', 'get_current_ratio_table'),
    (r'^get_debt_ratio_table/$', 'get_debt_ratio_table'),
    (r'^get_turnover_ratio_table/$', 'get_turnover_ratio_table'),
    (r'^get_interest_cover_table/$', 'get_interest_cover_table'),
    (r'^get_growth_rate_table/$', 'get_growth_rate_table'),
    
    (r'^get_performance_per_share_chart/$', 'get_performance_per_share_chart'),
    (r'^get_month_revenue_chart/$', 'get_month_revenue_chart'),
    (r'^get_season_revenue_chart/$', 'get_season_revenue_chart'),
    (r'^get_season_profit_chart/$', 'get_season_profit_chart'),
    (r'^get_dividend_chart/$', 'get_dividend_chart'),
    (r'^get_profitability_chart/$', 'get_profitability_chart'),
    (r'^get_roe_roa_chart/$', 'get_roe_roa_chart'),
    (r'^get_current_ratio_chart/$', 'get_current_ratio_chart'),
    (r'^get_debt_ratio_chart/$', 'get_debt_ratio_chart'),
    (r'^get_turnover_ratio_chart/$', 'get_turnover_ratio_chart'),
    (r'^get_interest_cover_chart/$', 'get_interest_cover_chart'),
    (r'^get_growth_rate_chart/$', 'get_growth_rate_chart'),

    (r'^venue_lookup/$','venue_lookup'),
    (r'^venue/$','venue'),
)

urlpatterns += patterns('stocks.views',
    (r'^update_stockid/$', 'update_stock_id'),
    (r'^update_dividend/$', 'update_dividend'),
    (r'^update_month_revenue/$', 'update_month_revenue'),
    (r'^check_month_revenue/$', 'check_month_revenue'),
    (r'^update_season_revenue/$', 'update_season_revenue'),
    (r'^test_month_revenue/$', 'test_month_revenue'),   
    (r'^update/$', 'update'),
)

urlpatterns += patterns('financial.views',
    (r'^update_season_financial_ratio/$', 'update_season_financial_ratio'),
    (r'^new_update_season_financial_ratio/$', 'update_season_financial_ratio'),
    (r'^update_year_financial_ratio/$', 'update_year_financial_ratio'),
    (r'^update_season_income_statement/$', 'update_season_income_statement'),
    (r'^update_year_income_statement/$', 'update_year_income_statement'),
    (r'^update_season_balance_sheet/$', 'update_season_balance_sheet'),
    (r'^show_season_balance_sheet/$', 'show_season_balance_sheet'),
    (r'^show_season_income_statement/$', 'show_season_income_statement'),
    (r'^show_statements_of_cashflows/$', 'show_statements_of_cashflows'),
    (r'^update_season_cashflow_statement/$', 'update_season_cashflow_statement'),
    (r'^update_year_cashflow_statement/$', 'update_year_cashflow_statement'),
)

urlpatterns += patterns('',
    url( r'^set_stockid/$', set_stockid, name = 'set_stockid'),
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
   
    
    # Examples:
    # url(r'^$', 'stock_analysis.views.home', name='home'),
    # url(r'^stock_analysis/', include('stock_analysis.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += patterns('filter.views',
    url(r'^filter/index/$', 'filter_index', name= 'filter_index'),
    url(r'^filter/start/$', 'filter_start', name= 'filter_start'),
    url(r'^filter/start2/$', 'filter_start2', name= 'filter_start2'),
    url(r'^filter/$', 'filter'),
    url(r'^filter/test/$', 'filter_test'),
    url(r'^filter_option/$', 'filter_option'),
    url(r'^filter_choice/$', 'filter_choice'),
    url(r'^tree_table/$', 'tree_table'),
    url(r'^test3/$', 'test3'),
    url(r'^test/$', 'test'),
)

urlpatterns += patterns('chip.views',
    url(r'^update_corp_trade/$', 'update_corp_trade'),
    url(r'^update_shareholder_structure/$', 'update_shareholder_structure'),
)

urlpatterns += patterns('price.views',
    url(r'^update_price/$', 'update_price'),
    url(r'^show_price/$', 'show_price'),
    url(r'^update_price_by_stockid/$', 'update_price_by_stockid'),
    url(r'^update_pivotal_state/$', 'update_pivotal_state'),
)

urlpatterns += patterns('reaserch.views',
    url(r'^chip_price_relation/$', 'chip_price_relation'),
)

urlpatterns += patterns('us_stocks.views',
    url( r'^us/update_finance/$', 'update_finance', name= 'us_update_finance'),
)
