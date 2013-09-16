from django.conf.urls import patterns, include, url
from django.conf.urls import *
from django.conf import settings
from stock_analysis.views import ajax_user_search, set_stockid, testStockid
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    (r'^home/index/$', 'stock_analysis.views.home'),
    (r'^analysis/$', 'stock_analysis.views.analysis'),
    url( r'^set_stockid/$', set_stockid, name = 'set_stockid'),
    (r'^revenue/month/$', 'stock_analysis.views.month_revenue'),
    (r'^revenue/season/$', 'stock_analysis.views.season_revenue'),
    (r'^update_stockid/$', 'stocks.views.update_stock_id'),
    (r'^update_month_revenue/$', 'stocks.views.update_month_revenue'),
    (r'^update_revenue/$', 'stocks.views.update_revenue'),
    (r'^update_season_profit/$', 'stocks.views.update_season_profit'),
    url(r'^test/$', 'stock_analysis.views.test'),
    url(r'^testStockid/$', 'stock_analysis.views.testStockid'),
    (r'^site/$', 'stock_analysis.views.site'),
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
    url( r'^hello/^$', 'stock_analysis.views.index', name = 'demo_index' ),
    url( r'^user/$', ajax_user_search, name = 'demo_user_search' ),
    # Examples:
    # url(r'^$', 'stock_analysis.views.home', name='home'),
    # url(r'^stock_analysis/', include('stock_analysis.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
