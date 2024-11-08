from taipy.gui import Gui
from taipy.common.config import Config
import os
import argparse

def create_gui(base_url):
    # Configuration de Taipy
    config = Config()
    config.http.base_pathname = base_url
    config.http.static_directory = os.path.join(os.path.dirname(__file__), "static")
    config.http.static_path = f"{base_url}static"  # Pas besoin de double slash
    
    # Définir les pages avec le bon mapping
    root_md = f"""<|toggle|theme|>
<|menu|label=Menu|lov={{[ 
    ('{base_url}/strategy', 'Technical indicators'), 
    ('{base_url}/options', 'Options')
]}}|on_action=on_menu|>"""

    pages = {
        "/": root_md,
        "strategy": strategy,
        "options": options,
    }

    # Configuration des fichiers statiques
    taipy_css = f"{base_url}/static/stylekit/stylekit.css"
    custom_css = f"{base_url}/static/styles.css"

    gui = Gui(pages=pages, css_files=[taipy_css, custom_css], config=config)
    gui.add_page("root", layout)

    return gui

parser = argparse.ArgumentParser(description="Run the application")
parser.add_argument("-H", "--host", type=str, default="0.0.0.0")
parser.add_argument("-P", "--port", type=int, default=80)
parser.add_argument("-B", "--base_url", type=str, 
                    default="/trading-strategy-analysis/")
parser.add_argument("--no-reloader", action="store_true")

args = parser.parse_args()

if __name__ == "__main__":
    # Créer le dossier static s'il n'existe pas
    os.makedirs("static/stylekit", exist_ok=True)

    # Déplacer les fichiers statiques dans le bon dossier
    if not os.path.exists("static/styles.css"):
        if os.path.exists("styles.css"):
            os.rename("styles.css", "static/styles.css")

    gui = create_gui(args.base_url)
    gui.run(
        debug=True,
        title="Strategies creator",
        host=args.host,
        port=args.port,
        use_reloader=not args.no_reloader
    )

app = create_gui(args.base_url).run