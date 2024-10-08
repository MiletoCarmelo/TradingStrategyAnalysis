# import norm from scipy.stats
from scipy.stats import norm
import numpy as np
import pandas as pd
from datetime import datetime

import utils.utils as ut
import utils.yahoo as yf

# calcul the option price : 
def calculate_d1(S, K, r, sigma, T):
    return (np.log(S / K) + (r + sigma ** 2 / 2) * T) / (sigma * np.sqrt(T))


# calcul normal distribution : 
def calculate_normal_distribution(x):
    return norm.cdf(x)


# calcul normal distribution density :
def calculate_normal_distribution_density(d1):
    return norm.pdf(d1)


# calcul delta :
def calculate_delta(type, ls, cp, S, K, r, sigma, T):
    if type.lower() == 'option':
        d1 = calculate_d1(S, K, r, sigma, T)
        if cp.lower() == 'call':
            delta = calculate_normal_distribution(d1)
        elif cp.lower() == 'put':
            delta = calculate_normal_distribution(d1) - 1
        if ls.lower() == 'short':
            delta = -delta
        return delta
    elif type.lower() == 'stock':
        if ls.lower() == 'long':
            return 1
        elif ls.lower() == 'short':
            return -1


# calcul vega :
def calculate_vega(type, ls, S, K, r, sigma, T):
    if type.lower() == 'option':
        d1 = calculate_d1(S, K, r, sigma, T)
        if ls.lower() == 'long':
            return S * calculate_normal_distribution_density(d1) * np.sqrt(T)
        elif ls.lower() == 'short':
            return -S * calculate_normal_distribution_density(d1) * np.sqrt(T)
    if type.lower() == 'stock':
        return 0


# calcul gamma :
def calculate_gamma(type, ls, S, K, r, sigma, T):
    if type.lower() == 'option':
        d1 = calculate_d1(S, K, r, sigma, T)
        if ls.lower() == 'long':
            return calculate_normal_distribution_density(d1) / (S * sigma * np.sqrt(T))
        elif ls.lower() == 'short':
            return -1 * calculate_normal_distribution_density(d1) / (S * sigma * np.sqrt(T))
    if type.lower() == 'stock':
        return 0


# calcul theta :
def calculate_theta(type, ls, S, K, r, sigma, T):
    if type.lower() == 'stock':
        return 0
    if type.lower() == 'option':
        d1 = calculate_d1(S, K, r, sigma, T)
        d2 = d1 - sigma * np.sqrt(T)
        # Common term for calculations
        theta_common = -S * calculate_normal_distribution_density(d1) * sigma / (2 * np.sqrt(T))
        if ls.lower() == 'long':
            theta = theta_common - r * K * np.exp(-r * T) * calculate_normal_distribution(d2)
        elif ls.lower() == 'short':
            theta = -theta_common + r * K * np.exp(-r * T) * calculate_normal_distribution(d2)
        return theta


# calcul rho :
def calculate_rho(type, ls, S, K, r, sigma, T):
    if type.lower() == 'stock':
        return 0
    if type.lower() == 'option':
        d2 = calculate_d1(S, K, r, sigma, T) - sigma * np.sqrt(T)
        if ls.lower() == 'long':
            return K * T * np.exp(-r * T) * calculate_normal_distribution(d2)
        elif ls.lower() == 'short':
            return -K * T * np.exp(-r * T) * calculate_normal_distribution(d2)


# calcul all greeks letters of portfolio : 
def calculate_greeks_portfolio(portfolio_list, risk_free_rate):

    greeks = pd.DataFrame(columns=["delta", "gamma", "vega", "theta", "rho"])

    for i in range(len(portfolio_list)):
        row = portfolio_list.iloc[i]
        sigma = yf.calculate_volatility(row.ticker)
        date = row.expirationDate if row.expirationDate is not None else datetime.now().strftime("%Y-%m-%d")
        T = ut.days_to_year_fraction(date)

        # calcul delta : 
        d = calculate_delta(row.type,
                            row.ls,
                            row.cp,
                            row.tickerPrice,
                            row.strike,
                            risk_free_rate,
                            sigma, 
                            T)
        # calcul gamma : 
        g = calculate_gamma(row.type,
                            row.ls,
                            row.tickerPrice,
                            row.strike,
                            risk_free_rate,
                            sigma, 
                            T)
        # calcul vega : 
        v = calculate_vega( row.type,
                            row.ls,
                            row.tickerPrice,
                            row.strike,
                            risk_free_rate,
                            sigma, 
                            T)
        # calcul theta : 
        t = calculate_theta(row.type,
                            row.ls,
                            row.tickerPrice,
                            row.strike,
                            risk_free_rate,
                            sigma, 
                            T)
        # calcul rho :
        r = calculate_rho(  row.type,
                            row.ls,
                            row.tickerPrice,
                            row.strike,
                            risk_free_rate,
                            sigma, 
                            T)

        greeks = greeks._append({"delta": d, "gamma": g, "vega": v, "theta": t, "rho":r}, ignore_index=True)

    return (
                greeks["delta"].sum(), 
                greeks["gamma"].sum(), 
                greeks["vega"].sum(), 
                greeks["theta"].sum(),
                greeks["rho"].sum()
            )


def get_greek_curve(ticker, type, ls, cp, strike, expirationDate, risk_free_rate, min_s, max_s):

     # Create an array from min_s to max_s with a step of 1
    price_range = np.arange(min_s, max_s, 1)  # +1 to include max_s in the range

    # filter price range > 0
    price_range = price_range[price_range > 0]

    sigma = yf.calculate_volatility(ticker)
    if expirationDate is None:
        expirationDate = datetime.now().strftime("%Y-%m-%d")
    T = ut.days_to_year_fraction(expirationDate)

    delta_values = pd.DataFrame(columns=["s", "greek", "ticker", "value"])
    gamma_values = pd.DataFrame(columns=["s", "greek", "ticker", "value"])
    vega_values = pd.DataFrame(columns=["s", "greek", "ticker", "value"])
    theta_values = pd.DataFrame(columns=["s", "greek", "ticker", "value"])
    rho_values = pd.DataFrame(columns=["s", "greek", "ticker", "value"])
    
    delta_values['s'] = price_range
    delta_values['ticker'] = ticker
    delta_values['greek'] = "delta"

    gamma_values['s'] = price_range
    gamma_values['ticker'] = ticker
    gamma_values['greek'] = "gamma"

    vega_values['s'] = price_range
    vega_values['ticker'] = ticker
    vega_values['greek'] = "vega"

    theta_values['s'] = price_range
    theta_values['ticker'] = ticker
    theta_values['greek'] = "theta"

    rho_values['s'] = price_range
    rho_values['ticker'] = ticker
    rho_values['greek'] = "rho"

    delta_values['value'] = delta_values.apply(lambda x: calculate_delta(   type,
                                                                            ls,
                                                                            cp, 
                                                                            x.s,
                                                                            strike,
                                                                            risk_free_rate,
                                                                            sigma,
                                                                            T), axis=1)

    gamma_values['value'] = gamma_values.apply(lambda x: calculate_gamma(   type,
                                                                            ls,
                                                                            x.s,
                                                                            strike,
                                                                            risk_free_rate,
                                                                            sigma,
                                                                            T), axis=1)
    
    vega_values['value'] = vega_values.apply(lambda x: calculate_vega(  type,
                                                                        ls,
                                                                        x.s,
                                                                        strike,
                                                                        risk_free_rate,
                                                                        sigma,
                                                                        T), axis=1)

    theta_values['value'] = theta_values.apply(lambda x: calculate_theta(   type,
                                                                            ls,
                                                                            x.s,
                                                                            strike,
                                                                            risk_free_rate,
                                                                            sigma,
                                                                            T), axis=1)

    rho_values['value'] = rho_values.apply(lambda x: calculate_rho(     type,
                                                                        ls,
                                                                        x.s,
                                                                        strike,
                                                                        risk_free_rate,
                                                                        sigma,
                                                                        T), axis=1)

    greeks_values = pd.DataFrame(columns=["s", "greek", "ticker", "value"])
    greeks_values = greeks_values._append(delta_values)
    greeks_values = greeks_values._append(gamma_values)
    greeks_values = greeks_values._append(vega_values)
    greeks_values = greeks_values._append(theta_values)
    greeks_values = greeks_values._append(rho_values)

    return greeks_values
