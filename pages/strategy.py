from taipy.gui import notify, Markdown
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

import utils.plots as plt
import utils.ta as teca


layout = {
    "margin": {
        "l": 70,  # left margin
        "r": 30,  # right margin
        "t": 30,  # top margin
        "b": 70   # bottom margin
    }
}

layout_bar = {
    "bargap": 0.1,  # Gap between bars
    "bargroupgap": 0.1 , # Gap between groups of bars
    "margin": {
        "l": 70,  # left margin
        "r": 30,  # right margin
        "t": 30,  # top margin
        "b": 70   # bottom margin
    }
}

columns_price_and_ta = ["Ticker", "Datetime", "Close", "Volume", "line_type", "id", "chart_category"]
columns_price = ["Ticker", "Datetime", "Open", "High", "Low", "Close", "Volume", "line_type", "id", "chart_category"]

# Initial data
ticker = None
tickers_list = [] #  pd.DataFrame(columns=["Ticker"])
ticker_selected = None
start_date = datetime.today() - timedelta(days=1)
# get yesterday's date: 
end_date = datetime.today()
intervals = ['1m', '2m', '5m', '15m', '30m', '1h', '1d', '1wk', '1mo', '6mo', '1y']
interval = '1m'
data_price_and_ta = pd.DataFrame(columns=columns_price_and_ta)
plot_price_and_ta = None
plot_purcentage_and_ta = None
plot_purcentage_positive_and_ta = None
ta_list = teca.indicators()
ta = teca.indicators()[0]
ti_list = []
ti_list_selected = []


window=10
short_window=10
long_window=20
span=9
smoothing=2


def reset_tables(state):
    # Initial data
    state.ticker = None
    state.tickers_list = [] # tickers_list[0:0]
    state.start_date = datetime.today() - timedelta(days=1)
    # get yesterday's date: 
    state.end_date = datetime.today()
    state.intervals = state.intervals
    state.interval = '1m'
    state.data_price_and_ta = state.data_price_and_ta[0:0]
    state.plot_price_and_ta = None
    state.plot_purcentage_and_ta = None
    state.plot_purcentage_positive_and_ta = None
    state.ta = ta_list[0]
    state.ti_list = []
    state.ti_list_selected = []



def fetch_data_price(ticker, start_date, end_date, interval="1d"):
    stock = yf.Ticker(ticker)
    data = stock.history(start=start_date, end=end_date, interval=interval)
    data["Ticker"] = ticker.upper()
    # rename index to DateTIme 
    date = data.rename_axis("Datetime")
    data = data.reset_index(drop=False)
    return data


def update_data_price(state, ticker_selected, start_date, end_date, interval):
    # drop duplicates : 
    # state.tickers_list = state.tickers_list.drop_duplicates() 
    # get tickers missing in the data_price : 
    try:
        if ticker_selected is not None : # len(tickers_list) >0 :
            # tickers_list = list(set(state.tickers_list["Ticker"]))
            # for ticker in tickers_list:
            data_price_and_ta_tmp = fetch_data_price(ticker_selected, start_date, end_date, interval)
            data_price_and_ta_tmp["line_type"] = "solid"
            data_price_and_ta_tmp["id"] = "close"
            data_price_and_ta_tmp["chart_category"] = "price"
            state.data_price_and_ta = state.data_price_and_ta._append(data_price_and_ta_tmp[columns_price_and_ta])
            notify(state, "success", f"Data updated for the portfolio")
        else: 
            notify(state, "warning", f"Please fill the portfolio behore.")
    except Exception as e:
        notify(state, "error", f"Failed to fetch data: {str(e)}")


def add_to_porfolio(state):
    if state.ticker is not None and state.ticker != "" and state.ticker not in state.tickers_list: # ["Ticker"].values:
        # state.tickers_list = pd.concat([state.tickers_list, pd.DataFrame([state.ticker], columns=["Ticker"])], ignore_index=True)
        # state.tickers_list = state.tickers_list.reset_index(drop=True)
        state.tickers_list = state.tickers_list + [state.ticker]
        notify(state, "success", f"Added '{state.ticker}' to the portfolio")
    else : 
        notify(state, "warning", f"Please provide a valied ticker")


def on_delete_table(state, var_name, payload):
    index = payload["index"] # row index
    # state.tickers_list = state.tickers_list.drop(index=index)
    state.tickers_list = state.tickers_list.remove(index)
    notify(state, "E", f"Deleted row at index '{index}'")

def pipeline(state): 
    if state.ticker_selected is not None and state.ticker_selected != "":
        state.data_price_and_ta = state.data_price_and_ta[0:0]
        # get prices from yahoo finance:
        update_data_price(state, state.ticker_selected, state.start_date, state.end_date, state.interval)
        # plot the data : 
        update_plot(state)
    else: 
        notify(state, "warning", f"Please select a ticker from the portfolio or add a new one")

def pipeline_ta(state):
    try : 
        data_ta = state.data_price_and_ta[state.data_price_and_ta["id"]=="close"].copy()
        data_ta = teca.calculate_indicator( state.ta, 
                                            data_ta, 
                                            "Close",
                                            int(state.window), 
                                            int(state.short_window),
                                            int(state.long_window), 
                                            int(state.span), 
                                            int(state.smoothing))
        data_ta["line_type"] = "dash"
        data_ta["Ticker"] = state.ticker
        data_ta = data_ta[columns_price_and_ta]
        for i in range(len(data_ta["id"].unique())):
            if data_ta["id"].unique()[i] not in state.ti_list:
                notify(state, "warning", f"Technical indicator already on the chart")
            data_ta_tmp = data_ta[data_ta["id"]==data_ta["id"].unique()[i]]
            state.data_price_and_ta = state.data_price_and_ta._append(data_ta_tmp)
            # add the ta to the list of selected ta
            state.ti_list = state.ti_list + [data_ta["id"].unique()[i]]
            state.ti_list = list(set(state.ti_list))
            state.ti_list_selected = state.ti_list_selected + [data_ta["id"].unique()[i]]
            state.ti_list = list(set(state.ti_list_selected))
            update_plot(state)
            notify(state, "success", f"Technical indicator added to the chart")
    except Exception as e :
        notify(state, "error", f"Failed to calculate the technical indicator selected: {str(e)}")

def update_plot(state):
    # select only ti from the list of selected ti and the close price
    data_price_and_ta = state.data_price_and_ta[state.data_price_and_ta["id"].isin(state.ti_list_selected + ["close"])].copy()
    # filter chart_category = price 
    data_chart_category_price = data_price_and_ta[data_price_and_ta["chart_category"]=="price"].copy()
    state.plot_price_and_ta = plt.create_plot(  data=data_chart_category_price, 
                                                x_column='Datetime', 
                                                y_column='Close', 
                                                color_column='id', 
                                                line_type_column='line_type', 
                                                x_title="Datetime", 
                                                y_title="Close", 
                                                title=None)
    data_chart_category_purcentage = data_price_and_ta[data_price_and_ta["chart_category"]=="purcentage"].copy()
    if len(data_chart_category_purcentage) > 0:
        state.plot_purcentage_and_ta = plt.create_plot(  data=data_chart_category_purcentage, 
                                                        x_column='Datetime', 
                                                        y_column='Close', 
                                                        color_column='id', 
                                                        line_type_column='line_type', 
                                                        x_title=None, 
                                                        y_title=None, 
                                                        title=None)
    data_chart_category_purcentage_positive = data_price_and_ta[data_price_and_ta["chart_category"]=="purcentage_positive"].copy()

    if len(data_chart_category_purcentage_positive) > 0:
        state.plot_purcentage_positive_and_ta = plt.create_plot(    data=data_chart_category_purcentage_positive, 
                                                                    x_column='Datetime', 
                                                                    y_column='Close', 
                                                                    color_column='id', 
                                                                    line_type_column='line_type', 
                                                                    x_title=None, 
                                                                    y_title=None, 
                                                                    title=None)

    # create secondary axis for the technical indicators
    data_chart_category_secondary_y = data_price_and_ta[data_price_and_ta["chart_category"]!="price"].copy()
    data_chart_category_secondary_y["line_type"] = "dot"
    state.plot_price_and_ta = plt.add_secondary_y(  plot = state.plot_price_and_ta, 
                                                    data = data_chart_category_secondary_y, 
                                                    x_column='Datetime',
                                                    y_column='Close',
                                                    color_column='id', 
                                                    line_type_column='line_type', 
                                                    y_title="Purcentage")              


# Portfolio
# <|{tickers_list}|table|width=100%|on_delete=on_delete_table|>


strategy = Markdown("""

<|layout|columns=1 1 8|

    <|

<|RESET|button|class_name=button_reset|on_action=reset_tables|>

---

Selected Tickers 
<|{ticker}|input|label=Ticker|>

<|Add to portfolio|button|class_name=button|on_action=add_to_porfolio|>

---

Portfolio 
<|{ticker_selected}|selector|type=str|lov={tickers_list}|adapter={lambda u: u}|dropdown=True|>


Since
<|{start_date}|date|label=Start Date|>
To
<|{end_date}|date|label=End Date|>
Interval
<|{interval}|selector|type=str|lov={intervals}|adapter={lambda u: u}|dropdown=True|>

<|GENERATE CHART|button|class_name=button|on_action=pipeline|>


    |>


    <|


Technical Indicator
<|{ta}|selector|type=str|lov={ta_list}|adapter={lambda u: u}|dropdown=True|>

<|{window}|input|label=Window|>
<|{short_window}|input|label=Short Window|>
<|{long_window}|input|label=Long Window|>
<|{span}|input|label=Span|>
<|{smoothing}|input|label=Smoothing|>

<|Add to chart|button|class_name=button|on_action=pipeline_ta|>


<|TI on chart|expandable|expanded=True|class_name=custom-expandable|
<|{ti_list_selected}|selector|type=str|lov={ti_list}|adapter={lambda u: u}|dropdown=False|multiple=True|mode=check|on_change=update_plot|>
|>

    |>

    <|
## Stock Price Chart
<|chart|figure={plot_price_and_ta}|height=900px|width=100%|>
    |>

|>




""")


# ## Pourcentage Chart
# <|chart|figure={plot_purcentage_positive_and_ta}|height=400px|width=100%|>

# ## Pourcentage Positive Chart
# <|chart|figure={plot_purcentage_and_ta}|height=400px|width=100%|>