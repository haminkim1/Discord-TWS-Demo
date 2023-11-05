from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract, ContractDetails
from ibapi.order import *
from ibapi.commission_report import *
from ibapi.execution import ExecutionFilter

from classes.ibkr.PositionInfo import PositionInfo
from classes.ibkr.TradeLogInfo import TradeLogInfo

from utils.csv_utils import post_data_as_CSV, update_positions

class IBapi(EWrapper, EClient):
	def __init__(self):
		EClient.__init__(self, self)
		self.positions = []
		self.positionEnd_callback_finished = False
		self.latest_order_commission = 0.0
		self.latest_price = 0.0
		self.trade_logs = []
	

	def nextValidId(self, orderId: int):
		super().nextValidId(orderId)
		self.nextorderId = orderId
		print('The next valid order id is: ', self.nextorderId)


	def openOrder(self, orderId, contract, order, orderState):
		print('openOrder id:', orderId, contract.symbol, contract.secType, '@', contract.exchange, ':', order.action, order.orderType, order.totalQuantity, orderState.status)
		self.latest_order_commission = orderState.commission


	def orderStatus(self, orderId, status, filled, remaining, avgFullPrice, permId, parentId, lastFillPrice, clientId, whyHeld, mktCapPrice):
		print('orderStatus - orderid:', orderId, 'status:', status, 'filled', filled, 'remaining', remaining, 'lastFillPrice', lastFillPrice)
		self.latest_price = avgFullPrice # More calculation may be required if number of contract > 1
		# Find and match orderID from self.contracts_opened_from_analyst. If match, assign price under that object. 
		for log in self.trade_logs:
			if isinstance(log, TradeLogInfo) and orderId == log.orderId:
				log.price = lastFillPrice


	# When market opens, see if this executes if an order is successfully placed. 
	# I can get any of the ID to link between contract, order and log it in Google Sheets
	def execDetails(self, reqId, contract, execution):
		print('Order Executed: ', reqId, contract.symbol, contract.secType, contract.currency, execution.execId, execution.orderId, execution.shares, execution.lastLiquidity)
		print('Contract ID:', contract.conId)
		# Find and match orderID from self.contracts_opened_from_analyst. If match, assign execID under that object. 
		for log in self.trade_logs:
			if isinstance(log, TradeLogInfo) and execution.orderId == log.orderId:
				log.execId = execution.execId
	

	# When market opens, check if commissionReport.execId and execution.execId are the same
	def commissionReport(self, commissionReport: CommissionReport):
		print('Commission Report:', commissionReport)
		# Find and match orderID from self.contracts_opened_from_analyst. If match, assign commission under that object. 
		# Update CSVs here (both positions and trade log).
		for log in self.trade_logs:
			if isinstance(log, TradeLogInfo) and commissionReport.execId == log.execId:
				log.commission = commissionReport.commission
				post_data_as_CSV(log.options_contract, log.price, log.commission)
				update_positions(log.options_contract)


	def position(self, account, contract: Contract, pos, avgCost):
		position_info = PositionInfo(contract, pos)
		self.positions.append(position_info)


	def positionEnd(self):
		self.positionEnd_callback_finished = True
