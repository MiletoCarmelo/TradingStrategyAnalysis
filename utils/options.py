import numpy as np
import pandas as pd
import utils.yahoo as yf
from datetime import datetime
import optionlab as ol


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


def get_indelying_perf(ticker, sharePerContract, quantity, ls, cp, strike, tickerPrice, lastPrice, startAnalysisDate, expirationDate, volatility, rfrValue, minStock, maxStock,  date_start=None):

    
    if rfrValue > 0.2: 
        rfrValue = rfrValue / 100

    if startAnalysisDate is None:
        startAnalysisDate = datetime.now().strftime("%Y-%m-%d")

    input_data = {
        "stock_price": tickerPrice,
        "start_date": startAnalysisDate,
        "target_date": expirationDate,
        "volatility": volatility,
        "interest_rate": rfrValue,
        "min_stock": minStock,
        "max_stock": maxStock,
        "strategy": [
            {
                "type": cp.lower(),
                "strike": strike,
                "premium": lastPrice,
                "n": sharePerContract,
                "action": "buy" if ls.lower() == "long" else "sell"
            },
        ],
    }

    out = ol.run_strategy(input_data)

    # Calculating means
    mean_implied_volatility = sum(out.implied_volatility) / len(out.implied_volatility)
    mean_in_the_money_probability = sum(out.in_the_money_probability) / len(out.in_the_money_probability)

    i = 0
    total_delta = out.delta[i] * quantity * sharePerContract
    total_gamma = out.gamma[i] * quantity * sharePerContract
    total_theta = out.theta[i] * quantity * sharePerContract
    total_vega = out.vega[i] * quantity * sharePerContract

    # Failed to add instrument to portfolio: If using all scalar values, you must pass an index

    profit_ranges = out.profit_ranges # [(233.81, inf)]
    # Summary output
    summary = pd.DataFrame([out.probability_of_profit], columns=["probability_of_profit"])
    summary["profit_ranges_min"] = out.profit_ranges[0][0]
    summary["profit_ranges_max"] = out.profit_ranges[0][1]
    summary["strategy_cost"] = out.strategy_cost
    summary["minimum_return_in_the_domain"] = out.minimum_return_in_the_domain
    summary["maximum_return_in_the_domain"] = out.maximum_return_in_the_domain
    summary["delta"] = total_delta
    summary["gamma"] = total_gamma
    summary["theta"] = total_theta
    summary["vega"] = total_vega

    #   Variable	                Type	        Aggregation
    #   Per Leg Cost	            Cost	        Sum
    #   Implied Volatility	        Percentage	    Mean
    #   In-the-Money Probability	Probability	    Mean
    #   Delta	                    Sensitivity	    Sum
    #   Gamma	                    Sensitivity	    Sum
    #   Theta	                    Sensitivity	    Sum
    #   Vega	                    Sensitivity	    Sum
    #   Probability of Profit	    Probability	    Mean
    #   Profit Ranges	            Profit	        List

    return summary


def get_strategy_perfs(portfolio_list, startAnalysisDate, rfrValue, periodDomain="1y"):

    perfs = pd.DataFrame()

    # Failed to add instrument to portfolio: 'list' object has no attribute 'lower'
    
    for i in range(len(portfolio_list)):
        row = portfolio_list.iloc[i]
        min_max_s = yf.get_stock_min_max(row.ticker,period=periodDomain)
        perf = get_indelying_perf(  row.ticker,
                                    row.shares, 
                                    row.quantity,
                                    row.ls,
                                    row.cp,
                                    row.strike,
                                    row.tickerPrice, 
                                    row.lastPrice,
                                    startAnalysisDate, 
                                    row.expirationDate, 
                                    yf.calculate_volatility(row.ticker, period=periodDomain),
                                    rfrValue, 
                                    min_max_s[0],
                                    min_max_s[1])
        perfs = pd.concat([perfs, perf])

    return perfs