from taipy.gui import Gui, navigate, State
from pages.home import home
from pages.strategy import strategy
from pages.options import options, option_page, stock_page
from pages.settings import settings
from navigation import layout, on_navigate
import pandas as pd 

import sys
import argparse

from flask import redirect

# create a navbar : 
# root_md="<|toggle|theme|>\n<|menu|label=Menu|lov={[ ('home', 'Home'), ('strategy', 'Technical indicators'), ('options', 'Options'), ('settings', 'Settings')]}|on_action=on_menu|>"

root_md="<|toggle|theme|>\n<|menu|label=Menu|lov={[ ('strategy', 'Technical indicators'), ('options', 'Options')]}|on_action=on_menu|>"


def on_menu(state, var_name, info):
    page = info['args'][0]
    navigate(state, to=page)

# Create and run the app
#  pages = {
#      "/": root_md,
#      "home": home,
#      "strategy": strategy,
#      "analysis": analysis,
#      "settings": settings
#  }

pages = {
    "/": root_md,
    "strategy": strategy,
    "options": options,
}


gui = Gui(pages=pages, css_file="styles.css")
gui.add_page("root", layout)

# Define a WSGI-compatible application
app = gui.run

if __name__ == "__main__":
    # gui.run(debug=True, dark_mode=True, use_reloader=True, title="Strategies creator")

    parser = argparse.ArgumentParser(description="Run the application")
    parser.add_argument("-H", "--host", type=str, default="0.0.0.0", help="Host to run the application on")
    parser.add_argument("-P", "--port", type=int, default=8080, help="Port to run the application on")
    parser.add_argument("-B", "--base_url", type=str, default="/trading-strategy-analysis", help="Base URL for the application")
    parser.add_argument("--no-reloader", action="store_true", help="Disable the reloader")
    args = parser.parse_args()

    gui.run(debug=True, title="Strategies creator", host=args.host, port=args.port, use_reloader=not args.no_reloader)


# run the app in a production server by using : 

# poetry run python app.py -H "0.0.0.0" -P "5000" -no-reloader
# http://0.0.0.0:5000/ => then works on the browser