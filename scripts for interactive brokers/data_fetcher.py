import pandas as pd
import time
import shinybroker as sb
import yfinance as yf
from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt import EfficientFrontier, risk_models, expected_returns, objective_functions


# Function to fetch close price for a given ticker using shinybroker
def fetch_close_for_a_ticker(ticker):
    df = sb.fetch_historical_data(
        contract=sb.Contract({
            'symbol': ticker,
            'secType': "STK",
            'exchange': "SMART",
            'currency': "USD"
        }),
        barSizeSetting='1 day',
        durationStr='1 Y',
        whatToShow='ADJUSTED_LAST'
    )['hst_dta'][['timestamp', 'close']]
    df = df.rename(columns={'close': ticker})
    return df


# Function to fetch historical data for multiple tickers
def fetch_historical_data(tickers):
    df = fetch_close_for_a_ticker(tickers[0])
    for tk in tickers[1:]:
        df = pd.merge(df, fetch_close_for_a_ticker(tk), on='timestamp')
        time.sleep(0.1)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df.set_index('timestamp')


# Function to fetch the latest prices for multiple tickers
def fetch_latest_prices(tickers):
    prices = {}
    for tk in tickers:
        df = fetch_close_for_a_ticker(tk)
        prices[tk] = df[tk].iloc[-1]
    return prices


# Function to fetch fundamental data like PE ratio and market cap using yfinance
def fetch_fundamentals_yf(ticker):
    """Fetch fundamental data for a given ticker using yfinance."""
    stock = yf.Ticker(ticker)
    info = stock.info
    market_cap = info.get('marketCap', None)
    pe_ratio = info.get('trailingPE', None)

    if market_cap is None:
        print(f"⚠️ Market Cap missing for {ticker}, skipping this stock.")
        return None
    
    fundamentals = {
        'pe_ratio': info.get('trailingPE', None),
        'market_cap': info.get('marketCap', None),  # Market Cap as Size factor
    }

    print('check for stock ', ticker, ' fundamentals: ', fundamentals)
    
    return fundamentals

def categorize_stocks(fundamentals):
    small_caps = []
    large_caps = []
    etfs = []

    for ticker, data in fundamentals.items():
        market_cap = data.get('market_cap', 0)
        
        # Classify ETFs based on tickers or sector
        if ticker in ["SPY", "QQQ", "IVV", "VOO", "VTI", "IWM", "DIA", "XLF", "XLK", "XLY", "XLC", "XLE", "XLV", "XLI", "XLB", "XLRE", "XLU"]:
            etfs.append(ticker)
        # Classify by market cap
        elif market_cap < 2e9:  # Small Cap
            small_caps.append(ticker)
            print('small_cap detected: ', ticker)
        elif market_cap > 10e9:  # Large Cap
            large_caps.append(ticker)
            print('large_cap detected: ', ticker)

    
    return small_caps, large_caps, etfs

# Function to optimize the portfolio using momentum, size (market cap), and value (PE ratio)
def optimize_portfolio(historical_data, fundamentals):
    # 1. Momentum Factor: 6-month price change
    momentum = historical_data.pct_change(126).iloc[-1].dropna()

    # Scale momentum scores between 0 and 1
    min_mom = momentum.min()
    max_mom = momentum.max()
    scaled_momentum = (momentum - min_mom) / (max_mom - min_mom)


    # # 2. Size Factor: Market Cap (larger market cap = higher score)
    market_caps = {ticker: fundamentals[ticker].get('market_cap', None) for ticker in fundamentals}
    
    # # Remove tickers with None as market cap
    market_caps = {ticker: cap for ticker, cap in market_caps.items() if cap is not None}
    # valid_tickers = [ticker for ticker in tickers if fundamentals.get(ticker)]

    small_caps, large_caps, etfs = categorize_stocks(fundamentals)

    # Check if there are any valid market cap values to compute scaling
    if len(market_caps) > 0:
        min_size = min(market_caps.values())
        max_size = max(market_caps.values())
        scaled_size = {ticker: (market_caps[ticker] - min_size) / (max_size - min_size) for ticker in market_caps}
    else:
        scaled_size = {}

    # 3. Value Factor: PE ratio (lower PE = better value)
    pe_ratios = {ticker: fundamentals[ticker].get('pe_ratio', None) for ticker in fundamentals}
    
    # Remove tickers with None as PE ratio
    pe_ratios = {ticker: pe for ticker, pe in pe_ratios.items() if pe is not None}

    # Check if there are any valid PE ratios to compute scaling
    if len(pe_ratios) > 0:
        min_pe = min(pe_ratios.values())
        max_pe = max(pe_ratios.values())
        scaled_pe = {ticker: (min_pe - pe_ratios[ticker]) / (min_pe - max_pe) for ticker in pe_ratios}
    else:
        scaled_pe = {}

    # Combine all factors into a combined expected return score
    combined_returns = {}
    for ticker in momentum.index:
        combined_returns[ticker] = (
            0.8 * scaled_momentum.get(ticker, 0) +  # 40% momentum
            # 0.3 * scaled_size.get(ticker, 0) +      # 30% size (market cap)
             0.2 * scaled_pe.get(ticker, 0.5)         # 30% value (PE ratio) NOTE: IF THERE IS NO PE SCORE, DONT PENALIZE, JUST ENSUREITS NEUTRAL
        )
        print('expected returns stock score for ', ticker, ' ', combined_returns[ticker])

        mu = pd.Series(combined_returns)

    # build covariance on *all* columns, then align it to mu
    S = risk_models.sample_cov(historical_data)
    S = S.reindex(index=mu.index, columns=mu.index)

    print("mu shape:", mu.shape)
    print("S shape:", S.shape)

    ef = EfficientFrontier(mu, S)

    # ➔ No individual asset should have more than 20%
    ef.add_constraint(lambda w: w <= 0.20)

    # ➔ Small caps should be at least 10% of total weight
    if small_caps:
        ef.add_constraint(lambda w: sum(w[i] for i, ticker in enumerate(ef.tickers) if ticker in small_caps) >= 0.10)

    # ➔ Large caps should be at least 10% of total weight
    if large_caps:
        ef.add_constraint(lambda w: sum(w[i] for i, ticker in enumerate(ef.tickers) if ticker in large_caps) >= 0.10)

    # ➔ ETFs should be at least 10% of total weight
    if etfs:
        ef.add_constraint(lambda w: sum(w[i] for i, ticker in enumerate(ef.tickers) if ticker in etfs) >= 0.10)

    # ➔ Now optimize
    weights = ef.max_sharpe()
    return ef.clean_weights()



# Function to compute target allocations based on portfolio weights and prices
def compute_target_allocations(weights, capital, prices):
    allocations = {}
    for ticker, weight in weights.items():
        if weight > 0:
            dollar_amount = capital * weight
            allocations[ticker] = int(dollar_amount / prices[ticker])
    return allocations
