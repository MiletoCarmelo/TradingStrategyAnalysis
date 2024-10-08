from taipy.gui import notify, Markdown, Gui
import pandas as pd
from datetime import datetime, timedelta

import utils.options as opt
import utils.yahoo as yf
import utils.plots as plt
import utils.greeks as gr

layout = {
    "margin": {
        "l": 70,  # left margin
        "r": 30,  # right margin
        "t": 30,  # top margin
        "b": 70   # bottom margin
    }
}

layout_greeks= {
    "margin": {
        "l": 70,  # left margin
        "r": 30,  # right margin
        "t": 30,  # top margin
        "b": 70   # bottom margin
    }
}

column_names = ['type', 'currency', 'ticker',
                'lastTradeDate', 'ls', 'cp', 'strike', 'lastPrice',
                'bid', 'ask', 'volume', 'openInterest', 'impliedVolatility', 
                'inTheMoney', 'contractSize', 'expirationDate', 'tickerPrice', 'contractSymbol']

column_names_portfolio = [  'show', 'id', 'quantity', 'type', 'ticker', 
                            'ls', 'cp', 'expirationDate', 'inTheMoney', 'strike', 'lastPrice', 
                            'tickerPrice', 'currency', 'volume', 
                            'contractSize', 'contractSymbol']

columns_names_payroll = ['s', 'payoff', 'ls', 'cp', 'type', 'contractSymbol', 'id', 'line_type']

columns_names_greeks = ['s', 'greek', 'value', 'id', 'line_type']


# Initial data
ticker = ""
shortlong_value = "LONG"
callput_value = "CALL"
stockoption_value = "OPTION"
rfr_value = 1
aquisition_dates_sel = None
aquisition_dates = []
expiration_dates = []
expiration_dates_sel = None
data_selection = pd.DataFrame(columns=column_names)
data_portfolio = pd.DataFrame(columns=column_names_portfolio)
data_portfolio_row_seletion = []
min_max_s = [0,400]
data_payoff = pd.DataFrame(columns=columns_names_payroll)
plot_payoff = None
data_greeks = pd.DataFrame(columns=columns_names_greeks)
plot_delta = None
plot_gamma = None
plot_vega = None
plot_theta = None
plot_rho = None


# functions for the inputs tools (vertical left bar)


def update_expiration_dates(state):
    ticker = state.ticker
    if ticker == "":
        notify(state, "error", f"Enter a correct ticker")
    else : 
        try:
            dates_list = []
            options_df = yf.get_options_expirations_dates(ticker)
            if options_df is not None and not options_df.empty:
                state.expiration_dates = [date.strftime('%Y-%m-%d') for date in options_df['Expiration Dates']]
                state.expiration_dates_sel = state.expiration_dates[0]
                notify(state, "success", f"Expiration dates updates for {ticker}")
                state.aquisition_dates = [datetime.today().date()]
                state.aquisition_dates_sel = state.aquisition_dates[0]
                notify(state, "success", f"Aquisition date update for {ticker}")
            # if dates_list is empty, set the initial value and date_list to tomorrow date 
            else :
                notify(state, "warning", f"Wrong ticker : {ticker}")
        except Exception as e:
            notify(state, "error", f"Failed to fetch data: {str(e)}")


def update_option_table(state):
    try:
        state.data_selection = yf.get_options_list( state.ticker, 
                                                [state.expiration_dates_sel], 
                                                state.shortlong_value, 
                                                state.callput_value)
        notify(state, "success", f'Option proposition(s) list updated')   
    except Exception as e:
        notify(state, "error", f"Failed to show option proposition(s): {str(e)}")


def update_stock_table(state):
    try: 
        state.data_selection = yf.get_stock_list(state.ticker, state.shortlong_value)
        notify(state, "success", f'Stock proposition(s) list updated')   
    except Exception as e:
        notify(state, "error", f"Failed to show stock proposition(s): {str(e)}")


# functions for tables : 


def update_portfolio_table(state, var_name, payload):
    try : 
        idx = payload["index"]
        data_portfolio_tmp = state.data_selection.iloc[[idx]]  # Use double brackets to keep it as a DataFrame
        data_portfolio_tmp = data_portfolio_tmp.reset_index(drop=True)
        data_portfolio_tmp.loc[:,"id"] = 0
        data_portfolio_tmp.loc[:, "quantity"] = 1
        data_portfolio_tmp.loc[:,"show"] = True
        if data_portfolio_tmp["contractSymbol"][0] in state.data_portfolio["contractSymbol"].values:
            notify(state, "warning", f'Selected instrument already in portfolio')
        else: 
            if len(state.data_portfolio[column_names_portfolio]) > 0 :
                state.data_portfolio = pd.concat([state.data_portfolio[column_names_portfolio], data_portfolio_tmp[column_names_portfolio]], ignore_index=True)
            else : 
                state.data_portfolio = data_portfolio_tmp[column_names_portfolio]
            state.data_portfolio["id"] = 0  
            state.data_portfolio = state.data_portfolio.drop_duplicates()
            state.data_portfolio['id'] = [i for i in range(len(state.data_portfolio))]
            state.data_portfolio = state.data_portfolio.reset_index(drop=True) 
            notify(state, "success", f'Line {idx} added to portfolio') 
            # update state variable pipeline : 
            update_states_variables_pipeline(state, state.data_payoff[0:0],state.data_portfolio, min_max_s, state.rfr_value)
            notify(state, "success", f'Payoff data updated')    
    except Exception as e:
            notify(state, "error", f"Failed to add instrument to portfolio: {str(e)}")


        # state.data_payoff = update_payoff(state.data_payoff, state.data_portfolio.iloc[[-1]], state.min_max_s)
        # state.data_payoff = opt.add_payoff_total(state.data_payoff, groupby_column=None, price_colum="s", payoff_colum="payoff", id_column="id")
        # state.plot_payoff = plt.create_plot(    data=state.data_payoff, 
        #                                         x_column='s', 
        #                                         y_column='payoff', 
        #                                         color_column='id', 
        #                                         line_type_column='line_type', 
        #                                         x_title=None, 
        #                                         y_title=None, 
        #                                         title=None)


def delete_portfolio_table(state, var_name, payload):
    try:
        idx = payload["index"]
        inst = state.data_portfolio.iloc[idx]
        inst = inst.contractSymbol
        # drop row from state.data_portfolio
        state.data_portfolio = state.data_portfolio.drop(idx).reset_index(drop=True)
        state.data_portfolio['id'] = [i for i in range(len(state.data_portfolio))]
        notify(state, "success", f'Line {idx} removed from portfolio')    
        # update state variable pipeline : 
        update_states_variables_pipeline(state, state.data_payoff[0:0],state.data_portfolio, state.min_max_s, state.rfr_value)
        notify(state, "success", f'Line {idx} removed from data payoff')  

    except Exception as e:
            notify(state, "error", f"Failed to remove instrument from portfolio: {str(e)}")


def update_inputs_portfolio_table(state, var_name, payload):
    try :
        idx = payload["index"]
        col = payload["col"]
        val = payload["value"]
        if col == "quantity":
            usr_val = payload["user_value"]
            if usr_val.isdigit():
                state.data_portfolio.loc[idx,col] = int(val)
                notify(state, "success", f'Quantity successfully updated')
                data_portfolio = state.data_portfolio
            else : 
                notify(state, "warning", f"Failed to update the quantity: {str(val)} is not an int.")
        if col == "show": 
            state.data_portfolio.loc[idx,col] = val
            data_portfolio = state.data_portfolio[state.data_portfolio["show"] == True]
        # update state variable pipeline : 
        update_states_variables_pipeline(state, state.data_payoff[0:0],data_portfolio,min_max_s, state.rfr_value)
    except Exception as e:
            notify(state, "error", f"Update failed: {str(e)}")


def reset_tables(state):
    state.data_portfolio = state.data_portfolio.iloc[0:0] 
    state.data_selection = state.data_selection.iloc[0:0]
    state.ticker = ""
    state.shortlong_value = "LONG"
    state.callput_value = "CALL"
    state.stockoption_value = "OPTION"
    state.rfr_value = 1
    state.aquisition_dates_sel = None   
    state.aquisition_dates = []
    state.expiration_dates = []
    state.expiration_dates_sel = None
    state.data_payoff = state.data_payoff.iloc[0:0]
    state.plot_payoff = None
    data_greeks = data_greeks.iloc[0:0]
    plot_delta = None
    plot_gamma = None
    plot_vega = None
    plot_theta = None
    plot_rho = None

# pipe line data update for plots : 


def update_min_max_s(portfolio_table):
    df = portfolio_table
    if len(df['strike']) == 1:
        strike = [df['strike'].values]
        tickerPrice = [df["tickerPrice"].values]
    elif len(df['strike']) == 0:
        strike = [0]
        tickerPrice = [200]
    else: 
        strike = df['strike'].values
        tickerPrice = df["tickerPrice"].values

    # Calculate min and max stock price range
    min_s = max(0, min(tickerPrice))
    max_s = max(tickerPrice)

    # Adjust min and max for the slider
    min_s = max(0, int(min_s - max_s * 0.3))
    max_s = int(max_s + max_s * 0.3)

    return [min_s,max_s]


def update_payoff(data_payoff, data_portfolio, min_max_s):
    min_value = min_max_s[0]
    max_value = min_max_s[1]
    for i in range(len(data_portfolio)):
        row = data_portfolio.iloc[i]
        if row.contractSymbol not in data_payoff["contractSymbol"]:
            if row.type == "option":
                prices = [row.strike]
                option_price = [row.lastPrice]
            else :
                prices = [row.tickerPrice]
                option_price = [0]
            payoffs_tmp = opt.get_payoffs(  ticker=row.ticker, 
                                            strike_prices=prices, 
                                            option_price=option_price,
                                            quantity=row.quantity,
                                            ls=row.ls, 
                                            cp=row.cp, 
                                            type=row.type,
                                            min_s=min_value, 
                                            max_s=max_value, 
                                            interval=1)
            payoffs_tmp['ls'] = row.ls
            payoffs_tmp['cp'] = row.cp
            payoffs_tmp['type'] = row.type
            payoffs_tmp['contractSymbol'] = row.contractSymbol
            payoffs_tmp['id'] = row.id
            payoffs_tmp['line_type'] = 'dash'
            data_payoff = pd.concat([data_payoff, payoffs_tmp], ignore_index=True)
    return data_payoff


def update_plot_playoff(state, data_payoff, data_portfolio, min_max_s):
    state.data_payoff = update_payoff(  data_payoff, 
                                        data_portfolio, 
                                        min_max_s)
    state.data_payoff = opt.add_payoff_total(   state.data_payoff, 
                                                groupby_column=None, 
                                                price_colum="s", 
                                                payoff_colum="payoff", 
                                                id_column="id")
    state.plot_payoff = plt.create_plot(    data=state.data_payoff, 
                                            x_column='s', 
                                            y_column='payoff', 
                                            color_column='id', 
                                            line_type_column='line_type', 
                                            x_title=None, 
                                            y_title=None, 
                                            title=None)


def update_greeks_plot(state, data_greeks, data_portfolio, risk_free_rate):


        # Failed to add instrument to portfolio: cannot access local variable 'delta' where it is not associated with a value

        min_value, max_value = state.min_max_s

        data_greeks = data_greeks[0:0]

        # Create the plot
        for i in range(len(data_portfolio)):
            row = data_portfolio.iloc[i]
            print(row)
            greeks_tmp = gr.get_greek_curve(    ticker=row.ticker,
                                                type=row.type,
                                                ls=row.ls,
                                                cp=row.cp,
                                                strike=row.strike,
                                                expirationDate=row.expirationDate,
                                                risk_free_rate=risk_free_rate,
                                                min_s=min_value,
                                                max_s=max_value)
            print(" => ", i)
            greeks_tmp['contractSymbol'] = row.contractSymbol
            greeks_tmp['id'] = row.id
            greeks_tmp['line_type'] = 'dash'
            data_greeks = pd.concat([data_greeks, greeks_tmp[columns_names_greeks]], ignore_index=True)

        # add total delta : 
        data_greeks = opt.add_payoff_total( data_greeks,
                                            groupby_column="greek", 
                                            price_colum="s", 
                                            payoff_colum="value", 
                                            id_column="id")

        print(data_greeks)

        print("2")
        # get greeks data 
        delta_df = data_greeks[data_greeks["greek"]=="delta"]
        gamma_df = data_greeks[data_greeks["greek"]=="gamma"]
        vega_df = data_greeks[data_greeks["greek"]=="vega"]
        theta_df = data_greeks[data_greeks["greek"]=="theta"]
        rho_df = data_greeks[data_greeks["greek"]=="rho"]

        # reset index
        delta_df = delta_df.reset_index(drop=True)
        gamma_df = gamma_df.reset_index(drop=True)
        vega_df = vega_df.reset_index(drop=True)
        theta_df = theta_df.reset_index(drop=True)
        rho_df = rho_df.reset_index(drop=True)

        print("3")
        # generate the plot
        plot_delta = plt.create_plot(   data=delta_df, 
                                        x_column='s', 
                                        y_column='value', 
                                        color_column='id', 
                                        line_type_column='line_type', 
                                        x_title="S", 
                                        y_title="Delta", 
                                        title=None, 
                                        legend=True)

        plot_gamma = plt.create_plot(   data=gamma_df, 
                                        x_column='s', 
                                        y_column='value', 
                                        color_column='id', 
                                        line_type_column='line_type', 
                                        x_title="S", 
                                        y_title="Gamma", 
                                        title=None, 
                                        legend=True)

        plot_vega = plt.create_plot(    data=vega_df, 
                                        x_column='s', 
                                        y_column='value', 
                                        color_column='id', 
                                        line_type_column='line_type', 
                                        x_title="S", 
                                        y_title="Vega", 
                                        title=None, 
                                        legend=True)

        plot_theta = plt.create_plot(   data=theta_df, 
                                        x_column='s', 
                                        y_column='value', 
                                        color_column='id', 
                                        line_type_column='line_type', 
                                        x_title="S", 
                                        y_title="Theta", 
                                        title=None,
                                        legend=True)

        plot_rho = plt.create_plot(     data=rho_df,
                                        x_column='s',
                                        y_column='value',
                                        color_column='id',
                                        line_type_column='line_type',
                                        x_title="S",
                                        y_title="Rho",
                                        title=None,
                                        legend=True)

        print("4")
        for i in range(len(data_portfolio)):
            row = data_portfolio.iloc[i]
            # if row.tickerPrice > min_value and row.tickerPrice < max_value:
            #    plot = plt.add_vertical_bar(plot, x_value=row.tickerPrice, info="s" + str(row.id))
            if row.type == "option":
                if row.strike > min_value and row.strike < max_value:
                    plot_delta = plt.add_vertical_bar(plot_delta, x_value=row.strike, info="k" + str(row.id), color_id_nb=i, legend=True)
                    plot_gamma = plt.add_vertical_bar(plot_gamma, x_value=row.strike, info="k" + str(row.id), color_id_nb=i, legend=True)
                    plot_vega = plt.add_vertical_bar(plot_vega, x_value=row.strike, info="k" + str(row.id), color_id_nb=i, legend=True)
                    plot_theta = plt.add_vertical_bar(plot_theta, x_value=row.strike, info="k" + str(row.id), color_id_nb=i, legend=True)
                    plot_rho = plt.add_vertical_bar(plot_rho, x_value=row.strike, info="k" + str(row.id), color_id_nb=i, legend=True)

        print("5")

        state.plot_delta = plot_delta
        state.plot_gamma = plot_gamma
        state.plot_vega = plot_vega
        state.plot_theta = plot_theta
        state.plot_rho = plot_rho


def update_states_variables_pipeline(state, data_payoff, data_portfolio, min_max_s, rfr_value):
    if data_payoff is None:
        data_payoff = state.data_payoff
    if data_portfolio is None:
        data_portfolio = state.data_portfolio
    if min_max_s is None:
        min_max_s = state.min_max_s
    if rfr_value is None:
        rfr_value = state.rfr_value
    # update min max s : 
    state.min_max_s = update_min_max_s(data_portfolio)
    notify(state, "success", f"s range updated")
    #  update payoff plot: 
    update_plot_playoff(state, data_payoff, data_portfolio, min_max_s)
    notify(state, "success", f"Payoff plot updated")
    #  update greeks plots:
    update_greeks_plot(state, data_greeks, data_portfolio, rfr_value)
    notify(state, "success", f"Greeks plot updated")
    


# Define the option page content
option_page = """
### Call or put
<|{callput_value}|toggle|lov=CALL;PUT|class_name=selector|>
### Expiration Dates
<|{expiration_dates_sel}|selector|type=str|lov={expiration_dates}|adapter={lambda u: u}|dropdown=True|>
### Risk-Free Rate
<|{rfr_value}|number|label=Risk-Free Rate|>
---
<|Get option list|button|class_name=button|on_action=update_option_table|>
"""

# Define the stock page content
stock_page = """
### Aquisition Date
<|{aquisition_dates_sel}|selector|type=str|lov={aquisition_dates}|adapter={lambda u: u}|dropdown=True|>
---
<|Get stock list|button|class_name=button|on_action=update_stock_table|>
"""

tables = """
<|layout|columns=1 2|
    <|
Instrument selection 
<|{data_selection}|table|class_name=tables|page_size=10|page_size_options=10|on_action=update_portfolio_table|hover_text=Click on the row to add it to the Portfolio.|>
    |>

    <|
Portfolio 
<|{data_portfolio}|table|class_name=tables|page_size=10|page_size_options=10|on_delete=delete_portfolio_table|hover_text=You can edit the quantiy.|editable=False|editable[show]=True|editable[quantity]=True|on_edit=update_inputs_portfolio_table|rebuild=True|selected={data_portfolio_row_seletion}|>
    |>

|>
"""

greeks_page = """
<|layout|columns=1 1 1 1 1|
    <|
<|chart|figure={plot_delta}|>
    |>

    <|
<|chart|figure={plot_gamma}|>
    |>

    <|
<|chart|figure={plot_vega}|>
    |>

    <|
<|chart|figure={plot_theta}|>
    |>

    <|
<|chart|figure={plot_rho}|>
    |>

|>
"""


options = Markdown("""

<|layout|columns=1 9|

    <|
<|RESET|button|class_name=button_reset|on_action=reset_tables|>

---

Selected Tickers 
<|{ticker}|input|label=Ticker|on_change=update_expiration_dates|on_action=update_expiration_dates|>
Long or Short 
<|{shortlong_value}|toggle|lov=LONG;SHORT|class_name=selector|>

---

<|Option|expandable|expanded=False|class_name=custom-expandable|
""" + option_page + """ 
|>
<|Stock|expandable|expanded=False|class_name=custom-expandable|
""" + stock_page + """
|>

--- 

S range
<|{min_max_s}|slider|min={min_max_s[0]}|max={min_max_s[1]}|on_change=update_plot_playoff|>

    |>

    <|
# Options Profit Calculator

---

""" + tables + """

---

<|chart|figure={plot_payoff}|>

--- 

""" + greeks_page + """
    |>



|>
""")


# <|chart|figure={fig}|height=500px|width=100%|layout={layout}|>
# <|{data_payoff}|chart|type=lines|id=chart1|x=s|y=payoff|color=id|height=500px|width=100%|labels=id|layout={layout}|>