from django.db import models

# Create your models here.
class CorpTrade(models.Model):
    surrogate_key = models.CharField(max_length=20, primary_key=True)
    trade_date = models.IntegerField(db_index=True)
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

		