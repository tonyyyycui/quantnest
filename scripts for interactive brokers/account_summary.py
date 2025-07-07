from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
import threading


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


# Main Logic
if __name__ == "__main__":
    # Fetch Account Value (Net Liquidation)
    net_liquidation = get_account_value()
    print(f"\n[INFO] Net Liquidation Value: ${net_liquidation:.2f}")

    # Fetch Positions
    positions = get_positions()
    print("\n✅ Final Positions:")
    for symbol, qty, cost in positions:
        print(f" - {symbol}: {qty} shares @ avg cost ${cost:.2f}")
