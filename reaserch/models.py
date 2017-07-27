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

class WawaValueLine(models.Model):
	surrogate_key = models.CharField(max_length=20, primary_key=True)
	symbol = models.CharField(max_length=20, db_index=True)
	year = models.IntegerField(db_index=True)
	season = models.IntegerField(db_index=True)
	date = models.DateField(db_index=True)
	last_year_eps = models.DecimalField(max_digits=10, decimal_places=2, null=False)
	future_eps_growth = models.DecimalField(max_digits=10, decimal_places=2, null=False)
	past_pe = models.DecimalField(max_digits=10, decimal_places=2, null=False)
	estimate_eps = models.DecimalField(max_digits=10, decimal_places=2, null=False)
	estimate_future_price = models.DecimalField(max_digits=10, decimal_places=2, null=False)
	estimate_price = models.DecimalField(max_digits=10, decimal_places=2, null=False)
	hold_price = models.DecimalField(max_digits=10, decimal_places=2, null=False)
	avg_dividend = models.DecimalField(max_digits=10, decimal_places=2, null=False)
	low_price = models.DecimalField(max_digits=10, decimal_places=2, null=False)
	high_price = models.DecimalField(max_digits=10, decimal_places=2, null=False)
	one_low_price = models.DecimalField(max_digits=10, decimal_places=2, null=False)
	recovery_years = models.DecimalField(max_digits=10, decimal_places=2, null=False)

class AvgPE(models.Model):
	surrogate_key = models.CharField(max_length=20, primary_key=True)
	symbol = models.CharField(max_length=20, db_index=True)
	year = models.IntegerField(db_index=True)
	date = models.DateField(db_index=True)
	low_price = models.DecimalField(max_digits=10, decimal_places=2, null=False)
	high_price = models.DecimalField(max_digits=10, decimal_places=2, null=False)
	eps = models.DecimalField(max_digits=10, decimal_places=2, null=False)
	pe = models.DecimalField(max_digits=10, decimal_places=2, null=False)