#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.db import models

# Create your models here.
class WawaGrowthPower(models.Model):
	surrogate_key = models.CharField(max_length=20, primary_key=True)
	symbol = models.CharField(max_length=20, db_index=True)
	year = models.IntegerField(db_index=True)
	season = models.IntegerField(db_index=True)
	date = models.DateField(db_index=True)
	reasonable_price = models.DecimalField(max_digits=10, decimal_places=2, null=False)
	estimate_growth_rate = models.DecimalField(max_digits=10, decimal_places=2, null=False)
	estimate_eps = models.DecimalField(max_digits=10, decimal_places=2, null=False)
	last_year_eps = models.DecimalField(max_digits=10, decimal_places=2, null=False)
	season_eps = models.DecimalField(max_digits=10, decimal_places=2, null=False)
	last_year_season_eps = models.DecimalField(max_digits=10, decimal_places=2, null=False)

class VKGrowthPower(models.Model):
	surrogate_key = models.CharField(max_length=20, primary_key=True)
	symbol = models.CharField(max_length=20, db_index=True)
	year = models.IntegerField(db_index=True)
	season = models.IntegerField(db_index=True)
	date = models.DateField(db_index=True)
	reasonable_price = models.DecimalField(max_digits=10, decimal_places=2, null=False)
	estimate_growth_rate = models.DecimalField(max_digits=10, decimal_places=2, null=False)
	estimate_eps = models.DecimalField(max_digits=10, decimal_places=2, null=False)
	last_year_eps = models.DecimalField(max_digits=10, decimal_places=2, null=False)
	season_eps = models.DecimalField(max_digits=10, decimal_places=2, null=False)
	last_year_season_eps = models.DecimalField(max_digits=10, decimal_places=2, null=False)