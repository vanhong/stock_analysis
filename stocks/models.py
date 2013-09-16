from django.db import models

class StockId(models.Model):
    symbol = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=20)
    market_type = models.CharField(max_length=10)
    company_type = models.CharField(max_length=20)
     
    def __unicode__(self):
        return u'%s %s' % (self.symbol, self.name)

class Revenue(models.Model):
    surrogate_key = models.CharField(max_length=50, primary_key=True)
    symbol = models.CharField(max_length=20, db_index=True)
    year = models.IntegerField(db_index=True)
    season = models.IntegerField(db_index=True)
    month = models.IntegerField(db_index=True)
    time_type = models.CharField(max_length=2, db_index=True)
    name = models.CharField(max_length=50, db_index=True)
    value = models.CharField(max_length=20)

class RevenueName:
    def __init__(self):
        self.revenue = 'revenue'
        self.growth_rate = 'growth_rate'
        self.last_year_revenue = 'last_year_revenue'
        self.year_growth_rate = 'year_growth_rate'
        self.acc_revenue = 'acc_revenue'
        self.acc_year_growth_rate = 'acc_year_growth_rate'