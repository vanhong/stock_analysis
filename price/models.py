from django.db import models

# Create your models here.
class Price(models.Model):
    surrogate_key = models.CharField(max_length=20, primary_key=True)
    date = models.DateField(db_index=True)
    symbol = models.CharField(max_length=10, db_index=True)
    open_price = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    high_price = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    low_price = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    close_price = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    adj_close_price = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    volume = models.DecimalField(max_digits=20, decimal_places=0, null=True)

#class PivotalPoint(models.Model):
#	surrogate_key = models.CharField(max_length=20, primary_key=True)
#	date - 
