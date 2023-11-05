from ibapi.client import EClient
from ibapi.order import Order
from ibapi.order_state import OrderState
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import *
from ibapi.commission_report import *




import threading
from threading import Timer
import time


class IBapi(EWrapper, EClient):
	def __init__(self):
		EClient.__init__(self, self)
		self.portfolio = []
		self.has_position_ended = False
	
	def nextValidId(self, orderId: int):
		super().nextValidId(orderId)
		self.nextorderId = orderId
		print('The next valid order id is: ', self.nextorderId)

	def orderStatus(self, orderId, status, filled, remaining, avgFullPrice, permId, parentId, lastFillPrice, clientId, whyHeld, mktCapPrice):
		print('orderStatus - orderid:', orderId, 'status:', status, 'filled', filled, 'remaining', remaining, 'lastFillPrice', lastFillPrice)
	
	def openOrder(self, orderId, contract, order, orderState):
		print('openOrder id:', orderId, contract.symbol, contract.secType, '@', contract.exchange, ':', order.action, order.orderType, order.totalQuantity, orderState.status)

	def execDetails(self, reqId, contract, execution):
		print('Order Executed: ', reqId, contract.symbol, contract.secType, contract.currency, execution.execId, execution.orderId, execution.shares, execution.lastLiquidity)

	def position(self, account, contract: Contract, pos, avgCost):
		position_info = PositionInfo(contract, pos)
		self.portfolio.append(position_info)
	
	def positionEnd(self):
		self.has_position_ended = True
		print("positionEnd")

	def commissionReport(self, commissionReport: CommissionReport):
		print('Commission Report:', commissionReport.execId, commissionReport.commission)

class PositionInfo:
	def __init__(self, contract, pos):
		self.contract = contract
		self.pos = pos

		
		


def execute_order_to_TWS():
	def run_loop():
		app.run()

	app = IBapi()
	app.connect('127.0.0.1', 7497, 123)

	app.nextorderId = None

	#Start the socket in a thread
	api_thread = threading.Thread(target=run_loop, daemon=True)
	api_thread.start()

	#Check if the API is connected via orderid
	while True:
		if isinstance(app.nextorderId, int):
			print('connected')
			print()
			break
		else:
			print('waiting for connection')
			time.sleep(1)

	#Create contract
	contract = Contract()
	contract.symbol = "COIN"
	contract.secType = "OPT"
	contract.lastTradeDateOrContractMonth = "20230728" # Make sure date is not in the past. 
	contract.strike = 81
	contract.right = "C"
	contract.exchange = "SMART"
	contract.currency = "USD"

	#Create order object
	order = Order()
	order.action = "BUY"
	order.totalQuantity = 1
	order.orderType = 'MKT'
	order.eTradeOnly = ""
	order.firmQuoteOnly = ""


	if order.action == "BUY":
		# Check if contracts exist to be sold. 
		app.reqPositions()
		while app.has_position_ended is False:
			time.sleep(0.25)
			print("Waiting")
		if app.has_position_ended is True:
			for position in app.portfolio:
				if isinstance(position, PositionInfo) and isinstance(position.contract, Contract):
					if position.pos > 0:
						print(position.contract)
					if position.contract.symbol == "AMD":
						app.disconnect()
	
	#Place order
	app.placeOrder(app.nextorderId, contract, order)

	app.reqCompletedOrders(True)



	time.sleep(3)
	app.disconnect()

execute_order_to_TWS()


