from django.conf.urls import patterns, include, url
from django.conf.urls import *
from django.conf import settings
from stock_analysis.views import ajax_user_search, set_stockid
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('stock_analysis.views',
    (r'^home/index/$', 'home'),
    (r'^analysis/$', 'month_revenue'),
    (r'^revenue/month/$', 'month_revenue'),
    (r'^revenue/season/$', 'season_revenue'),
    (r'^dividend/$', 'dividend'),
    (r'^profitability/$', 'profitability'),
    (r'^getRevenueChart/$', 'getRevenueChart'),
    (r'^getDividendChart/$', 'getDividendChart'),
    (r'^getProfitabilityChart/$', 'getProfitabilityChart'),
)

urlpatterns += patterns('stocks.views',
    (r'^update_stockid/$', 'update_stock_id'),
    (r'^update_dividend/$', 'update_dividend'),
    (r'^update_month_revenue/$', 'update_month_revenue'),
)

urlpatterns += patterns('financial.views',
    (r'^update_season_financial_ratio/$', 'update_season_financial_ratio'),
    (r'^update_season_balance_sheet/$', 'update_season_balance_sheet'),
)

urlpatterns += patterns('',
    url( r'^set_stockid/$', set_stockid, name = 'set_stockid'),
<<<<<<< HEAD
    (r'^revenue/month/$', 'stock_analysis.views.month_revenue'),
    (r'^revenue/season/$', 'stock_analysis.views.season_revenue'),
    (r'^dividend/$', 'stock_analysis.views.dividend'),
    (r'^profitability/$', 'stock_analysis.views.profitability'),
    (r'^update_stockid/$', 'stocks.views.update_stock_id'),
    (r'^update_dividend/$', 'stocks.views.update_dividend'),
    (r'^update_month_revenue/$', 'stocks.views.update_month_revenue'),
    (r'^update_corp_trade/$', 'chip.views.update_corp_trade'),
    (r'^update_price/$', 'price.views.update_price'),
    (r'^site/$', 'stock_analysis.views.site'),
=======
>>>>>>> a01702b32d4d24d8177f96b699c8e73ef30255bf
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
   
    
    # Examples:
    # url(r'^$', 'stock_analysis.views.home', name='home'),
    # url(r'^stock_analysis/', include('stock_analysis.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += patterns('stock_analysis.views',
    url( r'^filter/index/$', 'filter_index', name= 'filter_index'),
    url( r'^filter/start/$', 'filter_start', name= 'filter_start'),
)
