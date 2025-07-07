from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import Order
import threading
import time


# ------------ Net Liquidation ------------

class AccountApp(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.net_liquidation = None
        self.connected_event = threading.Event()
        self.done_event = threading.Event()

    def nextValidId(self, orderId: int):
        print("[DEBUG] Connected. Next valid order ID:", orderId)
        self.connected_event.set()

    def accountSummary(self, reqId, account, tag, value, currency):
        if tag == "NetLiquidation":
            try:
                self.net_liquidation = float(value)
                print(f"[ACCOUNT SUMMARY] NetLiquidation = {value} {currency}")
            except ValueError:
                print(f"[ERROR] Couldn't parse NetLiquidation value: {value}")
            self.done_event.set()

    def accountSummaryEnd(self, reqId):
        self.done_event.set()


def get_account_value():
    app = AccountApp()
    app.connect("127.0.0.1", 7497, clientId=1001)

    thread = threading.Thread(target=app.run, daemon=True)
    thread.start()

    app.connected_event.wait(timeout=5)
    print("[DEBUG] Requesting account summary...")
    app.reqAccountSummary(9001, "All", "NetLiquidation")
    app.done_event.wait(timeout=5)

    app.disconnect()
    thread.join(timeout=2)

    return app.net_liquidation or 0.0


# ------------ Get Positions ------------

class PositionsApp(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.connected_event = threading.Event()
        self.done_event = threading.Event()
        self.positions = []

    def nextValidId(self, orderId: int):
        print("[DEBUG] Connected. Next valid order ID:", orderId)
        self.connected_event.set()

    def position(self, account, contract, position, avgCost):
        if position != 0 and contract.secType == "STK":
            print(f"[POSITION] {contract.symbol} — {position} shares @ avg cost ${avgCost:.2f}")
            self.positions.append((contract.symbol, position, avgCost))

    def positionEnd(self):
        self.done_event.set()


def get_positions():
    app = PositionsApp()
    app.connect("127.0.0.1", 7497, clientId=998)

    thread = threading.Thread(target=app.run, daemon=True)
    thread.start()

    app.connected_event.wait(timeout=5)
    print("[DEBUG] Requesting positions...")
    app.reqPositions()
    app.done_event.wait(timeout=5)

    app.disconnect()
    thread.join(timeout=2)

    return app.positions


# ------------ Rebalancing Logic ------------

class TraderApp(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.nextOrderId = None
        self.connected_event = threading.Event()

    def nextValidId(self, orderId: int):
        self.nextOrderId = orderId
        print(f"[DEBUG] Next valid order ID: {orderId}")
        self.connected_event.set()


def create_contract(symbol):
    contract = Contract()
    contract.symbol = symbol
    contract.secType = "STK"
    contract.exchange = "SMART"
    contract.currency = "USD"
    return contract


def create_order(action, quantity):
    order = Order()
    order.action = action
    order.orderType = "MKT"
    order.totalQuantity = quantity
    order.eTradeOnly = False  # These two lines enable paper trading to occur
    order.firmQuoteOnly = False  # This too!
    return order



def rebalance_portfolio(target_allocations, current_prices):
    capital = get_account_value()
    positions = dict((symbol, qty) for symbol, qty, _ in get_positions())
    print(f"\n[INFO] Current capital: ${capital:.2f}")
    print(f"[INFO] Current positions: {positions}")

    target_shares = {}
    for symbol, weight in target_allocations.items():
        price = current_prices.get(symbol, 0)
        if price > 0:
            target_qty = int((capital * weight) / price)
            target_shares[symbol] = target_qty

    app = TraderApp()
    app.connect("127.0.0.1", 7497, clientId=999)

    thread = threading.Thread(target=app.run, daemon=True)
    thread.start()

    app.connected_event.wait(timeout=5)
    order_id = app.nextOrderId or 1

    for symbol, target_qty in target_shares.items():
        current_qty = positions.get(symbol, 0)
        delta = target_qty - current_qty

        if delta == 0:
            print(f"[INFO] No change needed for {symbol}")
            continue

        action = "BUY" if delta > 0 else "SELL"
        quantity = abs(delta)
        print(f"[TRADE] {action} {quantity} shares of {symbol}")

        contract = create_contract(symbol)
        order = create_order(action, quantity)
        app.placeOrder(order_id, contract, order)
        order_id += 1
        time.sleep(1)

    time.sleep(2)
    app.disconnect()
    thread.join(timeout=2)
