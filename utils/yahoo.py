import yfinance as yf
import pandas as pd
from datetime import datetime
import numpy as np


def calculate_volatility(ticker, period='1y'):
    """
    Calculate the annualized volatility of a stock.

    Parameters:
    - ticker: Stock ticker symbol (e.g., 'AAPL')
    - period: Time period to fetch data (e.g., '1y', '6mo', '1mo')

    Returns:
    - annualized_volatility: The annualized volatility of the stock
    """
    # Fetch historical data
    data = yf.download(ticker, period=period)

    # Calculate daily returns
    data['Daily Return'] = data['Adj Close'].pct_change()

    # Calculate the standard deviation of daily returns
    daily_volatility = data['Daily Return'].std()

    # Annualize the volatility (assuming 252 trading days in a year)
    annualized_volatility = daily_volatility * np.sqrt(252)

    return annualized_volatility


def get_options_expirations_dates(ticker="AAPL"):
    # Fetch the stock data
    stock = yf.Ticker(ticker)
    
    # Get available options expiration dates
    options_dates = stock.options
    
    # Create a DataFrame from the options dates
    options_df = pd.DataFrame(options_dates, columns=['Expiration Dates'])
    
    try:
        # Convert to datetime
        options_df['Expiration Dates'] = pd.to_datetime(options_df['Expiration Dates'])
        options_df['Month'] = options_df['Expiration Dates'].dt.month_name()

        # Calculate the number of months remaining
        today = datetime.now()
        options_df['Months Remaining'] = (
            (options_df['Expiration Dates'] - today) / pd.Timedelta(days=30)
        ).astype(int)  # Convert to integer

        # Filter out past expiration dates
        options_df = options_df[options_df['Expiration Dates'] > today]

    except Exception as e:
        print(f"Error converting dates: {e}")
        return None

    return options_df
    

def _get_options_info(ticker, expiration_date, ls, cp):
    # Fetch the stock data
    stock = yf.Ticker(ticker)
    
    # Get available options expiration dates
    options_dates = stock.options
    
    # Check if the expiration_date is in the options_dates
    if expiration_date not in options_dates:
        raise ValueError(f"{expiration_date} is not a valid expiration date for {ticker}.")
    
    # Fetch options data for the chosen expiration date
    options_data = stock.option_chain(expiration_date)
    
    # Access Call or Put Options
    if cp.lower() == "call":
        options_df = options_data.calls
    elif cp.lower() == "put":
        options_df = options_data.puts
    else:
        raise ValueError("cp should be either 'call' or 'put'.")

    options_df["ticker"] = ticker

    # Rotate columns by one position
    options_df = options_df[[options_df.columns[-1]] + options_df.columns[:-1].tolist()]
    options_df = options_df[[options_df.columns[-1]] + options_df.columns[:-1].tolist()]

    # Add expiration date
    options_df["expirationDate"] = expiration_date

    # add ticker price
    ticker_price = get_price(ticker, '1d')
    options_df["tickerPrice"] = round(ticker_price["Close"].iloc[-1], 3)
    # options_df["tickerPrice"] = round(ticker_price["Close"][-1],3)

    # update contractSymbol with cp and ls info 
    options_df["contractSymbol"] = options_df["contractSymbol"] + f"_{cp}_{ls}"

    # update ls and cp
    options_df["ls"] = ls
    options_df["cp"] = cp

    options_df["type"] = "option"

    return options_df


def get_options_list(ticker, expiration_dates, ls, cp):
    # Create an empty DataFrame to store the options data
    options_list = pd.DataFrame()

    # Loop through the expiration dates
    for date in expiration_dates:
        try:
            # Fetch options data for the chosen expiration date
            options_df = _get_options_info(ticker, date, ls, cp)
            options_list = pd.concat([options_list, options_df], ignore_index=True)
        except Exception as e:
            print(f"Error fetching options data for {date}: {e}")

    return options_list


def get_price(ticker, period='5d'):
    # ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']
    # Fetch the stock data
    stock = yf.Ticker(ticker)
    return stock.history(period=period)


def get_stock_list(ticker, ls):
    df = pd.DataFrame()
    infos = yf.Ticker(ticker).info
    df["type"] = ["stock"]
    df["currency"] = [infos["currency"]]
    df["ticker"] = [infos["symbol"]]
    df["contractSymbol"] = [infos["symbol"] + "_" + ls]
    df["ls"] = [ls]
    df["cp"] = None
    df["strike"] = None
    df["lastPrice"] = None
    df["volume"] = None
    df["inTheMoney"] = None
    df["contractSize"] = None
    df["expirationDate"] = None
    df["tickerPrice"] = [infos["currentPrice"]]
    df["lastTradeDate"] = None
    df["bid"] = [infos["bid"]]
    df["ask"] = [infos["ask"]]
    df["openInterest"] = None
    df["impliedVolatility"] = None

    return df


def get_risk_free_rate(period="1y"):
    # Fetch the 10-year U.S. Treasury bond yield
    treasury_data = yf.Ticker("^TNX")  # ^TNX is the ticker for the 10-year Treasury yield
    treasury_info = treasury_data.history(period=period)

    # Get the most recent yield (in percentage)
    risk_free_rate = treasury_info['Close'].iloc[-1] / 100  # Convert to decimal
    return risk_free_rate


def get_stock_min_max(ticker, period='1y'):
    # Fetch the stock data
    stock = yf.Ticker(ticker)
    
    # Get historical stock data
    stock_data = stock.history(period=period)
    
    # Calculate the minimum and maximum stock prices
    min_stock_price = stock_data['Low'].min()
    max_stock_price = stock_data['High'].max()
    
    return min_stock_price, max_stock_price

if __name__ == "__main__":
    risk_free_rate = get_risk_free_rate()
    print(f"Annualized Risk-Free Rate: {risk_free_rate:.2%}")