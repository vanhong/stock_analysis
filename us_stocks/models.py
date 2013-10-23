from django.db import models

class Finance(models.Model):
    surrogate_key = models.CharField(max_length=100, primary_key=True)
    symbol = models.CharField(max_length=20, db_index=True)
    date = models.IntegerField(db_index=True)
    time_type = models.CharField(max_length=2, db_index=True)
    name = models.CharField(max_length=50, db_index=True)
    value = models.CharField(max_length=20)