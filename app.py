from taipy.gui import Gui, navigate, State
from pages.home import home
from pages.strategy import strategy
from pages.options import options, option_page, stock_page
from pages.settings import settings
from navigation import layout, on_navigate
import pandas as pd 

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

if __name__ == "__main__":
    #  gui.run(debug=True, dark_mode=True, use_reloader=True, title="Strategies creator")
    gui.run(debug=False, dark_mode=True, use_reloader=True, title="Strategies creator")