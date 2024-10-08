import reflex as rx
import pandas as pd
import yfinance as yf
from datetime import date, timedelta

class State(rx.State):
    ticker: str = "AAPL"
    start_date: str = (date.today() - timedelta(days=365)).isoformat()
    end_date: str = date.today().isoformat()
    stock_data: pd.DataFrame = None

    def update_data(self):
        self.stock_data = yf.download(self.ticker, start=self.start_date, end=self.end_date)

    def set_ticker(self, ticker):
        self.ticker = ticker
        self.update_data()

    def set_start_date(self, start_date):
        self.start_date = start_date
        self.update_data()

    def set_end_date(self, end_date):
        self.end_date = end_date
        self.update_data()

    # Add getter methods
    @property
    def get_stock_data(self):
        return self.stock_data

def dashboard():
    state = State()  # Create an instance of State

    return rx.vstack(
        rx.heading("Stock Dashboard"),
        rx.input(
            placeholder="Enter ticker (e.g., AAPL)", 
            on_change=state.set_ticker
        ),
        rx.input(
            type_="date",
            placeholder="Start date",
            on_change=state.set_start_date
        ),
        rx.input(
            type_="date",
            placeholder="End date",
            on_change=state.set_end_date
        ),
        rx.button("Update Data", on_click=state.update_data),
        rx.cond(
            state.get_stock_data is not None and not state.get_stock_data.empty,
            rx.chart(
                data=state.get_stock_data.reset_index().to_dict('records'),
                x="Date",
                y=["Close"],
                title=f"Stock Price for {state.ticker}"
            ),
            rx.text("No data to display")
        )
    )

app = rx.App()
app.add_page(dashboard)
