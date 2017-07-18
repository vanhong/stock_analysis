#!/usr/bin/python
# -*- coding: utf-8 -*-

from price.models import *
from datetime import *
import pdb
from decimal import Decimal

INIT_PIVOTAL_STATE = 'init_pivotal_state'
UPWARD_TREND_STATE = 'upward_trend_state'
DOWNWARD_TREND_STATE = 'downward_trend_state'
NATURAL_REACTION_STATE = 'natural_reaction_state'
NATURAL_RALLY_STATE = 'natural_rally_state'
SECONDARY_REACTION_STATE = 'secondary_reaction_state'
SECONDARY_RALLY_STATE = 'secondary_rally_state'

class PivotalState:
	def __init__(self, date, price, symbol, prev_state, upward_trend, downward_trend, natural_reaction, 
		natural_rally, secondary_rally, secondary_reaction):
		self.date = date
		self.symbol = symbol
		self.price = price
		self.prev_state = prev_state
		self.upward_trend_point = upward_trend
		self.downward_trend_point = downward_trend
		self.natural_reaction_point = natural_reaction
		self.natural_rally_point = natural_rally
		self.secondary_rally_point = secondary_rally
		self.secondary_reaction_point = secondary_reaction
	def next(self, price, date):
		assert 0, "next not implemented"
	def save_to_db(self):
		state = PivotalPoint2()
		state.surrogate_key = self.symbol + '_' + self.date
		state.date = self.date
		state.symbol = self.symbol
		state.price = self.price
		state.state = self.state
		state.prev_state = self.prev_state
		state.upward_trend_point = self.upward_trend_point
		state.downward_trend_point = self.downward_trend_point
		state.natural_reaction_point = self.natural_reaction_point
		state.natural_rally_point = self.natural_rally_point
		state.secondary_reaction_point = self.secondary_reaction_point
		state.secondary_rally_point = self.secondary_rally_point
		state.save()

class InitPivotalState(PivotalState):
	def __init__(self, date, price, symbol, prev_state, upward_trend, downward_trend, natural_reaction, 
		natural_rally, secondary_rally, secondary_reaction):
		self.date = date
		self.symbol = symbol
		self.price = price
		self.prev_state = prev_state
		self.upward_trend_point = upward_trend
		self.downward_trend_point = downward_trend
		self.natural_reaction_point = natural_reaction
		self.natural_rally_point = natural_rally
		self.secondary_rally_point = secondary_rally
		self.secondary_reaction_point = secondary_reaction
		#super(InitPivotalState, self).__init__(date, price, symbol, prev_state, upward_trend, downward_trend, natural_reaction, 
		#natural_rally, secondary_rally, secondary_reaction)
		self.state = INIT_PIVOTAL_STATE
	def next(self, price, date):
		# 初始化關鍵點
		if (self.upward_trend_point == 0 and self.downward_trend_point == 0):
			return InitPivotalState(date=date, price=price, symbol=self.symbol, prev_state=self.prev_state, 
									upward_trend=price, downward_trend=price, 
									natural_reaction=0, natural_rally=0, 
									secondary_rally=0, secondary_reaction=0)
		# 價格超過最初價格的10% => 上升趨勢
		if (price >= self.upward_trend_point * Decimal(1.1) and self.upward_trend_point > 0):
			return UpwardTrendState(date=date, price=price, symbol=self.symbol, prev_state=self.state, 
									upward_trend=price, downward_trend=self.downward_trend_point, 
									natural_reaction=self.natural_reaction_point, natural_rally=self.natural_rally_point, 
									secondary_rally=self.secondary_rally_point, secondary_reaction=self.secondary_reaction_point)
		# 價格低於最初價格的10% => 下降趨勢
		if (price <= self.downward_trend_point * Decimal(0.9) and self.downward_trend_point > 0):
			return DownwardTrendState(date=date, price=price, symbol=self.symbol, prev_state=self.state, 
									upward_trend=self.upward_trend_point, downward_trend=price, 
									natural_reaction=self.natural_reaction_point, natural_rally=self.natural_rally_point, 
									secondary_rally=self.secondary_rally_point, secondary_reaction=self.secondary_reaction_point)
		return InitPivotalState(date=date, price=price, symbol=self.symbol, prev_state=self.prev_state, 
									upward_trend=self.upward_trend_point, downward_trend=self.downward_trend_point, 
									natural_reaction=self.natural_reaction_point, natural_rally=self.natural_rally_point, 
									secondary_rally=self.secondary_rally_point, secondary_reaction=self.secondary_reaction_point)

class UpwardTrendState(PivotalState):
	def __init__(self, date, price, symbol, prev_state, upward_trend, downward_trend, natural_reaction, 
		natural_rally, secondary_rally, secondary_reaction):
		self.date = date
		self.symbol = symbol
		self.price = price
		self.prev_state = prev_state
		self.upward_trend_point = upward_trend
		self.downward_trend_point = downward_trend
		self.natural_reaction_point = natural_reaction
		self.natural_rally_point = natural_rally
		self.secondary_rally_point = secondary_rally
		self.secondary_reaction_point = secondary_reaction
		self.state = UPWARD_TREND_STATE
	def next(self, price, date):
		# 價格突破上升趨勢關鍵點，持續記錄
		if (price >= self.upward_trend_point and self.upward_trend_point > 0):
			return UpwardTrendState(date=date, price=price, symbol=self.symbol, prev_state=self.prev_state, 
									upward_trend=price, downward_trend=self.downward_trend_point, 
									natural_reaction=self.natural_reaction_point, natural_rally=self.natural_rally_point, 
									secondary_rally=self.secondary_rally_point, secondary_reaction=self.secondary_reaction_point)
		# 價格低於上升趨勢關鍵點10% => 自然回檔
		if (price <= self.upward_trend_point * Decimal(0.9) and self.upward_trend_point > 0):
			return NaturalReactionState(date=date, price=price, symbol=self.symbol, prev_state=self.state, 
									upward_trend=self.upward_trend_point, downward_trend=self.downward_trend_point, 
									natural_reaction=price, natural_rally=self.natural_rally_point, 
									secondary_rally=self.secondary_rally_point, secondary_reaction=self.secondary_reaction_point)
		return UpwardTrendState(date=date, price=price, symbol=self.symbol, prev_state=self.prev_state, 
								upward_trend=self.upward_trend_point, downward_trend=self.downward_trend_point, 
								natural_reaction=self.natural_reaction_point, natural_rally=self.natural_rally_point, 
								secondary_rally=self.secondary_rally_point, secondary_reaction=self.secondary_reaction_point)

class DownwardTrendState(PivotalState):
	def __init__(self, date, price, symbol, prev_state, upward_trend, downward_trend, natural_reaction, 
		natural_rally, secondary_rally, secondary_reaction):
		self.date = date
		self.symbol = symbol
		self.price = price
		self.prev_state = prev_state
		self.upward_trend_point = upward_trend
		self.downward_trend_point = downward_trend
		self.natural_reaction_point = natural_reaction
		self.natural_rally_point = natural_rally
		self.secondary_rally_point = secondary_rally
		self.secondary_reaction_point = secondary_reaction
		self.state = DOWNWARD_TREND_STATE
	def next(self, price, date):
		# 價格跌破下降趨勢關鍵點，持續記錄
		if (price <= self.downward_trend_point and self.downward_trend_point > 0):
			return DownwardTrendState(date=date, price=price, symbol=self.symbol, prev_state=self.prev_state, 
								upward_trend=self.upward_trend_point, downward_trend=price, 
								natural_reaction=self.natural_reaction_point, natural_rally=self.natural_rally_point, 
								secondary_rally=self.secondary_rally_point, secondary_reaction=self.secondary_reaction_point)
		# 價格高於下降趨勢關鍵點10% => 自然反彈
		if (price >= self.downward_trend_point * Decimal(1.1) and self.downward_trend_point > 0):
			return NaturalRallyState(date=date, price=price, symbol=self.symbol, prev_state=self.state, 
								upward_trend=self.upward_trend_point, downward_trend=self.downward_trend_point, 
								natural_reaction=self.natural_reaction_point, natural_rally=price, 
								secondary_rally=self.secondary_rally_point, secondary_reaction=self.secondary_reaction_point)
		return DownwardTrendState(date=date, price=price, symbol=self.symbol, prev_state=self.prev_state, 
								upward_trend=self.upward_trend_point, downward_trend=self.downward_trend_point, 
								natural_reaction=self.natural_reaction_point, natural_rally=self.natural_rally_point, 
								secondary_rally=self.secondary_rally_point, secondary_reaction=self.secondary_reaction_point)

# 自然反彈
class NaturalRallyState(PivotalState):
	def __init__(self, date, price, symbol, prev_state, upward_trend, downward_trend, natural_reaction, 
		natural_rally, secondary_rally, secondary_reaction):
		self.date = date
		self.symbol = symbol
		self.price = price
		self.prev_state = prev_state
		self.upward_trend_point = upward_trend
		self.downward_trend_point = downward_trend
		self.natural_reaction_point = natural_reaction
		self.natural_rally_point = natural_rally
		self.secondary_rally_point = secondary_rally
		self.secondary_reaction_point = secondary_reaction
		self.state = NATURAL_RALLY_STATE
	def next(self, price, date):
		# 價格高於自然反彈最後一個數字 5% => 上升趨勢, 並將自然反彈關鍵點設為0 (前一個狀態是次級反彈)
		# 價格高於上升趨勢最後一個數字 => 上升趨勢, 並將自然反彈關鍵點設為0
		if ((price >= self.natural_rally_point * Decimal(1.05) and self.prev_state == SECONDARY_RALLY_STATE and self.natural_rally_point > 0) \
			or (price >= self.upward_trend_point and self.upward_trend_point > 0)):
			return UpwardTrendState(date=date, price=price, symbol=self.symbol, prev_state=self.state, 
								upward_trend=price, downward_trend=self.downward_trend_point, 
								natural_reaction=0, natural_rally=self.natural_rally_point, 
								secondary_rally=self.secondary_rally_point, secondary_reaction=self.secondary_reaction_point)
		# 價格高於自然反彈最後一個數字 => 記錄自然反彈關鍵點 (前一個狀態不能是次級反彈)
		if (price >= self.natural_rally_point and self.prev_state != SECONDARY_RALLY_STATE and self.natural_rally_point > 0):
			return NaturalRallyState(date=date, price=price, symbol=self.symbol, prev_state=self.prev_state, 
								upward_trend=self.upward_trend_point, downward_trend=self.downward_trend_point, 
								natural_reaction=self.natural_reaction_point, natural_rally=price, 
								secondary_rally=self.secondary_rally_point, secondary_reaction=self.secondary_reaction_point)
		# 價格低於自然反彈最後一個數字 10% => 次級回檔或
		# 							      自然回檔或(如果價格低於自然回檔關鍵點)
		# 								  下降趨勢(如果價格低於下降趨勢關鍵點, 並將自然回檔關鍵點設為0)

		if (price <= self.natural_rally_point * Decimal(0.9) and self.natural_rally_point > 0):
			if (price <= self.downward_trend_point and self.downward_trend_point > 0):
				return DownwardTrendState(date=date, price=price, symbol=self.symbol, prev_state=self.state, 
								upward_trend=self.upward_trend_point, downward_trend=price, 
								natural_reaction=self.natural_reaction_point, natural_rally=self.natural_rally_point, 
								secondary_rally=self.secondary_rally_point, secondary_reaction=self.secondary_reaction_point)
			if (self.prev_state == DOWNWARD_TREND_STATE):
				return NaturalReactionState(date=date, price=price, symbol=self.symbol, prev_state=self.state, 
								upward_trend=self.upward_trend_point, downward_trend=self.downward_trend_point, 
								natural_reaction=price, natural_rally=self.natural_rally_point, 
								secondary_rally=self.secondary_rally_point, secondary_reaction=self.secondary_reaction_point)
			return SecondaryReactionState(date=date, price=price, symbol=self.symbol, prev_state=self.state, 
								upward_trend=self.upward_trend_point, downward_trend=self.downward_trend_point, 
								natural_reaction=self.natural_reaction_point, natural_rally=self.natural_rally_point, 
								secondary_rally=self.secondary_rally_point, secondary_reaction=price)
		return NaturalRallyState(date=date, price=price, symbol=self.symbol, prev_state=self.prev_state, 
								upward_trend=self.upward_trend_point, downward_trend=self.downward_trend_point, 
								natural_reaction=self.natural_reaction_point, natural_rally=self.natural_rally_point, 
								secondary_rally=self.secondary_rally_point, secondary_reaction=self.secondary_reaction_point)

# 自然回檔
class NaturalReactionState(PivotalState):
	def __init__(self, date, price, symbol, prev_state, upward_trend, downward_trend, natural_reaction, 
		natural_rally, secondary_rally, secondary_reaction):
		self.date = date
		self.symbol = symbol
		self.price = price
		self.prev_state = prev_state
		self.upward_trend_point = upward_trend
		self.downward_trend_point = downward_trend
		self.natural_reaction_point = natural_reaction
		self.natural_rally_point = natural_rally
		self.secondary_rally_point = secondary_rally
		self.secondary_reaction_point = secondary_reaction
		self.state = NATURAL_REACTION_STATE
	def next(self, price, date):
		# 價格低於自然回檔最後一個數字 5% => 下降趨勢，並將自然回檔關鍵點設為0 (前一個狀態是次級回檔)
		# 價格低於下降趨勢最後一個數字 => 下降趨勢, 並將自然回檔關鍵點設為0
		if ((price <= self.natural_reaction_point * Decimal(0.95) and self.prev_state == SECONDARY_REACTION_STATE and self.natural_reaction_point > 0) \
			or (price <= self.downward_trend_point and self.downward_trend_point > 0)):
			return DownwardTrendState(date=date, price=price, symbol=self.symbol, prev_state=self.state, 
								upward_trend=self.upward_trend_point, downward_trend=price, 
								natural_reaction=self.natural_reaction_point, natural_rally=0, 
								secondary_rally=self.secondary_rally_point, secondary_reaction=self.secondary_reaction_point)
		# 價格低於自然回檔最後一個數字 => 記錄自然回檔關鍵點 (前一個狀態不能是次級回檔)
		if (price <= self.natural_reaction_point and self.prev_state != SECONDARY_REACTION_STATE and self.natural_reaction_point > 0):
			return NaturalReactionState(date=date, price=price, symbol=self.symbol, prev_state=self.prev_state, 
								upward_trend=self.upward_trend_point, downward_trend=self.downward_trend_point, 
								natural_reaction=price, natural_rally=self.natural_rally_point, 
								secondary_rally=self.secondary_rally_point, secondary_reaction=self.secondary_reaction_point)
		# 價格高於自然回檔最後一個數字 10% => 次級反彈或
		# 								   自然反彈或(如果價格高於自然反彈關鍵點)
		#  								   上升趨勢(如果價格高於上升趨勢關鍵點, 並將自然反彈關鍵點設為0)
		if (price >= self.natural_reaction_point * Decimal(1.1) and self.natural_reaction_point > 0):
			if (price >= self.upward_trend_point):
				return UpwardTrendState(date=date, price=price, symbol=self.symbol, prev_state=self.state, 
								upward_trend=price, downward_trend=self.downward_trend_point, 
								natural_reaction=self.natural_reaction_point, natural_rally=self.natural_rally_point, 
								secondary_rally=self.secondary_rally_point, secondary_reaction=self.secondary_reaction_point)
			if (self.prev_state == UPWARD_TREND_STATE):
				return NaturalRallyState(date=date, price=price, symbol=self.symbol, prev_state=self.state, 
								upward_trend=self.upward_trend_point, downward_trend=self.downward_trend_point, 
								natural_reaction=self.natural_reaction_point, natural_rally=price, 
								secondary_rally=self.secondary_rally_point, secondary_reaction=self.secondary_reaction_point)
			return SecondaryRallyState(date=date, price=price, symbol=self.symbol, prev_state=self.state, 
								upward_trend=self.upward_trend_point, downward_trend=self.downward_trend_point, 
								natural_reaction=self.natural_reaction_point, natural_rally=self.natural_rally_point, 
								secondary_rally=price, secondary_reaction=self.secondary_reaction_point)
		return NaturalReactionState(date=date, price=price, symbol=self.symbol, prev_state=self.prev_state, 
								upward_trend=self.upward_trend_point, downward_trend=self.downward_trend_point, 
								natural_reaction=self.natural_reaction_point, natural_rally=self.natural_rally_point, 
								secondary_rally=self.secondary_rally_point, secondary_reaction=self.secondary_reaction_point)

#次級反彈
class SecondaryRallyState(PivotalState):
	def __init__(self, date, price, symbol, prev_state, upward_trend, downward_trend, natural_reaction, 
		natural_rally, secondary_rally, secondary_reaction):
		self.date = date
		self.symbol = symbol
		self.price = price
		self.prev_state = prev_state
		self.upward_trend_point = upward_trend
		self.downward_trend_point = downward_trend
		self.natural_reaction_point = natural_reaction
		self.natural_rally_point = natural_rally
		self.secondary_rally_point = secondary_rally
		self.secondary_reaction_point = secondary_reaction
		self.state = SECONDARY_RALLY_STATE
	def next(self, price, date):
		# 股價高過上升趨勢關鍵點 => 上升趨勢
		if (price >= self.upward_trend_point and self.upward_trend_point > 0):
			return UpwardTrendState(date=date, price=price, symbol=self.symbol, prev_state=self.state, 
								upward_trend=price, downward_trend=self.downward_trend_point, 
								natural_reaction=self.natural_reaction_point, natural_rally=0, 
								secondary_rally=self.secondary_rally_point, secondary_reaction=self.secondary_reaction_point)
		# 股價高過自然反彈關鍵點 => 自然反彈
		if (price >= self.natural_rally_point and self.natural_rally_point > 0):
			return NaturalRallyState(date=date, price=price, symbol=self.symbol, prev_state=self.state, 
								upward_trend=self.upward_trend_point, downward_trend=self.downward_trend_point, 
								natural_reaction=self.natural_reaction_point, natural_rally=price, 
								secondary_rally=self.secondary_rally_point, secondary_reaction=self.secondary_reaction_point)
		# 股價低於次級反彈最後一個數字 10% => 次級回檔
		if (price <= self.secondary_rally_point * Decimal(0.9) and self.secondary_rally_point > 0):
			return SecondaryReactionState(date=date, price=price, symbol=self.symbol, prev_state=self.state, 
								upward_trend=self.upward_trend_point, downward_trend=self.downward_trend_point, 
								natural_reaction=self.natural_reaction_point, natural_rally=self.natural_rally_point, 
								secondary_rally=self.secondary_rally_point, secondary_reaction=price)
		if (price >= self.secondary_rally_point and self.secondary_rally_point > 0):
			return SecondaryRallyState(date=date, price=price, symbol=self.symbol, prev_state=self.prev_state, 
								upward_trend=self.upward_trend_point, downward_trend=self.downward_trend_point, 
								natural_reaction=self.natural_reaction_point, natural_rally=self.natural_rally_point, 
								secondary_rally=price, secondary_reaction=self.secondary_reaction_point)
		return SecondaryRallyState(date=date, price=price, symbol=self.symbol, prev_state=self.prev_state, 
								upward_trend=self.upward_trend_point, downward_trend=self.downward_trend_point, 
								natural_reaction=self.natural_reaction_point, natural_rally=self.natural_rally_point, 
								secondary_rally=self.secondary_rally_point, secondary_reaction=self.secondary_reaction_point)

#次級回檔
class SecondaryReactionState(PivotalState):
	def __init__(self, date, price, symbol, prev_state, upward_trend, downward_trend, natural_reaction, 
		natural_rally, secondary_rally, secondary_reaction):
		self.date = date
		self.symbol = symbol
		self.price = price
		self.prev_state = prev_state
		self.upward_trend_point = upward_trend
		self.downward_trend_point = downward_trend
		self.natural_reaction_point = natural_reaction
		self.natural_rally_point = natural_rally
		self.secondary_rally_point = secondary_rally
		self.secondary_reaction_point = secondary_reaction
		self.state = SECONDARY_REACTION_STATE
	def next(self, price, date):
		# 股價低過下降趨勢關鍵點 => 下降趨勢
		if (price <= self.downward_trend_point and self.downward_trend_point > 0):
			return DownwardTrendState(date=date, price=price, symbol=self.symbol, prev_state=self.state, 
									upward_trend=self.upward_trend_point, downward_trend=price, 
									natural_reaction=0, natural_rally=self.natural_rally_point, 
									secondary_rally=self.secondary_rally_point, secondary_reaction=self.secondary_reaction_point)
		# 股價低過自然回檔關鍵點 => 自然回檔
		if (price <= self.natural_reaction_point and self.natural_reaction_point > 0):
			return NaturalReactionState(date=date, price=price, symbol=self.symbol, prev_state=self.state, 
									upward_trend=self.upward_trend_point, downward_trend=self.downward_trend_point, 
									natural_reaction=price, natural_rally=self.natural_rally_point, 
									secondary_rally=self.secondary_rally_point, secondary_reaction=self.secondary_reaction_point)
		# 股價高於次級回檔最後一個數字 10% => 次級反彈
		if (price >= self.secondary_reaction_point * Decimal(1.1) and self.secondary_reaction_point > 0):
			return SecondaryRallyState(date=date, price=price, symbol=self.symbol, prev_state=self.state, 
								upward_trend=self.upward_trend_point, downward_trend=self.downward_trend_point, 
								natural_reaction=self.natural_reaction_point, natural_rally=self.natural_rally_point, 
								secondary_rally=price, secondary_reaction=self.secondary_reaction_point)
		if (price <= self.secondary_reaction_point and self.secondary_reaction_point > 0):
			return SecondaryReactionState(date=date, price=price, symbol=self.symbol, prev_state=self.prev_state, 
								upward_trend=self.upward_trend_point, downward_trend=self.downward_trend_point, 
								natural_reaction=self.natural_reaction_point, natural_rally=self.natural_rally_point, 
								secondary_rally=self.secondary_rally_point, secondary_reaction=price)
		return SecondaryReactionState(date=date, price=price, symbol=self.symbol, prev_state=self.prev_state, 
								upward_trend=self.upward_trend_point, downward_trend=self.downward_trend_point, 
								natural_reaction=self.natural_reaction_point, natural_rally=self.natural_rally_point, 
								secondary_rally=self.secondary_rally_point, secondary_reaction=self.secondary_reaction_point)







