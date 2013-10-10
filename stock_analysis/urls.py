from django.conf.urls import patterns, include, url
from django.conf.urls import *
from django.conf import settings
from stock_analysis.views import ajax_user_search, set_stockid
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    (r'^home/index/$', 'stock_analysis.views.home'),
    (r'^analysis/$', 'stock_analysis.views.month_revenue'),
    url( r'^set_stockid/$', set_stockid, name = 'set_stockid'),
    (r'^revenue/month/$', 'stock_analysis.views.month_revenue'),
    (r'^revenue/season/$', 'stock_analysis.views.season_revenue'),
    (r'^dividend/$', 'stock_analysis.views.dividend'),
    (r'^profitability/$', 'stock_analysis.views.profitability'),
    (r'^update_stockid/$', 'stocks.views.update_stock_id'),
    (r'^update_dividend/$', 'stocks.views.update_dividend'),
    (r'^update_month_revenue/$', 'stocks.views.update_month_revenue'),
    (r'^site/$', 'stock_analysis.views.site'),
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
    (r'^getRevenueChart/$', 'stock_analysis.views.getRevenueChart'),
    (r'^getDividendChart/$', 'stock_analysis.views.getDividendChart'),
    (r'^update_season_financial_ratio/$', 'financial.views.update_season_financial_ratio'),
    # Examples:
    # url(r'^$', 'stock_analysis.views.home', name='home'),
    # url(r'^stock_analysis/', include('stock_analysis.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
