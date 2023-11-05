# Imports
# https://www.youtube.com/watch?v=XKbk8SY9LD0&ab_channel=JacobAmaral
import ibapi
from ibapi.client import EClient
from ibapi.wrapper import EWrapper

#
from ibapi.contract import Contract # contract means symbols
from ibapi.order import *
import threading
import time

# Variable

# Class for IB Connection
class IBApi(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
    # Listen for realtime bars 
    def realtimeBar(self, reqId, time, open_, high, low, close, volume, wap, count):
        super().realtimeBar(reqId, time, open_, high, low, close, volume, wap, count)
        try:
            bot.on_bar_update(reqId, time, open_, high, low, close, volume, wap, count)
        except Exception as e:
            print(e)
    def error(self, id, errorCode, errorMsg):
        print(errorCode)
        print(errorMsg)


# Bot Logic
class Bot():
    ib = None
    def __init__(self):
        # Connect to IB on init
        self.ib = IBApi()
        # 7496: Socket port number for live account, 7497 for paper trading. 
        # The number beside the socket port is a client id used to identify our script to 
        # the API. It can be any unique positive integer. 
        self.ib.connect("127.0.0.1", 7497,1)
        ib_thread = threading.Thread(target=self.run_loop, daemon=True)
        ib_thread.start()
        time.sleep(1)
        # Get symbol info
        symbol = input("Enter the symbol you want to trade : ")
        # Create our IB Contract Object
        contract = Contract()
        contract.symbol = symbol.upper()
        contract.secType = "STK" # OPT for options
        contract.exchange = "SMART"
        contract.currency = "USD"
        # Request Market Data
        self.ib.reqRealTimeBars(0, contract, 5, "TRADES", 1, [])
        
        

    # Listens to socket in separate thread. 
    # separate thread needed because once run is called, the program is listening
    # for a socket and it cannot continue. So all code under ib.run() will not run
    # but we want the code to continue because we want to perform logic on when
    # to buy and sell. So we're going to have to put it into a separate thread. 
    def run_loop(self):
        self.ib.run()
    
    # Pass realtime bar data back to our bot object
    def on_bar_update(self, reqId, time, open_, high, low, close, volume, wap, count):
        print(reqId)

# Start Bot
bot = Bot()
