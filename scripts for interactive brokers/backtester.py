import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from data_fetcher import fetch_fundamentals_yf, categorize_stocks, optimize_portfolio

STOCK_TICKERS = [
    "AAPL",  # Apple
    "TSLA",  # Tesla
    "MSTR",  # MicroStrategy
    "GME",   # GameStop
    "AMZN",  # Amazon
    "MSFT",  # Microsoft
    "NVDA",  # NVIDIA
    "META",  # Meta (Facebook)
    "UNH",   # UnitedHealth
    "V",     # Visa
    "JPM",   # JPMorgan Chase
    "IBKR",  # Interactive Brokers
    "RBLX",  # Roblox
    "DKNG",  # DraftKings
    "CELH",  # Celsius Holdings
    "SOFI",  # SoFi Technologies
    "HOOD",  # Robinhood
    "ABNB",  # Airbnb
    "PEP",   # PepsiCo
    "COST",  # Costco
    "AMD",   # Advanced Micro Devices
    "GOOG",  # Alphabet (Google Class C)
    "MRK",   # Merck & Co.
    "CSCO",  # Cisco Systems
    "WMT",   # Walmart
    "BA",    # Boeing
    "C",     # Citigroup
    "DIS",   # Disney
    "CRM",   # Salesforce
    "AMGN",  # Amgen
    "LOW",   # Lowe’s
    "GS",    # Goldman Sachs
    "WBA",   # Walgreens Boots Alliance
    "PYPL",  # PayPal Holdings
    "ADBE",  # Adobe Systems
    "NKE",   # Nike
    "ORCL",  # Oracle
    "TXN",   # Texas Instruments
    "PFE",   # Pfizer
    "INTC",  # Intel Corporation
    "BKNG",  # Booking Holdings
    "GE",    # General Electric
    "UPS",   # United Parcel Service
    "T",     # AT&T
    "VRTX",  # Vertex Pharmaceuticals
    "MDT",   # Medtronic
    "CVX",   # Chevron
    "ABBV",  # AbbVie
    "MCD",   # McDonald's
    "BLK",   # BlackRock
    "FDX",   # FedEx
    "CAT",   # Caterpillar
    "ZM",    # Zoom Video Communications
    "TEAM",  # Atlassian
    "DDOG",  # Datadog
    "SHOP",  # Shopify
    "LYFT",  # Lyft
    "UBER",  # Uber Technologies
    "TWLO",  # Twilio
    "DOCU",  # DocuSign
    "RIVN",  # Rivian
    "F",     # Ford Motor Company
    "GM",    # General Motors
    "XOM",   # ExxonMobil
    "OXY",   # Occidental Petroleum
    "PSX",   # Phillips 66
    "APA",   # Apache Corp
    "WBD",   # Warner Bros Discovery
    "SBUX",  # Starbucks
    "BK",    # Bank of New York Mellon
    "MS",    # Morgan Stanley
    "ETSY",  # Etsy
    "PANW",  # Palo Alto Networks
    "ZS",    # Zscaler
    "ANET",  # Arista Networks
    "LULU",  # Lululemon Athletica
    "DE",    # Deere & Co.
    "SPOT",  # Spotify
    "CHTR",  # Charter Communications
    "MAR",   # Marriott International
    "HON",   # Honeywell
    "NOW",   # ServiceNow
    "ADP",   # Automatic Data Processing
    "TMO",   # Thermo Fisher Scientific
    "AVGO",  # Broadcom
    "KLAC",  # KLA Corporation
    "MPC",   # Marathon Petroleum
    "DFS",   # Discover Financial Services
    "MTCH",  # Match Group
    "EBAY",  # eBay
    "ALGN",  # Align Technology
    "CRWD",  # CrowdStrike Holdings
    "DD",    # DuPont
    "GLW",   # Corning Inc.
    "VRSK",  # Verisk Analytics
    "ILMN",  # Illumina
    "REGN",  # Regeneron Pharmaceuticals
    "SWKS",  # Skyworks Solutions
    "FTNT",  # Fortinet
    "ROST",  # Ross Stores
    "BBY",   # Best Buy
    "AES",   # AES Corporation
    "DRI",   # Darden Restaurants
    "ULTA",  # Ulta Beauty
    "IDXX",  # IDEXX Laboratories
    "APPF",   # AppFolio
    "INSM",   # Insmed
    "FND",    # Floor & Decor Holdings
    "RUN",    # Sunrun
    "BL",     # BlackLine
    "FOUR",   # Shift4 Payments
    "ESTC",   # Elastic N.V.
    "NEOG",   # Neogen Corp
    "RGEN",   # Repligen Corporation
    "VRT",    # Vertiv Holdings
    "MGNI",   # Magnite
    "LMND",   # Lemonade
    "WOLF"    # Wolfspeed
]

# Sector ETFs (SPDR Sector ETFs covering major US equity sectors)
SECTOR_ETFS = [
    "XLF",  # Financials
    "XLK",  # Technology
    "XLY",  # Consumer Discretionary
    "XLE",  # Energy
    "XLV",  # Health Care
    "XLI",  # Industrials
    "XLB",  # Materials
    "XLU",  # Utilities
    "XME",  # Metals and Mining
    "XOP",  # Oil & Gas Exploration
    "XRT"  # Retail
]

# Broad Market Index ETFs (Large-cap, mid-cap, small-cap U.S. markets)
MARKET_ETFS = [
    "SPY",  # S&P 500
    "QQQ",  # NASDAQ 100
    "IVV",  # S&P 500 (alternative)
    "VTI",  # Total U.S. Stock Market
    "IWM",  # Russell 2000 (small caps)
    "DIA"   # Dow Jones Industrial Average
]

# Combined Ticker List
TICKERS = STOCK_TICKERS + SECTOR_ETFS + MARKET_ETFS

# --- Configuration ---
ASSETS = TICKERS
START_DATE = "2019-01-01"
END_DATE = "2025-04-27"
INITIAL_CAPITAL = 1_000_000  # $1M
MOMENTUM_LOOKBACK = 126      # days for momentum

# --- Fetch & prepare price history ---
print("Downloading historical data via yfinance...")
raw = yf.download(ASSETS, start=START_DATE, end=END_DATE, auto_adjust=True)
if isinstance(raw.columns, pd.MultiIndex) and 'Close' in raw.columns.levels[0]:
    historical_data = raw['Close']
else:
    historical_data = raw
historical_data.index = pd.to_datetime(historical_data.index)
historical_data = historical_data.dropna(axis=1, how='all')  # drop tickers with no data
if historical_data.empty:
    raise RuntimeError(f"No price data between {START_DATE} and {END_DATE}")
print(f"Loaded price data: {historical_data.shape[0]} rows, {historical_data.shape[1]} assets.")

# --- Fetch fundamentals ---
print("Fetching fundamental data...")
fundamentals = {t: f for t, f in ((tk, fetch_fundamentals_yf(tk)) for tk in ASSETS) if f is not None}
small_caps, large_caps, _ = categorize_stocks(fundamentals)
ETF_TICKERS = SECTOR_ETFS + MARKET_ETFS

# --- Helper functions ---
def get_current_weights(holdings, prices):
    total_val = sum(holdings.get(t,0) * prices.get(t,0) for t in holdings)
    if total_val <= 0:
        return {}, 0.0
    weights = {t: (holdings[t] * prices[t]) / total_val for t in holdings}
    return weights, total_val


def check_constraints(weights, small_caps, large_caps, etfs):
    if any(w > 0.20 for w in weights.values()):
        return True
    if small_caps and sum(weights.get(t, 0) for t in small_caps) < 0.10:
        return True
    if large_caps and sum(weights.get(t, 0) for t in large_caps) < 0.10:
        return True
    if etfs and sum(weights.get(t, 0) for t in etfs) < 0.10:
        return True
    return False


def rebalance(date, hist, fnds, prices, port_value):
    window_start = date - pd.Timedelta(days=365)
    past = hist.loc[window_start:date]
    if len(past) < MOMENTUM_LOOKBACK + 1:
        print(f"[WARN] Insufficient history ({len(past)}) at {date.date()}")
        return None, None
    valid_cols = past.dropna(axis=1, thresh=int(0.8 * len(past))).columns
    past = past[valid_cols]
    if past.empty:
        print(f"[WARN] No valid price columns at {date.date()}")
        return None, None
    fund_flds = {t: fnds[t] for t in valid_cols if t in fnds}
    if not fund_flds:
        print(f"[WARN] No valid fundamentals at {date.date()}")
        return None, None
    try:
        new_weights = optimize_portfolio(past, fund_flds)
    except Exception as e:
        print(f"[WARN] Optimization failed at {date.date()}: {e}")
        return None, None
    new_holdings = {}
    for t, w in new_weights.items():
        p = prices.get(t, 0)
        if p > 0:
            new_holdings[t] = int((port_value * w) / p)
    return new_weights, new_holdings

# --- Initialize portfolio ---
first_date = historical_data.index[0]
first_prices = historical_data.loc[first_date].to_dict()
init_hist = historical_data.iloc[:252]
init_weights = optimize_portfolio(init_hist, fundamentals)
holdings = {t: int((INITIAL_CAPITAL * w) / first_prices[t]) for t, w in init_weights.items() if first_prices.get(t,0) > 0}
weights, port_value = get_current_weights(holdings, first_prices)

print("Starting backtest...")
records = []
# --- Backtest Loop ---
for date, row in historical_data.iterrows():
    prices = row.to_dict()
    weights, port_value = get_current_weights(holdings, prices)
    if check_constraints(weights, small_caps, large_caps, ETF_TICKERS):
        print(f"[REBALANCE] at {date.date()}")
        w_new, h_new = rebalance(date, historical_data, fundamentals, prices, port_value)
        if h_new:
            weights, holdings = w_new, h_new
    rec = {"Date": date.strftime("%Y-%m-%d"), "PortfolioValue": port_value}
    rec.update({t: f"{weights.get(t,0) * 100:.2f}%" for t in ASSETS})
    records.append(rec)

# --- Output & plot ---
df = pd.DataFrame(records)
df.to_csv("backtest_allocations.csv", index=False)
print("Backtest complete; allocations saved.")
plt.figure(figsize=(10,5))
plt.plot(df["Date"], df["PortfolioValue"], marker='o', markersize=2)
plt.xticks(rotation=45)
plt.title("Portfolio Value Over Time")
plt.tight_layout()
plt.show()
