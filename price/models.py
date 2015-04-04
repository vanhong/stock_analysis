#!/usr/bin/python
# -*- coding: utf-8 -*-
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

class PivotalPoint(models.Model):
    surrogate_key = models.CharField(max_length=20, primary_key=True)
    date = models.DateField(db_index=True)
    symbol = models.CharField(max_length=10, db_index=True)
    price = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    state = models.CharField(max_length=20)
    prevState = models.CharField(max_length=20)
    # 上升趨勢關鍵點
    upward_trand_point = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    # 自然回檔關鍵點
    natural_reaction_point = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    # 下降趨勢關鍵點
    downward_trend_point = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    # 自然反彈關鍵點
    natural_rally_point = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    # 次級反彈關鍵點
    secondary_rally_point = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    # 次級回檔關鍵點
    secondary_reaction_point = models.DecimalField(max_digits=20, decimal_places=2, null=True)
