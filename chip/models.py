from django.db import models

# Create your models here.
class CorpTrade(models.Model):
    surrogate_key = models.CharField(max_length=20, primary_key=True)
    date = models.IntegerField(db_index=True)
    symbol = models.CharField(max_length=10, db_index=True)
    dealer_buy = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    dealer_sell = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    foreign_buy = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    foreign_sell = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    security_buy = models.DecimalField(max_digits=20, decimal_places=0, null=True)
    security_sell = models.DecimalField(max_digits=20, decimal_places=0, null=True)



class CorpTradeData():
    def __init__(self, key, txdate, symbol, dealer_buy,dealer_sell, foreign_buy, foreign_sell, security_buy, security_sell):
    	self.surrogate_key = key
    	self.trade_date = txdate
    	self.symbol = symbol
    	self.dealer_buy = dealer_buy
    	self.dealer_sell = dealer_sell
    	self.foreign_buy = foreign_buy
    	self.foreign_sell = foreign_sell
    	self.security_buy = security_buy
    	self.security_sell = security_sell

class ShareholderStructure(models.Model):
    surrogate_key = models.CharField(max_length=20, primary_key=True)
    date = models.IntegerField(db_index=True)
    symbol = models.CharField(max_length=10, db_index=True)
    data_kind = models.CharField(max_length=10, db_index=True) 
    value0_1 = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    value1_5 = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    value5_10 = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    value10_15 = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    value15_20 = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    value20_30 = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    value30_40 = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    value40_50 = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    value50_100 = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    value100_200 = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    value200_400 = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    value400_600 = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    value600_800 = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    value800_1000 = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    value1000 = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    value_sum = models.DecimalField(max_digits=20, decimal_places=2, null=True)

