from django.db import models

class StockId(models.Model):
    symbol = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=20)
    market_type = models.CharField(max_length=10)
    company_type = models.CharField(max_length=20)
     
    def __unicode__(self):
        return u'%s %s' % (self.symbol, sylf.name)

class MonthRevenue(models.Model):
    surrogate_key = models.CharField(max_length=20, primary_key=True)
    year = models.IntegerField(db_index=True)
    month = models.IntegerField(db_index=True)
    symbol = models.CharField(max_length=20, db_index=True)
    revenue = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    month_growth_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    last_year_revenue = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    year_growth_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    acc_revenue = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    acc_year_growth_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True)

    def __unicode__(self):
        return u"%d%d %s" % (self.year, self.month, self.symbol)

class SeasonRevenue(models.Model):
    surrogate_key =  models.CharField(max_length=20, primary_key=True)
    year = models.IntegerField(db_index=True)
    season = models.IntegerField(db_index=True)
    symbol = models.CharField(max_length=20, db_index=True)
    profit = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    season_growth_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    last_year_profit = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    year_growth_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    acc_profit = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    acc_year_growth_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True)

