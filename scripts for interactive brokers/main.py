from data_fetcher import fetch_historical_data, optimize_portfolio, fetch_latest_prices, fetch_fundamentals_yf
from trader import rebalance_portfolio, get_account_value

# Individual US Stocks
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


def main():
    print("🔍 Fetching historical data...")
    historical_data = fetch_historical_data(TICKERS)

    print("🧠 Fetching fundamental data (PE ratio, market cap)...")
    fundamentals = {ticker: fetch_fundamentals_yf(ticker) for ticker in TICKERS}

    print("🧠 Optimizing portfolio...")
    weights = optimize_portfolio(historical_data, fundamentals)  # Pass fundamentals here

    print("💰 Fetching account value...")
    capital = get_account_value()
    if capital == 0.0:
        print("⚠️ Could not fetch NetLiquidation. Using fallback capital of $10,000.")
        capital = 10000.0
    print(f"✅ Capital available for allocation: ${capital:.2f}")

    print("💹 Fetching latest prices...")
    latest_prices = fetch_latest_prices(TICKERS)

    print("📊 Calculating target allocations...")
    allocations = {
        symbol: weights.get(symbol, 0.0)
        for symbol in TICKERS
        if symbol in latest_prices and latest_prices[symbol] > 0
    }

    estimated_cost = sum((capital * weight) for symbol, weight in allocations.items())
    cash_remaining = capital - estimated_cost
    print(f"💸 Estimated cash remaining after allocation: ${cash_remaining:.2f}")

    print("🔁 Rebalancing portfolio...")
    rebalance_portfolio(allocations, latest_prices)


if __name__ == "__main__":
    main()
