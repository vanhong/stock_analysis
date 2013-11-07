﻿from django.conf.urls import patterns, include, url
from django.conf.urls import *
from django.conf import settings
from stock_analysis.views import set_stockid
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('stock_analysis.views',
    (r'^analysis/$', 'analysis', {'template_name': 'revenue.html', 'drawTool': 'new Revenue.Tool();'}),
    (r'^revenue/$', 'analysis', {'template_name': 'revenue.html', 'drawTool': 'new Revenue.Tool();'}),
    (r'^dividend/$', 'analysis', {'template_name': 'dividend.html', 'drawTool': 'new Revenue.Tool();'}),
    (r'^profitability/$', 'analysis', {'template_name': 'profitability.html', 'drawTool': 'new Revenue.Tool();'}),
    (r'^performance_per_share/$', 'analysis', {'template_name': 'performance_per_share.html', 'drawTool': 'new Revenue.Tool();'}),
    (r'^season_roe/$', 'analysis', {'template_name': 'roe_roa.html', 'drawTool': 'new Revenue.Tool();'}),

    (r'^performance_per_share_table/$', 'performance_per_share_table'),
    (r'^getRevenueChart/$', 'getRevenueChart'),
    (r'^getSeasonRevenueChart/$', 'getSeasonRevenueChart'),
    (r'^getSeasonProfitChart/$', 'getSeasonProfitChart'),
    (r'^getDividendChart/$', 'getDividendChart'),
    (r'^getProfitabilityChart/$', 'getProfitabilityChart'),
    (r'^get_performance_per_share/$', 'get_performance_per_share'),
    (r'^month_revenue/$', 'month_revenue'),
    (r'^season_revenue/$', 'season_revenue'),
    (r'^season_profit/$', 'season_profit'),
    (r'^dividend_table/$', 'dividend_table'),
    (r'^season_profitability/$', 'season_profitability'),
    
    (r'^season_roe_table/$', 'season_roe_table'),
    (r'^get_season_roe_chart/$', 'get_season_roe_chart'),
)

urlpatterns += patterns('stocks.views',
    (r'^update_stockid/$', 'update_stock_id'),
    (r'^update_dividend/$', 'update_dividend'),
    (r'^update_month_revenue/$', 'update_month_revenue'),
    (r'^update_season_profit/$', 'update_season_profit'),
    (r'^update_season_revenue/$', 'update_season_revenue'),
)

urlpatterns += patterns('financial.views',
    (r'^update_season_financial_ratio/$', 'update_season_financial_ratio'),
    (r'^update_season_income_statement/$', 'update_season_income_statement'),
    (r'^update_season_balance_sheet/$', 'update_season_balance_sheet'),
    (r'^show_season_balance_sheet/$', 'show_season_balance_sheet'),
    (r'^show_season_income_statement/$', 'show_season_income_statement'),
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
    url( r'^filter/index/$', 'filter_index', name= 'filter_index'),
    url( r'^filter/start/$', 'filter_start', name= 'filter_start'),
    url( r'^filter/test/$', 'query_gross_profit_margin_gtn_pre_avg'),
)

urlpatterns += patterns('us_stocks.views',
    url( r'^us/update_finance/$', 'update_finance', name= 'us_update_finance'),
)
