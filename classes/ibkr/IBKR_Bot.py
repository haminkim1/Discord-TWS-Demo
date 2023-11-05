from ibapi.contract import Contract, ContractDetails
from ibapi.order import *
from ibapi.execution import ExecutionFilter

import threading
import time

from classes.discord.Options_Contract import Options_Contract
from classes.ibkr.IBapi import IBapi
from classes.ibkr.PositionInfo import PositionInfo
from classes.ibkr.TradeLogInfo import TradeLogInfo
from config.config import ibapi_port_no

class IBKR_Trade_Bot():

	def __init__(self):
		self.app = IBapi()
		self.init_for_next_trade()

	
	def init_for_next_trade(self):
		self.order_failed = False
		self._options_contract = None

		self.app.positions = []
		self.app.positionEnd_callback_finished = False


	def run_loop(self):
		self.app.run()


	def turn_on_API(self):
		self.app.connect('127.0.0.1', ibapi_port_no(), 123)
		self.app.nextorderId = None

		#Start the socket in a thread
		api_thread = threading.Thread(target=self.run_loop, daemon=True)
		api_thread.start()

		#Check if the API is connected via orderid
		timer = 0
		while True and timer != 5:
			if isinstance(self.app.nextorderId, int):
				print('connected')
				print()
				break
			else:
				print('waiting for connection')
				timer += 1
				time.sleep(1)
		if timer == 5:
			self.order_failed = True
			self.app.disconnect()
			return


	def execute_order_to_TWS(self, options_contract: Options_Contract):
		self.init_for_next_trade()
		self._options_contract = options_contract
		self.app.nextorderId += 1
		#Create contract
		contract = self._create_contract()
		#Create order object
		order = self._create_order()

		if order.action == "SELL":
			# Check if contracts exist to be sold. 
			self.app.reqPositions()
			while self.app.positionEnd_callback_finished is False:
				time.sleep(0.25)
			# Only execute sell order if an existing position exists. Prevents from short selling non-existant positions. 
			for position in self.app.positions:
				if isinstance(position, PositionInfo) and isinstance(position.contract, Contract):
					if (contract.symbol == position.contract.symbol and
						contract.lastTradeDateOrContractMonth == position.contract.lastTradeDateOrContractMonth and
						contract.strike == position.contract.strike and
						contract.right == position.contract.right and
						position.qty > 0):
						self.placeOrder(contract, order)

		elif order.action == "BUY":
			self.placeOrder(contract, order)


	def placeOrder(self, contract: Contract, order: Order):
		# In here, append new object into self.app.trade_logs. New object contains:
			# orderID
			# execID
			# Price
			# Commission
			# Analyst name. 
		# Start by assigning orderID. 
		trade_log = TradeLogInfo()
		trade_log.orderId = self.app.nextorderId
		trade_log.options_contract = self._options_contract
		self.app.trade_logs.append(trade_log)
		place_order_thread = threading.Thread(target=self.app.placeOrder, args=(self.app.nextorderId, contract, order), daemon=True)
		place_order_thread.start()


	def _create_contract(self):
		contract = Contract()
		contract.symbol = self._options_contract.symbol
		contract.secType = "OPT"
		contract.lastTradeDateOrContractMonth = self._options_contract.expiry_date
		contract.strike = self._options_contract.strike
		contract.right = self._options_contract.right
		contract.exchange = "SMART"
		contract.currency = "USD"
		return contract
	
	
	def _create_order(self):
		order = Order()
		order.action = self._options_contract.action
		order.totalQuantity = 1
		order.orderType = 'MKT'
		order.eTradeOnly = ""
		order.firmQuoteOnly = ""
		order.orderRef = self._options_contract.analyst_name
		return order



