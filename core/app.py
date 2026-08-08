import os
import sys
import threading
from flask import Flask

# Windows Embedded Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from database import init_db

# Import blueprints
from routes.api_youtube import bp_youtube
from routes.api_songs import bp_songs
from routes.api_artists import bp_artists
from routes.api_notion import bp_notion
from routes.api_system import bp_system

app = Flask(__name__)
app.config.from_object(Config)

init_db()

app.register_blueprint(bp_youtube)
app.register_blueprint(bp_songs)
app.register_blueprint(bp_artists)
app.register_blueprint(bp_notion)
app.register_blueprint(bp_system)

if __name__ == "__main__":
    if app.config.get("OPEN_BROWSER_ON_START", True):
        import webbrowser
        port = app.config.get("PORT", 5000)
        threading.Timer(1.25, lambda: webbrowser.open(f"http://127.0.0.1:{port}")).start()
    app.run(port=app.config.get("PORT", 5000), debug=True, use_reloader=False)
