from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import Order
from threading import Thread
import time

class IBApi(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.next_order_id = None
        self.positions = {}
        self.fills = []

    def nextValidId(self, orderId: int):
        self.next_order_id = orderId
        print(f"Next valid order ID: {orderId}")

    def position(self, account, contract, position, avgCost):
        if contract.exchange == "SMART" and contract.secType == "STK":
            self.positions[contract.symbol] = position

    def positionEnd(self):
        print("Finished receiving positions.")

    def execDetails(self, reqId, contract, execution):
        self.fills.append({
            'symbol': contract.symbol,
            'exec_id': execution.execId,
            'shares': execution.shares,
            'price': execution.price,
            'time': execution.time
        })

def run_loop(app):
    app.run()

def start_ib_client():
    app = IBApi()
    app.connect("127.0.0.1", 7497, clientId=1)
    api_thread = Thread(target=run_loop, args=(app,), daemon=True)
    api_thread.start()
    while app.next_order_id is None:
        time.sleep(0.1)
    return app

def stock_contract(symbol):
    contract = Contract()
    contract.symbol = symbol
    contract.secType = "STK"
    contract.exchange = "SMART"
    contract.currency = "USD"
    return contract

def market_order(action, quantity):
    order = Order()
    order.action = action
    order.orderType = "MKT"
    order.totalQuantity = quantity
    return order
