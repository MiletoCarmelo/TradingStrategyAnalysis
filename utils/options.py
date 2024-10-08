import numpy as np
import pandas as pd
import utils.yahoo as yf


def get_payoff_options(stock_price, strike_price, option_price, longShort, callPut):
    """
    Calculate the payoff for a given options position, supporting both scalar and array inputs.

    Parameters:
    - stock_price: Current price(s) of the underlying stock (float or array-like)
    - strike_price: Strike price(s) of the option (float or array-like)
    - longShort: 'long' for a long position, 'short' for a short position
    - callPut: 'call' for a call option, 'put' for a put option

    Returns:
    - Payoff: The calculated payoff for the position (array-like)
    """
    
    # Convert inputs to NumPy arrays for element-wise operations
    stock_price = np.asarray(stock_price)
    strike_price = np.asarray(strike_price)
    option_price = np.asarray(option_price)

    if callPut.lower() == 'call':
        if longShort.lower() == 'long':
            payoff = np.maximum(0, stock_price - strike_price) - option_price # Long Call Payoff
        elif longShort.lower() == 'short':
            payoff = -np.maximum(0, stock_price - strike_price) + option_price # Short Call Payoff
        else:
            raise ValueError("longShort must be 'long' or 'short'")
    elif callPut.lower() == 'put':
        if longShort.lower() == 'long':
            payoff = np.maximum(0, strike_price - stock_price) - option_price # Long Put Payoff
        elif longShort.lower() == 'short':
            payoff = - np.maximum(0, strike_price - stock_price) + option_price # Short Put Payoff
        else:
            raise ValueError("longShort must be 'long' or 'short'")
    else:
        raise ValueError("callPut must be 'call' or 'put'")

    return payoff


def get_payoff_stocks(stock_price, strike_price, longShort): 
    # Convert inputs to NumPy arrays for element-wise operations
    stock_price = np.asarray(stock_price)
    strike_price = np.asarray(strike_price)
    if longShort.lower() == 'long':
        payoff = stock_price - strike_price  # Long Call Payoff
    elif longShort.lower() == 'short':
        payoff = - (stock_price - strike_price)  # Short Call Payoff
    else:
        raise ValueError("longShort must be 'long' or 'short'")

    return payoff


def get_payoffs(ticker, strike_prices, option_price, quantity, cp, ls, type, min_s=None, max_s=None, interval=1):

    strike_prices_mean = np.mean(strike_prices)


    # Calculate min and max stock price at expiration date (emulation)
    if min_s is None:
        min_s = int(strike_prices_mean - strike_prices_mean / 2)
    if max_s is None:
        max_s = int(strike_prices_mean + strike_prices_mean / 2)

    # Create an array from min_s to max_s with a step of 1
    price_range = np.arange(min_s, max_s, interval)  # +1 to include max_s in the range
    
    # Create a DataFrame for payoffs
    payoff_df = pd.DataFrame()

    # Add the payoff for each strike price
    for k in strike_prices:
        payoff_df_tmp = pd.DataFrame()
        payoff_df_tmp["s"] = price_range
        payoff_df_tmp["k"] = [k] * len(price_range)  # Set strike prices for all rows
        if type == "option":
            payoff_df_tmp["payoff"] = get_payoff_options(price_range, k, option_price, ls, cp)
        else :
            payoff_df_tmp["payoff"] = get_payoff_stocks(price_range, k, ls)

        # Append temporary DataFrame to the main payoff DataFrame
        payoff_df = pd.concat([payoff_df, payoff_df_tmp], ignore_index=True)

    payoff_df["ticker"] = ticker

    # Rotate columns by one position
    payoff_df = payoff_df[[payoff_df.columns[-1]] + payoff_df.columns[:-1].tolist()]
    payoff_df = payoff_df[[payoff_df.columns[-1]] + payoff_df.columns[:-1].tolist()]

    # multiply by the quantity : 
    payoff_df["payoff"] = payoff_df["payoff"] * quantity

    return payoff_df


def add_payoff_total(df, groupby_column="greek", price_colum="s", payoff_colum="payoff", id_column="id"):
    # check if the total column already exists in the df : 
    if "total" in df[id_column].unique():
        df = df[df[id_column] != "total"]
    if groupby_column is not None: 
        df = df[df[groupby_column].str.contains("_total" ) == False]
    groupby = [groupby_column, price_colum]
    # remove None values
    groupby = [x for x in groupby if x is not None]
    # Group by and sum the specified payoff column
    result = df.groupby(groupby).agg({  payoff_colum: "sum"}).reset_index()
    # Add new columns to the result DataFrame
    if groupby_column is not None:
        result[groupby_column] = result[groupby_column] + "_total"
    else:
        result["contractSymbol"] = "total"
    result["line_type"] = "solid"
    result["ls"] = None
    result["cp"] = None
    result[id_column] = "total"

    df["line_type"] = "dash"

    # Concatenate the original df with the result DataFrame
    combined_df = pd.concat([df, result], ignore_index=True)

    return combined_df
