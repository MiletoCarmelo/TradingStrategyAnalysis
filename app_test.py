from taipy.gui import notify, Gui
import yfinance as yf
import pandas as pd

# Initial data
ticker = "AAPL"
start_date = "2023-01-01"
end_date = "2023-12-31"
stock_data = pd.DataFrame(columns=["Date", "Close"])

states = {
    "ticker": ticker, 
    "start_date": start_date,
    "end_date": end_date, 
    "stock_data": stock_data
}

def fetch_stock_data(ticker, start_date, end_date):
    stock = yf.Ticker(ticker)
    data = stock.history(start=start_date, end=end_date)
    return data[['Close']].reset_index()

def update_data(state):
    try:
        # state.stock_data = fetch_stock_data(state.ticker, state.start_date, state.end_date)
        stock_data = fetch_stock_data(ticker, start_date, end_date)
        notify(state, "success", f"Data updated for {ticker}")
        # update the state of stock_data 
        state.stock_data = stock_data
    except Exception as e:
        notify(state, "error", f"Failed to fetch data: {str(e)}")

dashboard = """
# Options Dashboard

<|{ticker}|input|label=Stock Ticker|>
<|{start_date}|date|label=Start Date|>
<|{end_date}|date|label=End Date|>
<|Update|button|on_action=update_data|>

## Stock Price Chart
<|{stock_data}|chart|x=Date|y=Close|height=500px|width=100%|>
"""

# Create a GUI instance with the defined state
gui = Gui(dashboard)
gui.run(state=states)
