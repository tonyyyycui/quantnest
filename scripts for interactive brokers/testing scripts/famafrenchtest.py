from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
import pandas as pd
import datetime
import numpy as np
from sklearn.linear_model import LinearRegression

import ssl



class IBApp(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.data = []

    def historicalData(self, reqId, bar):
        # This function is called for each bar (historical data point)
        self.data.append([bar.date, bar.close])

    def get_historical_data(self, symbol, end_date, duration, bar_size):
        contract = Contract()
        contract.symbol = symbol
        contract.secType = "STK"
        contract.exchange = "SMART"
        contract.currency = "USD"
        
        # Format end_date as a string
        end_date_str = end_date.strftime("%Y%m%d %H:%M:%S")
        
        # Request historical data
        self.reqHistoricalData(1, contract, end_date_str, duration, bar_size, "TRADES", 1, 1, False, [])
        
        # Wait for the data to be received
        self.run()

    def process_data(self):
        # Convert data to pandas DataFrame
        df = pd.DataFrame(self.data, columns=['Date', 'Close'])
        df['Date'] = pd.to_datetime(df['Date'], format='%Y%m%d  %H:%M:%S')
        df.set_index('Date', inplace=True)
        df['Returns'] = df['Close'].pct_change()
        return df

# Fetch stock returns for a symbol from IB
def get_stock_returns(symbol):
    app = IBApp()
    app.connect("127.0.0.1", 7497, 0)  # Connect to IB Gateway/Trader Workstation

    end_date = datetime.datetime.now()
    duration = "1 M"  # Last 1 month
    bar_size = "1 day"  # 1-day bars

    app.get_historical_data(symbol, end_date, duration, bar_size)
    stock_returns = app.process_data()
    
    app.disconnect()  # Disconnect after getting the data

    return stock_returns

# Fetch Fama-French factors
def get_fama_french_factors():
    # Download the Fama-French factors (already cleaned and available in a CSV file)
    ff_url = "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_Factors.csv"
    ff_factors = pd.read_csv(ff_url, skiprows=3)
    ff_factors['Date'] = pd.to_datetime(ff_factors['Date'], format='%Y%m%d')
    ff_factors.set_index('Date', inplace=True)
    
    return ff_factors[['Mkt-RF', 'SMB', 'HML', 'RF']]

# Estimate Fama-French 3-factor betas for each stock
def estimate_ff3_betas(stock_returns, ff_factors):
    # Merge stock returns with Fama-French factors on 'Date'
    ff_factors = ff_factors.loc[stock_returns.index]
    data = pd.concat([stock_returns['Returns'], ff_factors], axis=1).dropna()
    
    # Fit linear regression model: Stock return = alpha + beta1*Mkt-RF + beta2*SMB + beta3*HML
    X = data[['Mkt-RF', 'SMB', 'HML']]
    y = data['Returns']
    
    model = LinearRegression()
    model.fit(X, y)
    
    betas = model.coef_
    
    return betas

# Calculate expected returns using the Fama-French model
def calculate_expected_returns(betas, factors_mean):
    expected_returns = {}
    
    for ticker, beta in betas.items():
        expected_return = factors_mean['Mkt-RF'] * beta[0] + factors_mean['SMB'] * beta[1] + factors_mean['HML'] * beta[2] + factors_mean['RF']
        expected_returns[ticker] = expected_return
    
    return expected_returns

# Portfolio optimization based on expected returns
def get_target_allocations():
    # Get stock returns for multiple stocks
    tickers = ["AAPL", "GOOGL", "MSFT"]  # Example tickers
    stock_returns = {}
    
    for ticker in tickers:
        stock_returns[ticker] = get_stock_returns(ticker)
    
    # Get Fama-French factors
    ff_factors = get_fama_french_factors()
    
    # Calculate betas for each stock
    betas = {}
    for ticker, returns in stock_returns.items():
        betas[ticker] = estimate_ff3_betas(returns, ff_factors)
    
    # Calculate expected returns for each stock
    factors_mean = ff_factors.mean()
    expected_returns = calculate_expected_returns(betas, factors_mean)
    
    # Optimization (basic equal allocation for demonstration)
    total_weight = sum(expected_returns.values())
    allocations = {ticker: expected_return / total_weight for ticker, expected_return in expected_returns.items()}
    
    return allocations

# Main function
def main():
    ssl._create_default_https_context = ssl._create_unverified_context

    allocations = get_target_allocations()
    print("Optimal Allocations:")
    for ticker, allocation in allocations.items():
        print(f"{ticker}: {allocation:.2f}")

# Run the script
if __name__ == "__main__":
    main()
