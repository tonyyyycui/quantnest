import pandas as pd
import shinybroker as sb
import time
from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt import risk_models
from pypfopt import expected_returns


list_of_tickers = ["AAPL", "TSLA", "MSTR", "GME", "AMZN", "USO", "SHY", "IVV"]

def fetch_close_for_a_ticker(ticker):
    df = sb.fetch_historical_data(          #this is the part that is connecting to the IB API
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

historical_data = fetch_close_for_a_ticker(list_of_tickers[0])

for tk in list_of_tickers[1:]:
    historical_data = pd.merge(
        historical_data,
        fetch_close_for_a_ticker(tk),
        on='timestamp'
    )
    time.sleep(0.1)

historical_data['timestamp'] = pd.to_datetime(historical_data['timestamp'])
historical_data = historical_data.set_index('timestamp')

# Calculate expected returns and sample covariance
mu = expected_returns.mean_historical_return(historical_data)
S = risk_models.sample_cov(historical_data)

# Optimize for maximal Sharpe ratio
ef = EfficientFrontier(mu, S)
weights = ef.max_sharpe()

ef.portfolio_performance(verbose=True)
print(weights)