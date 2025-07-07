from pypfopt import expected_returns, risk_models
from pypfopt.efficient_frontier import EfficientFrontier
from data_fetcher import fetch_historical_data, fetch_latest_prices

TICKERS = ["AAPL", "TSLA", "MSTR", "GME", "AMZN", "USO", "SHY", "IVV"]

def optimize_portfolio(historical_data):
    mu = expected_returns.mean_historical_return(historical_data)
    S = risk_models.sample_cov(historical_data)
    ef = EfficientFrontier(mu, S)
    weights = ef.max_sharpe()
    ef.portfolio_performance(verbose=True)
    return weights

def get_target_allocations():
    hist_data = fetch_historical_data(TICKERS)
    weights = optimize_portfolio(hist_data)
    print('these are the weights: ', weights)
    return weights  # Returns dict like {"AAPL": 0.18, "TSLA": 0.12, ...}

def get_latest_prices(tickers=None):
    if tickers is None:
        tickers = TICKERS
    return fetch_latest_prices(tickers)  # Returns dict like {"AAPL": 170.2, ...}
