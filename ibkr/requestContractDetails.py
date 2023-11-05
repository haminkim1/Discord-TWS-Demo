# from ibapi.client import *
# from ibapi.wrapper import *
# import time
# class TestApp(EClient, EWrapper):
#     def __init__(self):
#         EClient.__init__(self, self)
#     def contractDetails(self, reqId, contractDetails):
#         print(f"contract details: {contractDetails}")
#     def contractDetailsEnd(self, reqId):
#         print("End of contractDetails")
#         self.disconnect()
# def main():
#     app = TestApp()
#     app.connect("127.0.0.1", 7497, 1000)
#     mycontract = Contract()
#     mycontract.symbol = "AAPL"
#     mycontract.secType = "OPT"
#     mycontract.exchange = "SMART"
#     mycontract.currency = "USD"
#     mycontract.right = "C"
#     mycontract.lastTradeDateOrContractMonth = "202211"
#     mycontract.strike = 125
#     time.sleep(3)
#     app.reqContractDetails(1, mycontract)
#     app.run()
# if __name__ == "__main__":
#     main()


from ibapi.client import *
from ibapi.wrapper import *
import time
class TestApp(EClient, EWrapper):
    def __init__(self):
        EClient.__init__(self, self)
    def contractDetails(self, reqId, contractDetails):
        contractDetails.notes = "This is the way to write notes on contracts"
        print(f"contract details: {contractDetails.contract.conId}")
    def contractDetailsEnd(self, reqId):
        print("End of contractDetails")
        self.disconnect()
def main():
    app = TestApp()
    app.connect("127.0.0.1", 7496, 1000)
    mycontract = Contract()
    mycontract.symbol = "AAPL"
    mycontract.secType = "STK"
    mycontract.exchange = "SMART"
    mycontract.currency = "USD"
    mycontract.primaryExchange = "ISLAND"
    # mycontract.notes = "Analyst3"
    time.sleep(3)
    app.reqContractDetails(265598, mycontract)
    print(f"Contract details: {mycontract.conId}")
    app.run()
if __name__ == "__main__":
    main()