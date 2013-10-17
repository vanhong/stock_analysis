from django.db import models

# Create your models here.
class Price(models.Model):
    surrogate_key = models.CharField(max_length=20, primary_key=True)
    trade_date = models.IntegerField(db_index=True)
    symbol = models.CharField(max_length=10, db_index=True)
    openp = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    highp = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    lowp = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    closep = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    adjp = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    quantity = models.DecimalField(max_digits=20, decimal_places=0, null=True)


