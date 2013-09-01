from django.conf.urls import patterns, include, url
from django.conf.urls import *
"""from stock_analysis.views import test, site, home, analysis, set_stock_id, revenue
from stocks.views import update_stock_id, update_month_revenue, update_season_revenue
from financial.views import update_season_financial_ratio"""
import stock_analysis
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    (r'^home/index/$', 'stock_analysis.views.home'),
    (r'^analysis/$', 'stock_analysis.views.analysis'),
    (r'^revenue/month/$', 'stock_analysis.views.month_revenue'),
    (r'^revenue/season/$', 'stock_analysis.views.season_revenue'),
    (r'^update_stockid/$', 'stocks.views.update_stock_id'),
    (r'^update_month_revenue/$', 'stocks.views.update_month_revenue'),
    (r'^update_season_profit/$', 'stocks.views.update_season_profit'),
    (r'^update_season_financial_ratio/$', 'stocks.views.update_season_financial_ratio'),
    (r'^test/$', 'stock_analysis.views.test'),
    (r'^site/$', 'stock_analysis.views.site'),
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': stock_analysis.settings.STATIC_ROOT}),
    # Examples:
    # url(r'^$', 'stock_analysis.views.home', name='home'),
    # url(r'^stock_analysis/', include('stock_analysis.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
